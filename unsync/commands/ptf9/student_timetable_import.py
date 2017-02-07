"""Timetabler PTF9 import functions."""
import click
import petl

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.', required=True)
@click.option('--destination', '-d', required=True, help='The destination table that these courses will be stored in.')
@pass_data
def student_timetable_import(data, input_file, destination):
    """Import the teacher timetable information from a PTF9 file."""
    student_timetables = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}StudentLessons/{http://www.timetabling.com.au/TDV9}StudentLesson', {
                             'StudentID': '{http://www.timetabling.com.au/TDV9}StudentID',
                             'CourseID': '{http://www.timetabling.com.au/TDV9}CourseID',
                             'LessonType': '{http://www.timetabling.com.au/TDV9}LessonType',
                             'ClassCode': '{http://www.timetabling.com.au/TDV9}ClassCode',
                             'RollClassCode': '{http://www.timetabling.com.au/TDV9}RollClassCode'
                             })
    data.set(destination, student_timetables)

command = student_timetable_import

# default=[('Code', 'course_id'), ('Name', 'long_name'), ('Code', 'short_name'), ('ClassID', 'ptf9_id')]
