'''Create and store an MSSQL (PyTDS) connection '''
from __future__ import unicode_literals

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync

import click
import pytds
import petl


def validate_port(ctx, param, value):
    if value is None:
        return value
    elif 0 <= value and value <= 65535:
        return value
    else:
        raise click.BadParameter('port must be >=0 and <=65535')


# These need more work.
# auth=None,
# load_balancer=None
# tds_version=tds_base.TDS74,,
# encryption_level=tds_base.TDS_ENCRYPTION_OFF
# row_strategy=None

@unsync.command()
@click.option('--connection-name', type=str, help='The name used to store this connection in the value registry.')
@click.option('--dsn', type=str, help='SQL server host and instance: <host>[<instance>]')
@click.option('--failover-partner', default=None, type=str, help='Secondary database host, used if primary is not accessible')
@click.option('--database', default=None, type=str, help='The database to initially connect to')
@click.option('--user', default=None, type=str, help='Database user to connect as')
@click.option('--password', default=None, type=str, help='User’s password')
@click.option('--timeout', default=None, type=int, help='query timeout in seconds, default 0 (no timeout)')
@click.option('--login-timeout', default=15, type=int, help='timeout for connection and login in seconds, default 15')
# @click.option('--as-dict', default=False, type=bool, help='whether rows should be returned as dictionaries instead of tuples.')  # Pretty sure this will break petl if its turned on.
@click.option('--appname', default='UNSYNC', type=str, help='Set the application name to use for the connection')
# @click.option('--port', default=None, type=int, callback=validate_port, help='the TCP port to use to connect to the server')
@click.option('--autocommit/--no-autocommit', default=False, help='Enable or disable database level autocommit')
@click.option('--blocksize', default=4096, type=int, help=' Size of block for the TDS protocol, usually should not be used')
@click.option('--use-mars/--no-use-mars', default=False, help='Enable or disable MARS')
@click.option('--readonly/-no-readonly', default=False, help='Allows to enable read-only mode for connection, only supported by MSSQL 2012, earlier versions will ignore this parameter')
@click.option('--bytes-to-unicode/--no-bytes-to-unicode', default=True, help='If true single byte database strings will be converted to unicode Python strings, otherwise will return strings as bytes without conversion.')
# @click.option('--auth-type', default=None, type=click.Choice(['NTLM', 'SSPI']), help='Alternative authentication method.')
@click.option('--tz-offset', default=None, type=int, help='Fixed offset in minutes east from UTC.')
@pass_data
def connection(data, connection_name, dsn, failover_partner, database, user, password, timeout, login_timeout, appname, autocommit, blocksize, use_mars, readonly, bytes_to_unicode, tz_offset):
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
