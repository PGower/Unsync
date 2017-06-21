"""Timetabler PTF9 import functions."""
from __future__ import absolute_import
import click
import petl

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@click.option('--destination', '-d', default='enrollments', help='The destination table that these enrollments will be stored in.')
@pass_data
def ptf9_student_enrollment_import(data, input_file, destination):
    """Import student enrollments from a Timetabler PTF9 export file."""
    student_enrollments = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}StudentLessons/{http://www.timetabling.com.au/TDV9}StudentLesson',
                                       {
                                            'StudentID': '{http://www.timetabling.com.au/TDV9}StudentID',
                                            'CourseID': '{http://www.timetabling.com.au/TDV9}CourseID',
                                            'LessonType': '{http://www.timetabling.com.au/TDV9}LessonType',
                                            'ClassCode': '{http://www.timetabling.com.au/TDV9}ClassCode',
                                            'RollClassCode': '{http://www.timetabling.com.au/TDV9}RollClassCode',
                                       })
    data.cat(destination, student_enrollments)

command = ptf9_student_enrollment_import


# default=[('StudentID', 'ptf9_student_id'), ('ClassCode', 'course_id')]