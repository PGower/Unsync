import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, help='Source table to print data from.')
@pass_data
def stats(data, source):
    """Print a text representation of the data table for a given KIND."""
    d = data.get(source)
    click.secho('Row Count: {}'.format(d.nrows()), fg='green')
    click.secho('Column Count: {}'.format(len(d[0])), fg='green')

command = stats
