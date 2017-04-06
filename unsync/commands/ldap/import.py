from __future__ import absolute_import
import click

# Until I can get fromldap in the main PETL package I need to be a bit defensive.
try:
    from petl import fromldap
except ImportError:
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ldap_view import fromldap  # noqa

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--connection-name', required=True, help='Name of the connection to use.')
@click.option('--base-ou', required=True, help='Base OU for searches.')
@click.option('--query', '-q', required=True, help='LDAP search filters as per RFC2254.')
@click.option('--attributes', '-a', multiple=True, required=True, help='Attributes to return from matching objects.')
@click.option('--destination', '-d', required=True, help='Kind of data contained in the LDAP query.')
@pass_data
def ldap_import(data, connection_name, base_ou, query, attributes, destination):
    """Import data from an LDAP server."""
    conn = data.values(connection_name)
    query_results = fromldap(conn, base_ou, query, attributes=attributes)
    data.set(destination, query_results)


command = ldap_import
