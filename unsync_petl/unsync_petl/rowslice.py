"""PETL Head Command."""
import click
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, help='Name of the source data table.')
@click.option('--destination', '-d', help='Name of the destination data table. Will default to the source table if not specified.')
@click.option('--start', default=None, type=int, help='Row number to start the slice from.')
@click.option('--stop', required=True, type=int, help='Row number to stop the slice at.')
@click.option('--step', default=None, type=int, help='Slice step.')
@pass_data
def rowslice(data, source, destination, start, stop, step):
    """Return the first n rows of the data table and store them in the destination data table."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.rowslice(start, stop, step)
    data.set(destination, s)
