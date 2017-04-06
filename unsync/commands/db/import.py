'''Generic Python DB API v2.0 Query'''
from __future__ import unicode_literals

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync

import click
import petl


@unsync.command()
@click.option('--connection-name', type=str, help='The name of the connection to use for this query. This needs to be a DB-APIv2.0 compiant connection.')
@click.option('--query', type=str, help='SQL query to make against the connection.')
@click.option('--destination', '-d', type=str, help='Destination table to store the data in.')
@pass_data
def db_import(data, connection_name, query, destination):
    connection = data.values[connection_name]
    query_data = petl.fromdb(connection, query)
    data.set(destination, query_data)

command = db_import
