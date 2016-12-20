"""PETL Rename Command."""
import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, type=unicode, help='Name of the source data table/s.')
@click.option('--destination', '-d', type=unicode, help='Name of the destination data table.')
@click.option('--transform', '-t', multiple=True, type=click.Tuple([unicode, unicode]), help='Header transforms, FROM, TO.')
@pass_data
def petl_rename(data, source, destination, transform):
    """Rename columns based on Transform parameters."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.rename(dict(transform))
    data.set(destination, s)

command = petl_rename
