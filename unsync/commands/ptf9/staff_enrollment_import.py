"""Timetabler PTF9 import functions."""
from __future__ import absolute_import
import click
import petl

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@click.option('--destination', '-d', default='enrollments', help='The destination table that these enrollments will be stored in. Defaults to enrollments.')
@pass_data
def ptf9_staff_enrollment_import(data, input_file, destination):
    """Import staff enrolments from a Timetabler PTF9 export file."""
    staff_enrollments = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}Timetables/{http://www.timetabling.com.au/TDV9}Timetable',
                                     {
                                          'TimetableID': '{http://www.timetabling.com.au/TDV9}TimetableID',
                                          'RollClassID': '{http://www.timetabling.com.au/TDV9}RollClassID',
                                          'PeriodID': '{http://www.timetabling.com.au/TDV9}PeriodID',
                                          'ClassID': '{http://www.timetabling.com.au/TDV9}ClassID',
                                          'RoomID': '{http://www.timetabling.com.au/TDV9}RoomID',
                                          'TeacherID': '{http://www.timetabling.com.au/TDV9}TeacherID',
                                     })
    data.set(destination, staff_enrollments)

command = ptf9_staff_enrollment_import

# default=[('ClassID', 'ptf9_class_id'), ('TeacherID', 'ptf9_teacher_id')]