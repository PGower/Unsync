"""Timetabler PTF9 import functions."""
import unsync
import petl


@unsync.command()
@unsync.option('--input-file', '-i', type=unsync.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@unsync.option('--destination', '-d', default='enrollments', help='The destination table that these enrollments will be stored in. Defaults to enrollments.')
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