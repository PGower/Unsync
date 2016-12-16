import click
import petl

from lib.unsync_data import pass_data
from lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, help='Name of the source data table.')
@click.option('--destination', '-d', help='Name of the destination data table. Will default to the source table if not specified.')
@pass_data
def move_table_to_memory(data, source, destination):
    source_table = data.get(source)
    a = petl.MemorySource()
    source_table.tocsv(a)

    b = petl.MemorySource(a.getvalue())
    destination_table = petl.fromcsv(source=b)
    data.set(destination, destination_table)

command = move_table_to_memory
