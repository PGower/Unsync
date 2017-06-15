"""PETL Update Command."""
from __future__ import unicode_literals

import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, type=str, help='Name of the source data table/s.')
@click.option('--destination', '-d', type=str, help='Name of the destination data table.')
@click.option('--field', '-f', required=True, help='The field name to modify')
@click.option('--value', '-v', required=True, help='the value to fill the field with.')
@pass_data
def update(data, source, destination, field, value):
    """Update a given column with a static value."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.update(field, value)
    data.set(destination, s)