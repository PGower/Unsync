"""LDAP3 Commands for the Unsync Tool."""
from __future__ import absolute_import
import ldap3
import unsync

# Until I can get fromldap in the main PETL package I need to be a bit defensive.
try:
    from petl import fromldap
except ImportError:
    from .ldap_view import fromldap  # noqa


@unsync.command()
@unsync.option('--connection-name', required=True, help='Name used to store this connection in teh value registry.')
@unsync.option('--server', '-s', required=True, help='LDAP Server Address.')
@unsync.option('--port', '-p', default=389, help='LDAP Server Port (389 or 636 for SSL).')
@unsync.option('--use-ssl/--no-use-ssl', default=False, help='Should we use SSL for the connection.')
@unsync.option('--user', default=None, help='User to bind as. If blank will attempt an anonymous bind.')
@unsync.option('--password', default=None, help='Password to use for binding.')
def connect(data, connection_name, server, port, use_ssl, user, password):
    """Create an LDAP connection object and store it in the valstore with the given connection-name."""
    server = ldap3.Server(server, port=port, use_ssl=use_ssl)
    conn = ldap3.Connection(server=server, user=user, password=password)
    data.values[connection_name] = conn


@unsync.command()
@unsync.option('--connection-name', required=True, help='Name of the connection to use.')
@unsync.option('--base-ou', required=True, help='Base OU for searches.')
@unsync.option('--query', '-q', required=True, help='LDAP search filters as per RFC2254.')
@unsync.option('--attributes', '-a', multiple=True, required=True, help='Attributes to return from matching objects.')
@unsync.option('--destination', '-d', required=True, help='Kind of data contained in the LDAP query.')
def ldap_import(data, connection_name, base_ou, query, attributes, destination):
    """Import the results of an LDAP query into a data table."""
    conn = data.values[connection_name]
    query_results = fromldap(conn, base_ou, query, attributes=attributes)
    data.set(destination, query_results)

ldap_import.display_name = 'import'


# TODO: Add commands to CREATE / UPDATE and DELETE.