'''Generic Python DB API v2.0 Commands for the Unsync Tool.'''
import unsync
import petl


@unsync.command()
@unsync.option('--connection-name', type=str, help='The name of the connection to use for this query. This needs to be a DB-APIv2.0 compiant connection.')
@unsync.option('--table', type=str, help='The name of the table to store data in. Assumes table exists and that it has the correct schema.')
@unsync.option('--source', '-s', type=str, help='Destination table to store the data in.')
@unsync.option('--commit/--no-commit', default=True, help='Commit the database transaction after the operation.')
def db_export(data, connection_name, table, source, commit):
    """Generic export command for a db connection conforming to the DB API V2.0 Spec."""
    source_table = data.get(source)
    connection = data.values[connection_name]
    petl.todb(source_table, connection, table, commit=commit)

db_export.display_name = 'export'


@unsync.command()
@unsync.option('--connection-name', type=str, help='The name of the connection to use for this query. This needs to be a DB-APIv2.0 compiant connection.')
@unsync.option('--query', type=str, help='SQL query to make against the connection.')
@unsync.option('--destination', '-d', type=str, help='Destination table to store the data in.')
def db_import(data, connection_name, query, destination):
    """Generic import command for a db connection conforming to the DB API V2.0 Spec."""
    connection = data.values[connection_name]
    query_data = petl.fromdb(connection, query)
    data.set(destination, query_data)

db_import.display_name = 'import'

# TODO: callproc
