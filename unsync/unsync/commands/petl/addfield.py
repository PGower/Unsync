"""PETL Addfield Command."""
import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, help='Name of the source data table.')
@click.option('--field', '-f', required=True, help='Name of the new field.')
@click.option('--value', '-v', required=True, help='Either a static value or a string that can be evaluated by petl.expr')
@pass_data
def petl_addfield(data, source, field, value):
    """Return the first n rows of the data table and store them in the destination data table."""
    s = data.get(source)
    s = s.addfield(field, petl.expr(value))
    data.set(source, s)

command = petl_addfield
