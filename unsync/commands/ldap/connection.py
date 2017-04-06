'''Create an LDAP connection and store it in a context variable.'''
from __future__ import absolute_import
import click
import ldap3

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--connection-name', required=True, help='Name used to store this connection in teh value registry.')
@click.option('--server', '-s', required=True, help='LDAP Server Address.')
@click.option('--port', '-p', default=389, help='LDAP Server Port (389 or 636 for SSL).')
@click.option('--use-ssl/--no-use-ssl', default=False, help='Should we use SSL for the connection.')
@click.option('--user', default=None, help='User to bind as. If blank will attempt an anonymous bind.')
@click.option('--password', default=None, help='Password to use for binding.')
@pass_data
def ldap_connection(data, connection_name, server, port, use_ssl, user, password):
    """Create an LDAP3 connection and store it in the value registry under the given name."""
    server = ldap3.Server(server, port=port, use_ssl=use_ssl)
    conn = ldap3.Connection(server=server, user=user, password=password)
    data.values[connection_name] = conn

command = ldap_connection
