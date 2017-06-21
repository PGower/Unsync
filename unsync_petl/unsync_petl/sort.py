"""PETL Sort Command."""
from __future__ import unicode_literals

import click
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, type=str, help='Name of the source data table/s.')
@click.option('--destination', '-d', type=str, help='Name of the destination data table.')
@click.option('--key', '-k', multiple=True, help='The field names to sort by. Can be None, a single field or multiple fields.')
@click.option('--reverse/--no-reverse', default=False, help='Perform a reverse sort.')
@pass_data
def sort(data, source, destination, key, reverse):
    """Return rows that match the given selector."""
    if not destination:
        destination = source
    s = data.get(source)
    if key == ():  # An empty key is okay but must be None
        key = None
    s = s.sort(key=key, reverse=reverse)
    data.set(destination, s)
