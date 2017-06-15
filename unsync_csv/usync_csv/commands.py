"""CSV commands for the Unsync Tool."""
from __future__ import unicode_literals

import click
import petl
import os

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--output-file', '-o', type=click.Path(dir_okay=False, readable=True, resolve_path=True), help='CSV file that data will be read from.')
@click.option('--source', '-s', required=True, help='Source table to export as CSV.')
@click.option('--csv-arg', multiple=True, type=click.Tuple([str, str]), help='Arguments that will be passed to petl\'s CSV parsing engine.')
@click.option('--errors', default='strict', help='PETL option for CSV errors.')
@click.option('--write-header/--no-write-header', default=True, help='When set the CSV file will have a header row.')
@click.option('--append/--no-append', default=False, help='When set the output file will be opened and rows will be appended to the existing data. When set --write-header is always False.')
@pass_data
def export(data, output_file, source, csv_arg, errors, write_header, append):
    """Export the specified table of data to a csv file."""
    existing_data = data.get(source)
    if append is True:
        petl.appendcsv(existing_data, output_file, errors=errors, **dict(csv_arg))
    else:
        petl.tocsv(existing_data, output_file, errors=errors, write_header=write_header, **dict(csv_arg))


@unsync.command()
@click.option('--output-dir', '-o', type=click.Path(dir_okay=True, file_okay=False, readable=True, resolve_path=True), help='CSV file that data will be read from.')
@click.option('--csv-arg', multiple=True, type=click.Tuple([str, str]), help='Arguments that will be passed to petl\'s CSV parsing engine.')
@click.option('--errors', default='strict', help='PETL option for CSV errors.')
@click.option('--write-header/--no-write-header', default=True, help='When set the CSV file will have a header row.')
@click.option('--exclude-empty/--include-empty', default=True, help='When set data tables with no data in them will not create CSV files.')
@pass_data
def full_export(data, output_dir, csv_arg, errors, write_header, exclude_empty):
    """Export all data tables as CSV files."""
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for name in data.registry:
        current_data = data.get(name)
        if exclude_empty and current_data.nrows() <= 0:
            continue
        output_file = os.path.join(output_dir, data.filename(name, 'csv'))
        petl.tocsv(current_data, output_file, errors=errors, write_header=write_header, **dict(csv_arg))


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

csv_import.display_name = 'import'

