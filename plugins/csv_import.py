"""CSV Import and Export functions for CanvasUnsync."""
from __future__ import absolute_import
import click
import petl
import os

from .common import pass_data, generic_import_actions


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='CSV file that data will be read from.')
@click.option('--attr-map', '-m', multiple=True, type=click.Tuple([unicode, unicode]), help='Determines how fields from the ptf9 data will be mapped to Canvas course fields.')
@click.option('--attr-fill', '-f', multiple=True, type=click.Tuple([unicode, unicode]), help='Fill attributes with values from the provided pairs. First name is the attribute name second is the value.')
@click.option('--delete-import-fields/--no-delete-import-fields', default=False, help='When set any fields that were imported and not explicitly named in the attr_map or attr_fill will be removed.')
@click.option('--csv-arg', multiple=True, type=click.Tuple([unicode, unicode]), help='Arguments that will be passed to petl\'s CSV parsing engine.')
@click.option('--errors', default='strict', help='PETL option for CSV errors.')
@click.option('--destination', '-d', required=True, help='The destination table that imported CSV data will be stored in.')
@pass_data
def csv_import(data, input_file, attr_map, attr_fill, delete_import_fields, csv_arg, errors, destination):
    """Import data from a CSV file into the destination table."""
    new_data = petl.fromcsv(input_file, errors=errors, **dict(csv_arg))
    new_data = generic_import_actions(new_data, attr_map, attr_fill, delete_import_fields)
    data.cat(destination, new_data)

command = csv_import
