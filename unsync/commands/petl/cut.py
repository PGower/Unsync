"""PETL Cut Command."""
import click
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, help='Name of the source data table.')
@click.option('--destination', '-d', help='Name of the destination data table. Will default to the source table if not specified.')
@click.option('--field', multiple=True, type=unicode, help='Field names to cut from the source table.')
@click.option('--index', multiple=True, type=int, help='Field indexes to cut from the source table.')
@pass_data
def petl_cut(data, source, destination, field, index):
    """Return only columns that are specified in field on index options."""
    if not destination:
        destination = source
    s = data.get(source)
    a = field + index
    s = s.cut(*a)
    data.set(destination, s)

command = petl_cut
