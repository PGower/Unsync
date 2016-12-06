"""Timetabler PTF9 import functions."""
from __future__ import absolute_import
import click
import petl

from .common import KINDS, pass_data, generic_import_actions


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.', required=True)
@click.option('--status', default='active', type=click.Choice(KINDS['courses']['enums']['status']), help='All courses imported will have this status.')
# @click.option('--attr-map', '-m', multiple=True, type=click.Tuple([unicode, unicode]), help='Determines how fields from the ptf9 data will be mapped to Canvas course fields.')
# @click.option('--attr-fill', '-f', multiple=True, type=click.Tuple([unicode, unicode]), help='Fill attributes with values from the provided pairs. First name is the attribute name second is the value.')
# @click.option('--delete-import-fields/--no-delete-import-fields', default=True, help='When set any fields that were imported and not explicitly named in the attr_map or attr_fill will be removed.')
@click.option('--destination', '-d', default='courses', help='The destination table that these courses will be stored in.')
@pass_data
def ptf9_course_import(data, input_file, status, destination):
    """Import courses from a Timetabler PTF9 export file."""
    new_courses = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}Classes/{http://www.timetabling.com.au/TDV9}Class', {
                             'ClassID': '{http://www.timetabling.com.au/TDV9}ClassID',
                             'Code': '{http://www.timetabling.com.au/TDV9}Code',
                             'Name': '{http://www.timetabling.com.au/TDV9}Name',
                             'FacultyID': '{http://www.timetabling.com.au/TDV9}FacultyID',
                             'Suffix': '{http://www.timetabling.com.au/TDV9}Suffix',
                             'SubjectName': '{http://www.timetabling.com.au/TDV9}SubjectName',
                             'SubjectCode': '{http://www.timetabling.com.au/TDV9}SubjectCode',
                             'BOSClassCode1': '{http://www.timetabling.com.au/TDV9}BOSClassCode1',
                             'BOSClassCode2': '{http://www.timetabling.com.au/TDV9}BOSClassCode2',
                             'BOSClassCode3': '{http://www.timetabling.com.au/TDV9}BOSClassCode3',
                             'ClassCodeCheck': '{http://www.timetabling.com.au/TDV9}ClassCodeCheck',
                             })
    # attr_fill += (('status', status),)
    # new_courses = generic_import_actions(new_courses, attr_map, attr_fill, delete_import_fields)
    data.cat(destination, new_courses)

command = ptf9_course_import

# default=[('Code', 'course_id'), ('Name', 'long_name'), ('Code', 'short_name'), ('ClassID', 'ptf9_id')]
