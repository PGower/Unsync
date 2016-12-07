"""Timetabler PTF9 import functions."""
from __future__ import absolute_import
import click
import petl

from lib.common import pass_data


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@click.option('--destination', '-d', default='users', help='The destination table that these users will be stored in.')
@pass_data
def ptf9_staff_import(data, input_file, destination):
    """Import staff users from a Timetabler PTF9 export file."""
    staff_users = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}Teachers/{http://www.timetabling.com.au/TDV9}Teacher',
                               {
                                  'TeacherID': '{http://www.timetabling.com.au/TDV9}TeacherID',
                                  'Code': '{http://www.timetabling.com.au/TDV9}Code',
                                  'FirstName': '{http://www.timetabling.com.au/TDV9}FirstName',
                                  'MiddleName': '{http://www.timetabling.com.au/TDV9}MiddleName',
                                  'LastName': '{http://www.timetabling.com.au/TDV9}LastName',
                                  'Salutation': '{http://www.timetabling.com.au/TDV9}Salutation',
                                  'DaysUnavailable': '{http://www.timetabling.com.au/TDV9}DaysUnavailable',
                                  'PeriodsUnavailable': '{http://www.timetabling.com.au/TDV9}PeriodsUnavailable',
                                  'ProposedLoad': '{http://www.timetabling.com.au/TDV9}ProposedLoad',
                                  'ActualLoad': '{http://www.timetabling.com.au/TDV9}ActualLoad',
                                  'FinalLoad': '{http://www.timetabling.com.au/TDV9}FinalLoad',
                                  'ConsecutivePeriods': '{http://www.timetabling.com.au/TDV9}ConsecutivePeriods',
                                  'MaxYardDutyLoad': '{http://www.timetabling.com.au/TDV9}MaxYardDutyLoad',
                                  'PeriodsOff': '{http://www.timetabling.com.au/TDV9}PeriodsOff',
                                  'Email': '{http://www.timetabling.com.au/TDV9}Email',
                                  'SpareField1': '{http://www.timetabling.com.au/TDV9}SpareField1',
                                  'SpareField2': '{http://www.timetabling.com.au/TDV9}SpareField2',
                                  'SpareField3': '{http://www.timetabling.com.au/TDV9}SpareField3',
                               })
    data.set(destination, staff_users)

command = ptf9_staff_import
