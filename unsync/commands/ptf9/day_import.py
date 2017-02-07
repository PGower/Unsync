"""Timetabler PTF9 import functions."""
import click
import petl

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.', required=True)
@click.option('--destination', '-d', required=True, help='The destination table that these courses will be stored in.')
@pass_data
def day_import(data, input_file, destination):
    """Import courses from a Timetabler PTF9 export file."""
    new_days = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}Days/{http://www.timetabling.com.au/TDV9}Day', {
                             'DayID': '{http://www.timetabling.com.au/TDV9}DayID',
                             'Code': '{http://www.timetabling.com.au/TDV9}Code',
                             'Name': '{http://www.timetabling.com.au/TDV9}Name',
                             })
    data.set(destination, new_days)

command = day_import

# default=[('Code', 'course_id'), ('Name', 'long_name'), ('Code', 'short_name'), ('ClassID', 'ptf9_id')]
