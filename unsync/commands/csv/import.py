"""CSV Import and Export functions for CanvasUnsync."""
from __future__ import unicode_literals

import click
import petl

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='CSV file that data will be read from.')
@click.option('--csv-arg', multiple=True, type=click.Tuple([str, str]), help='Arguments that will be passed to petl\'s CSV parsing engine.')
@click.option('--errors', default='strict', help='PETL option for CSV errors.')
@click.option('--destination', '-d', required=True, help='The destination table that imported CSV data will be stored in.')
@pass_data
def csv_import(data, input_file, csv_arg, errors, destination):
    """Import data from a CSV file into the destination table."""
    new_data = petl.fromcsv(input_file, errors=errors, **dict(csv_arg))
    data.cat(destination, new_data)

command = csv_import
