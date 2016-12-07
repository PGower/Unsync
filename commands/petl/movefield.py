"""PETL Head Command."""
import click
from lib.common import pass_data


@click.command()
@click.option('--source', '-s', required=True, help='Name of the source data table.')
@click.option('--destination', '-d', help='Name of the destination data table. Will default to the source table if not specified.')
@click.option('--field', required=True, type=unicode, help='Name of the field to move.')
@click.option('--index', required=True, type=int, help='New index of the field.')
@pass_data
def petl_movefield(data, source, destination, field, index):
    """Return the first n rows of the data table and store them in the destination data table."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.movefield(field, index)
    data.set(destination, s)

command = petl_movefield
