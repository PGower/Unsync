"""LDAP3 Commands for the Unsync Tool."""
from __future__ import absolute_import
import click
import ldap3

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync

# Until I can get fromldap in the main PETL package I need to be a bit defensive.
try:
    from petl import fromldap
except ImportError:
    from .ldap_view import fromldap  # noqa


@unsync.command()
@click.option('--connection-name', required=True, help='Name used to store this connection in teh value registry.')
@click.option('--server', '-s', required=True, help='LDAP Server Address.')
@click.option('--port', '-p', default=389, help='LDAP Server Port (389 or 636 for SSL).')
@click.option('--use-ssl/--no-use-ssl', default=False, help='Should we use SSL for the connection.')
@click.option('--user', default=None, help='User to bind as. If blank will attempt an anonymous bind.')
@click.option('--password', default=None, help='Password to use for binding.')
@pass_data
def connect(data, connection_name, server, port, use_ssl, user, password):
    """Create an LDAP connection object and store it in the valstore with the given connection-name."""
    server = ldap3.Server(server, port=port, use_ssl=use_ssl)
    conn = ldap3.Connection(server=server, user=user, password=password)
    data.values[connection_name] = conn


@unsync.command()
@click.option('--connection-name', required=True, help='Name of the connection to use.')
@click.option('--base-ou', required=True, help='Base OU for searches.')
@click.option('--query', '-q', required=True, help='LDAP search filters as per RFC2254.')
@click.option('--attributes', '-a', multiple=True, required=True, help='Attributes to return from matching objects.')
@click.option('--destination', '-d', required=True, help='Kind of data contained in the LDAP query.')
@pass_data
def ldap_import(data, connection_name, base_ou, query, attributes, destination):
    """Import the results of an LDAP query into a data table."""
    conn = data.values[connection_name]
    query_results = fromldap(conn, base_ou, query, attributes=attributes)
    data.set(destination, query_results)

ldap_import.display_name = 'import'
