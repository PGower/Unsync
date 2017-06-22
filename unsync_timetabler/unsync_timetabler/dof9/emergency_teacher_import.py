"""Timetabler DOF9 import functions."""
import unsync
import petl


@unsync.command()
@unsync.option('--input-file', '-i', type=unsync.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler DOF9 file to extract data from.', required=True)
@unsync.option('--destination', '-d', required=True, help='The destination table that these courses will be stored in.')
def dof9_emergency_teacher_import(data, input_file, destination):
    """Import the emergency teaher information from a Timetabler DOF9 file."""
    emergency_teachers = petl.fromxml(input_file, '{http://www.timetabling.com.au/DOV9}EmergencyTeachers/{http://www.timetabling.com.au/DOV9}EmergencyTeacher', {
                                                  'EmergencyTeacherID': '{http://www.timetabling.com.au/DOV9}EmergencyTeacherID',
                                                  'Code': '{http://www.timetabling.com.au/DOV9}Code',
                                                  'FirstName': '{http://www.timetabling.com.au/DOV9}FirstName',
                                                  'MiddleName': '{http://www.timetabling.com.au/DOV9}MiddleName',
                                                  'LastName': '{http://www.timetabling.com.au/DOV9}LastName',
                                                  'Salutation': '{http://www.timetabling.com.au/DOV9}Salutation',
                                                  'Email': '{http://www.timetabling.com.au/DOV9}Email',
                                                  'Address': '{http://www.timetabling.com.au/DOV9}Address',
                                                  'Suburb': '{http://www.timetabling.com.au/DOV9}Suburb',
                                                  'State': '{http://www.timetabling.com.au/DOV9}State',
                                                  'Postcode': '{http://www.timetabling.com.au/DOV9}Postcode',
                                                  'Phone': '{http://www.timetabling.com.au/DOV9}Phone',
                                                  'Mobile': '{http://www.timetabling.com.au/DOV9}Mobile',
                                                  'OtherPhone': '{http://www.timetabling.com.au/DOV9}OtherPhone',
                                                  'Priority': '{http://www.timetabling.com.au/DOV9}Priority',
                                                  'Notes': '{http://www.timetabling.com.au/DOV9}Notes',
                                                  'SpareField1': '{http://www.timetabling.com.au/DOV9}SpareField1',
                                                  'SpareField2': '{http://www.timetabling.com.au/DOV9}SpareField2',
                                                  'SpareField3': '{http://www.timetabling.com.au/DOV9}SpareField3'})
    data.set(destination, emergency_teachers)

dof9_emergency_teacher_import.display_name = 'emergency_teacher_import'
