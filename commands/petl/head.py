"""PETL Head Command."""
import click
from lib.unsync_data import pass_data
from lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, help='Name of the source data table.')
@click.option('--destination', '-d', help='Name of the destination data table. Will default to the source table if not specified.')
@click.option('-n', type=int, required=True, help='Number of rows to select.')
@pass_data
def petl_head(data, source, destination, n):
    """Return the first n rows of the data table and store them in the destination data table."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.head(n)
    data.set(destination, s)

command = petl_head