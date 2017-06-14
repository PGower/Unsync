"""PETL Rename Command."""
from __future__ import unicode_literals

import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, type=str, help='Name of the source data table/s.')
@click.option('--destination', '-d', type=str, help='Name of the destination data table.')
@click.option('--transform', '-t', multiple=True, type=click.Tuple([str, str]), help='Header transforms, FROM, TO.')
@pass_data
def rename(data, source, destination, transform):
    """Rename columns based on Transform parameters."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.rename(dict(transform))
    data.set(destination, s)
