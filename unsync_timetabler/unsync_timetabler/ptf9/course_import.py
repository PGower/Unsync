"""Timetabler PTF9 import functions."""
import unsync
import petl


@unsync.command()
@unsync.option('--input-file', '-i', type=unsync.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.', required=True)
@unsync.option('--destination', '-d', required=True, help='The destination table that these courses will be stored in.')
def ptf9_course_import(data, input_file, destination):
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
                                           'ClassCodeCheck': '{http://www.timetabling.com.au/TDV9}ClassCodeCheck'})
    data.set(destination, new_courses)

command = ptf9_course_import

# default=[('Code', 'course_id'), ('Name', 'long_name'), ('Code', 'short_name'), ('ClassID', 'ptf9_id')]
