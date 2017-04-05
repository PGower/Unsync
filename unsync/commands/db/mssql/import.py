'''MSSQL specific command to import data from an SQL query.'''
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
@click.option('--dsn', type=str, help='SQL server host and instance: <host>[<instance>]')
@click.option('--failover-partner', default=None, type=str, help='Secondary database host, used if primary is not accessible')
@click.option('--database', default=None, type=str, help='The database to initially connect to')
@click.option('--user', default=None, type=str, help='Database user to connect as')
@click.option('--password', default=None, type=str, help='User’s password')
@click.option('--timeout', default=None, type=int, help='query timeout in seconds, default 0 (no timeout)')
@click.option('--login-timeout', default=15, type=int, help='timeout for connection and login in seconds, default 15')
# @click.option('--as-dict', default=False, type=bool, help='whether rows should be returned as dictionaries instead of tuples.')  # Pretty sure this will break petl if its turned on.
@click.option('--appname', default='UNSYNC', type=str, help='Set the application name to use for the connection')
@click.option('--server', default=None, type=str, help='')
@click.option('--port', default=None, type=int, callback=validate_port, help='the TCP port to use to connect to the server')
@click.option('--autocommit/--no-autocommit', default=False, help='Enable or disable database level autocommit')
@click.option('--blocksize', default=4096, type=int, help=' Size of block for the TDS protocol, usually should not be used')
@click.option('--use-mars/--no-use-mars', default=False, help='Enable or disable MARS')
@click.option('--readonly/-no-readonly', default=False, help='Allows to enable read-only mode for connection, only supported by MSSQL 2012, earlier versions will ignore this parameter')
@click.option('--bytes-to-unicode/--no-bytes-to-unicode', default=True, help='If true single byte database strings will be converted to unicode Python strings, otherwise will return strings as bytes without conversion.')
# @click.option('--auth-type', default=None, type=click.Choice(['NTLM', 'SSPI']), help='Alternative authentication method.')
@click.option('--tz-offset', default=None, type=int, help='Fixed offset in minutes east from UTC.')
@click.option('--query', type=str, help='SQL query to make against the connection.')
@click.option('--destination', type=str, help='Destination table to store the data in.')

@pass_data
def mssql_import(data, dsn, failover_partner, database, user, password, timeout, login_timeout, appname, port, autocommit, blocksize, use_mars, readonly, bytes_to_unicode, tz_offset, query, destination):
    connection = pytds.connect(dsn=dsn,
                               database=database,
                               user=user,
                               password=password,
                               timeout=timeout,
                               login_timeout=login_timeout,
                               appname=appname,
                               port=port,
                               autocommit=autocommit,
                               blocksize=blocksize,
                               use_mars=use_mars,
                               readonly=readonly,
                               bytes_to_unicode=bytes_to_unicode,
                               failover_partner=failover_partner)
    query_data = petl.fromdb(connection, query)
    data.set(destination, query_data)

command = mssql_import