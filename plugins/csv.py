from __future__ import absolute_import
import click
import petl
import os

from .common import KINDS, KIND_NAMES, pass_data, generic_import_actions


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='CSV file that data will be read from.')
@click.option('--kind', '-k', type=click.Choice(KIND_NAMES), required=True, help='Kind of data contained in the CSV.')
# @click.option('--status', default='active', type=click.Choice(KINDS['courses']['enums']['status']), help='All courses imported will have this status.')
@click.option('--attr-map', '-m', multiple=True, type=click.Tuple([unicode, unicode]), default=[('Code', 'course_id'), ('Name', 'long_name'), ('Code', 'short_name'), ('ClassID', 'ptf9_id')], help='Determines how fields from the ptf9 data will be mapped to Canvas course fields.')
@click.option('--attr-fill', '-f', multiple=True, type=click.Tuple([unicode, unicode]), help='Fill attributes with values from the provided pairs. First name is the attribute name second is the value.')
@click.option('--delete-import-fields/--no-delete-import-fields', default=False, help='When set any fields that were imported and not explicitly named in the attr_map or attr_fill will be removed.')
@click.option('--csv-arg', multiple=True, type=click.Tuple([unicode, unicode]), help='Arguments that will be passed to petl\'s CSV parsing engine.')
@click.option('--errors', default='strict', help='PETL option for CSV errors.')
@pass_data
def csv_import(data, input_file, kind, attr_map, attr_fill, delete_import_fields, csv_arg, errors):
    existing_data = getattr(data, kind)
    new_data = petl.fromcsv(input_file, errors=errors, **dict(csv_arg))
    new_data = generic_import_actions(new_data, attr_map, attr_fill, delete_import_fields)
    all_data = existing_data.cat(new_data)
    setattr(data, kind, all_data)


@click.command()
@click.option('--output-file', '-o', type=click.Path(dir_okay=False, readable=True, resolve_path=True), help='CSV file that data will be read from.')
@click.option('--kind', '-k', type=click.Choice(KIND_NAMES), required=True, help='Kind of data to export.')
@click.option('--csv-arg', multiple=True, type=click.Tuple([unicode, unicode]), help='Arguments that will be passed to petl\'s CSV parsing engine.')
@click.option('--errors', default='strict', help='PETL option for CSV errors.')
@click.option('--write-header/--no-write-header', default=True, help='When set the CSV file will have a header row.')
@click.option('--append/--no-append', default=False, help='When set the output file will be opened and rows will be appended to the existing data. When set --write-header is always False.')
@pass_data
def csv_export(data, output_file, kind, csv_arg, errors, write_header, append):
    existing_data = getattr(data, kind)
    if append is True:
        petl.appendcsv(existing_data, output_file, errors=errors, **dict(csv_arg))
    else:
        petl.tocsv(existing_data, output_file, errors=errors, write_header=write_header, **dict(csv_arg))


@click.command()
@click.option('--output-dir', '-o', type=click.Path(dir_okay=True, file_okay=False, readable=True, resolve_path=True), help='CSV file that data will be read from.')
@click.option('--csv-arg', multiple=True, type=click.Tuple([unicode, unicode]), help='Arguments that will be passed to petl\'s CSV parsing engine.')
@click.option('--errors', default='strict', help='PETL option for CSV errors.')
@click.option('--write-header/--no-write-header', default=True, help='When set the CSV file will have a header row.')
@click.option('--exclude-empty/--include-empty', default=True, help='When set data tables with no data in them will not create CSV files.')
@pass_data
def full_csv_export(data, output_dir, csv_arg, errors, write_header, exclude_empty):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for name in KIND_NAMES:
        current_data = getattr(data, name)
        if exclude_empty and current_data.nrows() <= 0:
            continue
        output_file = os.path.join(output_dir, KINDS[name]['filename'])
        petl.tocsv(current_data, output_file, errors=errors, write_header=write_header, **dict(csv_arg))
