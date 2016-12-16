import click
import petl
import ldap3

from lib.unsync_data import pass_data
from lib.unsync_commands import unsync


@unsync.command()
@click.option('--server', '-s', required=True, help='LDAP Server Address.')
@click.option('--port', '-p', default=389, help='LDAP Server Port (389 or 636 for SSL).')
@click.option('--use-ssl/--no-use-ssl', default=False, help='Should we use SSL for the connection.')
@click.option('--user', default=None, help='User to bind as. If blank will attempt an anonymous bind.')
@click.option('--password', default=None, help='Password to use for binding.')
@click.option('--base-ou', required=True, help='Base OU for searches.')
@click.option('--query', '-q', required=True, help='LDAP search filters as per RFC2254.')
@click.option('--attributes', '-a', multiple=True, required=True, help='Attributes to return from matching objects.')
@click.option('--destination', '-d', required=True, help='Kind of data contained in the LDAP query.')
@pass_data
def ldap_import(data, server, port, use_ssl, user, password, base_ou, query, attributes, destination):
    """Import data from an LDAP server."""
    server = ldap3.Server(server, port=port, use_ssl=use_ssl)
    conn = ldap3.Connection(server=server, user=user, password=password)
    query_results = petl.fromldap(conn, base_ou, query, attributes=attributes)
    data.cat(destination, query_results)


command = ldap_import
