"""PETL Cutout Command."""
import click
from lib.common import pass_data


@click.command()
@click.option('--source', '-s', required=True, help='Name of the source data table.')
@click.option('--destination', '-d', help='Name of the destination data table. Will default to the source table if not specified.')
@click.option('--field', multiple=True, type=unicode, help='Field names to cut from the source table.')
@click.option('--index', multiple=True, type=int, help='Field indexes to cut from the source table.')
@pass_data
def petl_cutout(data, source, destination, field, index):
    """Return only columns that are not specified in field on index options."""
    if not destination:
        destination = source
    s = data.get(source)
    a = field + index
    s = s.cutout(*a)
    data.set(destination, s)

command = petl_cutout
