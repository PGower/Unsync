"""PETL Head Command."""
import click
import petl
from lib.common import pass_data


@click.command()
@click.option('--source', '-s', multiple=True, required=True, help='Name of the source data table/s.')
@click.option('--destination', '-d', required=True, help='Name of the destination data table.')
@click.option('--header', '-h', multiple=True, type=unicode, help='Use the provided list in place of the existing table headers.')
@click.option('--missing', default=None, help='The value to store in columns that have no value set.')
@pass_data
def petl_head(data, source, destination, header, missing):
    """Return the first n rows of the data table and store them in the destination data table."""
    sources = [data.get(s) for s in source]
    if len(header) == 0:
        n = petl.cat(*sources, missing=missing)
    else:
        n = petl.cat(*sources, header=header, missing=missing)
    data.set(destination, n)

command = petl_head
