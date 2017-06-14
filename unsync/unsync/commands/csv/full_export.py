"""CSV Import and Export functions for CanvasUnsync."""
from __future__ import unicode_literals

import click
import petl
import os

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--output-dir', '-o', type=click.Path(dir_okay=True, file_okay=False, readable=True, resolve_path=True), help='CSV file that data will be read from.')
@click.option('--csv-arg', multiple=True, type=click.Tuple([str, str]), help='Arguments that will be passed to petl\'s CSV parsing engine.')
@click.option('--errors', default='strict', help='PETL option for CSV errors.')
@click.option('--write-header/--no-write-header', default=True, help='When set the CSV file will have a header row.')
@click.option('--exclude-empty/--include-empty', default=True, help='When set data tables with no data in them will not create CSV files.')
@pass_data
def csv_full_export(data, output_dir, csv_arg, errors, write_header, exclude_empty):
    """Export all data tables as CSV files."""
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for name in data.registry:
        current_data = data.get(name)
        if exclude_empty and current_data.nrows() <= 0:
            continue
        output_file = os.path.join(output_dir, data.filename(name, 'csv'))
        petl.tocsv(current_data, output_file, errors=errors, write_header=write_header, **dict(csv_arg))

command = csv_full_export
