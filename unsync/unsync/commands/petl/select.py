"""PETL Select Command."""
from __future__ import unicode_literals

import click
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, type=str, help='Name of the source data table/s.')
@click.option('--destination', '-d', type=str, help='Name of the destination data table.')
@click.option('--selector', required=True, type=str, help='A string expression to be applied against the row. See http://petl.readthedocs.io/en/latest/transform.html#petl.transform.selects.select')
@pass_data
def petl_select(data, source, destination, selector):
    """Return rows that match the given selector."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.select(selector)
    data.set(destination, s)

command = petl_select
