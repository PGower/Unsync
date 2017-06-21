"""Utility command to filter table rows based on the value of a column and a provided regex."""
from __future__ import unicode_literals

import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, help='The source data table.')
@click.option('--filter', '-f', type=click.Tuple([str, str]), multiple=True, required=True, help='A tuple of values, first is the column to filter on and second is the regex to use.')
@click.option('--destination', '-d', help='The destination data table for matched rows. If blank will overwrite the source table.')
@pass_data
def searchcomplement(data, source, filter, destination):
    """Exclude rows where the specified column matches the given regex."""
    if not destination:
        destination = source
    s = data.get(source)
    for column, pattern in filter:
        s = s.searchcomplement(column, pattern)
    data.set(destination, s)
