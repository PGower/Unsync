"""Timetabler PTF9 import functions."""
from __future__ import absolute_import
import click
import petl

from .common import KINDS, pass_data, generic_import_actions


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@click.option('--status', default='active', type=click.Choice(KINDS['users']['enums']['status']), help='All users imported will have this status.')
@click.option('--attr-map', '-m', multiple=True, type=click.Tuple([unicode, unicode]), default=[('FirstName', 'first_name'), ('LastName', 'last_name'), ('Email', 'email'), ('Code', 'integration_id'), ('TeacherID', 'ptf9_id')], help='Determines how fields from the ptf9 data will be mapped to Canvas course fields.')
@click.option('--attr-fill', '-f', multiple=True, type=click.Tuple([unicode, unicode]), help='Fill attributes with values from the provided pairs. First name is the attribute name second is the value.')
@click.option('--delete-import-fields/--no-delete-import-fields', default=True, help='When set any fields that were imported and not explicitly named in the attr_map or attr_fill will be removed.')
@click.option('--destination', '-d', default='users', help='The destination table that these users will be stored in.')
@pass_data
def ptf9_staff_import(data, input_file, status, attr_map, attr_fill, delete_import_fields, destination):
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
    attr_fill += (('status', status),)
    staff_users = generic_import_actions(staff_users, attr_map, attr_fill, delete_import_fields)
    data.cat(destination, staff_users)

command = ptf9_staff_import
