"""Create and store an MSSQL (PyTDS) connection."""
import unsync
import pytds


def validate_port(ctx, param, value):
    if value is None:
        return value
    elif 0 <= value and value <= 65535:
        return value
    else:
        raise unsync.BadParameter('port must be >=0 and <=65535')


# These need more work.
# auth=None,
# load_balancer=None
# tds_version=tds_base.TDS74,,
# encryption_level=tds_base.TDS_ENCRYPTION_OFF
# row_strategy=None

@unsync.command()
@unsync.option('--connection-name', type=str, help='The name used to store this connection in the value registry.')
@unsync.option('--dsn', type=str, help='SQL server host and instance: <host>[<instance>]')
@unsync.option('--failover-partner', default=None, type=str, help='Secondary database host, used if primary is not accessible')
@unsync.option('--database', default=None, type=str, help='The database to initially connect to')
@unsync.option('--user', default=None, type=str, help='Database user to connect as')
@unsync.option('--password', default=None, type=str, help='User’s password')
@unsync.option('--timeout', default=None, type=int, help='query timeout in seconds, default 0 (no timeout)')
@unsync.option('--login-timeout', default=15, type=int, help='timeout for connection and login in seconds, default 15')
# @unsync.option('--as-dict', default=False, type=bool, help='whether rows should be returned as dictionaries instead of tuples.')  # Pretty sure this will break petl if its turned on.
@unsync.option('--appname', default='UNSYNC', type=str, help='Set the application name to use for the connection')
# @unsync.option('--port', default=None, type=int, callback=validate_port, help='the TCP port to use to connect to the server')
@unsync.option('--autocommit/--no-autocommit', default=False, help='Enable or disable database level autocommit')
@unsync.option('--blocksize', default=4096, type=int, help=' Size of block for the TDS protocol, usually should not be used')
@unsync.option('--use-mars/--no-use-mars', default=False, help='Enable or disable MARS')
@unsync.option('--readonly/-no-readonly', default=False, help='Allows to enable read-only mode for connection, only supported by MSSQL 2012, earlier versions will ignore this parameter')
@unsync.option('--bytes-to-unicode/--no-bytes-to-unicode', default=True, help='If true single byte database strings will be converted to unicode Python strings, otherwise will return strings as bytes without conversion.')
# @unsync.option('--auth-type', default=None, type=unsync.Choice(['NTLM', 'SSPI']), help='Alternative authentication method.')
@unsync.option('--tz-offset', default=None, type=int, help='Fixed offset in minutes east from UTC.')
def connection(data, connection_name, dsn, failover_partner, database, user, password, timeout, login_timeout, appname, autocommit, blocksize, use_mars, readonly, bytes_to_unicode, tz_offset):
    """Generate and store a PyTDS connection object in the valstore. Can be used with the generic dbapi commands to retrieve data."""
    connection = pytds.connect(dsn=dsn,
                               database=database,
                               user=user,
                               password=password,
                               timeout=timeout,
                               login_timeout=login_timeout,
                               appname=appname,
                               autocommit=autocommit,
                               blocksize=blocksize,
                               use_mars=use_mars,
                               readonly=readonly,
                               bytes_to_unicode=bytes_to_unicode,
                               failover_partner=failover_partner)
    data.values[connection_name] = connection
