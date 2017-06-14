import click
import petl

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, multiple=True, help='Name of the source data table.')
@pass_data
def move_tables_to_memory(data, source):
    """Create a petl.MemorySource and copy data from the given tables into it. Can greatly decrease processing time for some operations."""
    for s in source:
        source_table = data.get(s)
        a = petl.MemorySource()
        source_table.tocsv(a)

        b = petl.MemorySource(a.getvalue())
        destination_table = petl.fromcsv(source=b)
        data.set(s, destination_table)

command = move_tables_to_memory
