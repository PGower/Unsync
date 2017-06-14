"""Timetabler PTF9 import functions."""
from __future__ import absolute_import
import click
import petl

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@click.option('--destination', '-d', default='users', help='The destination table that these users will be stored in.')
@pass_data
def ptf9_student_import(data, input_file, destination):
    """Import student users from a Timetabler PTF9 export file."""
    student_users = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}Students/{http://www.timetabling.com.au/TDV9}Student',
                                 {
                                   'StudentID': '{http://www.timetabling.com.au/TDV9}StudentID',
                                   'Code': '{http://www.timetabling.com.au/TDV9}Code',
                                   'FirstName': '{http://www.timetabling.com.au/TDV9}FirstName',
                                   'MiddleName': '{http://www.timetabling.com.au/TDV9}MiddleName',
                                   'FamilyName': '{http://www.timetabling.com.au/TDV9}FamilyName',
                                   'Gender': '{http://www.timetabling.com.au/TDV9}Gender',
                                   'Email': '{http://www.timetabling.com.au/TDV9}Email',
                                   'House': '{http://www.timetabling.com.au/TDV9}House',
                                   'RollClass': '{http://www.timetabling.com.au/TDV9}RollClass',
                                   'YearLevel': '{http://www.timetabling.com.au/TDV9}YearLevel',
                                   'HomeGroup': '{http://www.timetabling.com.au/TDV9}HomeGroup',
                                   'WCSet': '{http://www.timetabling.com.au/TDV9}WCSet',
                                   'BOSCode': '{http://www.timetabling.com.au/TDV9}BOSCode',
                                   'SpareField1': '{http://www.timetabling.com.au/TDV9}SpareField1',
                                   'SpareField2': '{http://www.timetabling.com.au/TDV9}SpareField2',
                                   'SpareField3': '{http://www.timetabling.com.au/TDV9}SpareField3',
                                 })
    data.cat(destination, student_users)

command = ptf9_student_import


# default=[('FirstName', 'first_name'), ('FamilyName', 'last_name'), ('Email', 'email'), ('Code', 'integration_id'), ('StudentID', 'ptf9_id')]