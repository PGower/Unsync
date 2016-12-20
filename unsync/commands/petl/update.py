"""PETL Update Command."""
import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, type=unicode, help='Name of the source data table/s.')
@click.option('--destination', '-d', type=unicode, help='Name of the destination data table.')
@click.option('--field', '-f', required=True, help='The field name to modify')
@click.option('--value', '-v', required=True, help='the value to fill the field with.')
@pass_data
def petl_update(data, source, destination, field, value):
    """Update a given column with a static value."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.update(field, value)
    data.set(destination, s)


command = petl_update
