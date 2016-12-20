"""CSV Import and Export functions for CanvasUnsync."""
import click
import petl

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--output-file', '-o', type=click.Path(dir_okay=False, readable=True, resolve_path=True), help='CSV file that data will be read from.')
@click.option('--source', '-s', required=True, help='Source table to export as CSV.')
@click.option('--csv-arg', multiple=True, type=click.Tuple([unicode, unicode]), help='Arguments that will be passed to petl\'s CSV parsing engine.')
@click.option('--errors', default='strict', help='PETL option for CSV errors.')
@click.option('--write-header/--no-write-header', default=True, help='When set the CSV file will have a header row.')
@click.option('--append/--no-append', default=False, help='When set the output file will be opened and rows will be appended to the existing data. When set --write-header is always False.')
@pass_data
def csv_export(data, output_file, source, csv_arg, errors, write_header, append):
    """Export the specified table of data to a csv file."""
    existing_data = data.get(source)
    if append is True:
        petl.appendcsv(existing_data, output_file, errors=errors, **dict(csv_arg))
    else:
        petl.tocsv(existing_data, output_file, errors=errors, write_header=write_header, **dict(csv_arg))

command = csv_export
