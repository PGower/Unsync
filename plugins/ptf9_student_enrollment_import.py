"""Timetabler PTF9 import functions."""
from __future__ import absolute_import
import click
import petl

from .common import KINDS, pass_data, generic_import_actions


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@click.option('--status', default='active', type=click.Choice(KINDS['enrollments']['enums']['status']), help='All enrollments imported will have this status.')
@click.option('--attr-map', '-m', multiple=True, type=click.Tuple([unicode, unicode]), default=[('StudentID', 'ptf9_student_id'), ('ClassCode', 'course_id')], help='Determines how fields from the ptf9 data will be mapped to Canvas course fields.')
@click.option('--attr-fill', '-f', multiple=True, type=click.Tuple([unicode, unicode]), help='Fill attributes with values from the provided pairs. First name is the attribute name second is the value.')
@click.option('--delete-import-fields/--no-delete-import-fields', default=True, help='When set any fields that were imported and not explicitly named in the attr_map or attr_fill will be removed.')
@click.option('--destination', '-d', default='enrollments', help='The destination table that these enrollments will be stored in.')
@pass_data
def ptf9_student_enrollment_import(data, input_file, status, attr_map, attr_fill, delete_import_fields, destination):
    """Import student enrollments from a Timetabler PTF9 export file."""
    student_enrollments = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}StudentLessons/{http://www.timetabling.com.au/TDV9}StudentLesson',
                                       {
                                            'StudentID': '{http://www.timetabling.com.au/TDV9}StudentID',
                                            'CourseID': '{http://www.timetabling.com.au/TDV9}CourseID',
                                            'LessonType': '{http://www.timetabling.com.au/TDV9}LessonType',
                                            'ClassCode': '{http://www.timetabling.com.au/TDV9}ClassCode',
                                            'RollClassCode': '{http://www.timetabling.com.au/TDV9}RollClassCode',
                                       })
    attr_fill += (('status', status),)
    student_enrollments = generic_import_actions(student_enrollments, attr_map, attr_fill, delete_import_fields)
    data.cat(destination, student_enrollments)

command = ptf9_student_enrollment_import
