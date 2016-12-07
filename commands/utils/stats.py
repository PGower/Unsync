import click
import petl
from lib.common import pass_data


@click.command()
@click.option('--source', '-s', required=True, help='Source table to print data from.')
@pass_data
def stats(data, source):
    """Print a text representation of the data table for a given KIND."""
    d = data.get(source)
    click.secho('Row Count: {}'.format(d.nrows()), fg='green')
    click.secho('Column Count: {}'.format(len(d[0])), fg='green')


command = stats