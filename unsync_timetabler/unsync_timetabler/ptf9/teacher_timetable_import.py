"""Timetabler PTF9 import functions."""
import unsync
import petl


@unsync.command()
@unsync.option('--input-file', '-i', type=unsync.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.', required=True)
@unsync.option('--destination', '-d', required=True, help='The destination table that these courses will be stored in.')
def teacher_timetable_import(data, input_file, destination):
    """Import the teacher timetable information from a PTF9 file."""
    teacher_timetables = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}Timetables/{http://www.timetabling.com.au/TDV9}Timetable', {
                             'TimetableID': '{http://www.timetabling.com.au/TDV9}TimetableID',
                             'RollClassID': '{http://www.timetabling.com.au/TDV9}RollClassID',
                             'PeriodID': '{http://www.timetabling.com.au/TDV9}PeriodID',
                             'ClassID': '{http://www.timetabling.com.au/TDV9}ClassID',
                             'RoomID': '{http://www.timetabling.com.au/TDV9}RoomID',
                             'TeacherID': '{http://www.timetabling.com.au/TDV9}TeacherID'
                             })
    data.set(destination, teacher_timetables)

command = teacher_timetable_import

# default=[('Code', 'course_id'), ('Name', 'long_name'), ('Code', 'short_name'), ('ClassID', 'ptf9_id')]
