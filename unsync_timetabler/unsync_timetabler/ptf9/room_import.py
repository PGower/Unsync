"""Timetabler PTF9 import functions."""
import click
import petl

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.', required=True)
@click.option('--destination', '-d', required=True, help='The destination table that these courses will be stored in.')
@pass_data
def room_import(data, input_file, destination):
    """Import courses from a Timetabler PTF9 export file."""
    new_rooms = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}Rooms/{http://www.timetabling.com.au/TDV9}Room', {
                             'RoomID': '{http://www.timetabling.com.au/TDV9}RoomID',
                             'Code': '{http://www.timetabling.com.au/TDV9}Code',
                             'Name': '{http://www.timetabling.com.au/TDV9}Name',
                             'Seats': '{http://www.timetabling.com.au/TDV9}Seats',
                             'SiteNo': '{http://www.timetabling.com.au/TDV9}SiteNo',
                             'Notes': '{http://www.timetabling.com.au/TDV9}Notes',
                             })
    data.set(destination, new_rooms)

command = room_import
