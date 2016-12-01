from __future__ import absolute_import
import click
import petl

from .common import KINDS, pass_data, generic_import_actions


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@click.option('--status', default='active', type=click.Choice(KINDS['courses']['enums']['status']), help='All courses imported will have this status.')
@click.option('--attr-map', '-m', multiple=True, type=click.Tuple([unicode, unicode]), default=[('Code', 'course_id'), ('Name', 'long_name'), ('Code', 'short_name'), ('ClassID', 'ptf9_id')], help='Determines how fields from the ptf9 data will be mapped to Canvas course fields.')
@click.option('--attr-fill', '-f', multiple=True, type=click.Tuple([unicode, unicode]), help='Fill attributes with values from the provided pairs. First name is the attribute name second is the value.')
@click.option('--delete-import-fields/--no-delete-import-fields', default=True, help='When set any fields that were imported and not explicitly named in the attr_map or attr_fill will be removed.')
@pass_data
def ptf9_course_import(data, input_file, status, attr_map, attr_fill, delete_import_fields):
    # TODO: What do we do if there is existing data from another source and we have new data?
    courses = data.courses
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
    attr_fill += (('status', status),)
    new_courses = generic_import_actions(new_courses, attr_map, attr_fill, delete_import_fields)

    courses = courses.cat(new_courses)
    data.courses = courses


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@click.option('--status', default='active', type=click.Choice(KINDS['users']['enums']['status']), help='All users imported will have this status.')
@click.option('--attr-map', '-m', multiple=True, type=click.Tuple([unicode, unicode]), default=[('FirstName', 'first_name'), ('FamilyName', 'last_name'), ('Email', 'email'), ('Code', 'integration_id'), ('StudentID', 'ptf9_id')], help='Determines how fields from the ptf9 data will be mapped to Canvas course fields.')
@click.option('--attr-fill', '-f', multiple=True, type=click.Tuple([unicode, unicode]), help='Fill attributes with values from the provided pairs. First name is the attribute name second is the value.')
@click.option('--delete-import-fields/--no-delete-import-fields', default=True, help='When set any fields that were imported and not explicitly named in the attr_map or attr_fill will be removed.')
@pass_data
def ptf9_student_import(data, input_file, status, attr_map, attr_fill, delete_import_fields):
    users = data.users
    student_users = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}Students/{http://www.timetabling.com.au/TDV9}Student',
                                 {
                                   'StudentID': '{http://www.timetabling.com.au/TDV9}StudentID',
                                   'Code': '{http://www.timetabling.com.au/TDV9}Code',
                                   'FirstName': '{http://www.timetabling.com.au/TDV9}FirstName',
                                   'MiddleName': '{http://www.timetabling.com.au/TDV9}MiddleName',
                                   'FamilyName': '{http://www.timetabling.com.au/TDV9}FamilyName',
                                   'Gender': '{http://www.timetabling.com.au/TDV9}Gender',
                                   'Email': '{http://www.timetabling.com.au/TDV9}Email',
                                   'House': '{http://www.timetabling.com.au/TDV9}House',
                                   'RollClass': '{http://www.timetabling.com.au/TDV9}RollClass',
                                   'YearLevel': '{http://www.timetabling.com.au/TDV9}YearLevel',
                                   'HomeGroup': '{http://www.timetabling.com.au/TDV9}HomeGroup',
                                   'WCSet': '{http://www.timetabling.com.au/TDV9}WCSet',
                                   'BOSCode': '{http://www.timetabling.com.au/TDV9}BOSCode',
                                   'SpareField1': '{http://www.timetabling.com.au/TDV9}SpareField1',
                                   'SpareField2': '{http://www.timetabling.com.au/TDV9}SpareField2',
                                   'SpareField3': '{http://www.timetabling.com.au/TDV9}SpareField3',
                                 })
    attr_fill += (('status', status),)
    student_users = generic_import_actions(student_users, attr_map, attr_fill, delete_import_fields)

    users = users.cat(student_users)
    data.users = users


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@click.option('--status', default='active', type=click.Choice(KINDS['users']['enums']['status']), help='All users imported will have this status.')
@click.option('--attr-map', '-m', multiple=True, type=click.Tuple([unicode, unicode]), default=[('FirstName', 'first_name'), ('LastName', 'last_name'), ('Email', 'email'), ('Code', 'integration_id'), ('TeacherID', 'ptf9_id')], help='Determines how fields from the ptf9 data will be mapped to Canvas course fields.')
@click.option('--attr-fill', '-f', multiple=True, type=click.Tuple([unicode, unicode]), help='Fill attributes with values from the provided pairs. First name is the attribute name second is the value.')
@click.option('--delete-import-fields/--no-delete-import-fields', default=True, help='When set any fields that were imported and not explicitly named in the attr_map or attr_fill will be removed.')
@pass_data
def ptf9_staff_import(data, input_file, status, attr_map, attr_fill, delete_import_fields):
    users = data.users
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

    users = users.cat(staff_users)
    data.users = users


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@click.option('--status', default='active', type=click.Choice(KINDS['enrollments']['enums']['status']), help='All enrollments imported will have this status.')
@click.option('--attr-map', '-m', multiple=True, type=click.Tuple([unicode, unicode]), default=[('StudentID', 'ptf9_student_id'), ('ClassCode', 'course_id')], help='Determines how fields from the ptf9 data will be mapped to Canvas course fields.')
@click.option('--attr-fill', '-f', multiple=True, type=click.Tuple([unicode, unicode]), help='Fill attributes with values from the provided pairs. First name is the attribute name second is the value.')
@click.option('--delete-import-fields/--no-delete-import-fields', default=True, help='When set any fields that were imported and not explicitly named in the attr_map or attr_fill will be removed.')
@pass_data
def ptf9_student_enrollment_import(data, input_file, status, attr_map, attr_fill, delete_import_fields):
    enrollments = data.enrollments
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

    enrollments = enrollments.cat(student_enrollments)
    data.enrollments = enrollments


@click.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Timetabler PTF9 file to extract data from.')
@click.option('--status', default='active', type=click.Choice(KINDS['enrollments']['enums']['status']), help='All enrollments imported will have this status.')
@click.option('--attr-map', '-m', multiple=True, type=click.Tuple([unicode, unicode]), default=[('ClassID', 'ptf9_class_id'), ('TeacherID', 'ptf9_teacher_id')], help='Determines how fields from the ptf9 data will be mapped to Canvas course fields.')
@click.option('--attr-fill', '-f', multiple=True, type=click.Tuple([unicode, unicode]), help='Fill attributes with values from the provided pairs. First name is the attribute name second is the value.')
@click.option('--delete-import-fields/--no-delete-import-fields', default=True, help='When set any fields that were imported and not explicitly named in the attr_map or attr_fill will be removed.')
@pass_data
def ptf9_staff_enrollment_import(data, input_file, status, attr_map, attr_fill, delete_import_fields):
    enrollments = data.enrollments
    staff_enrollments = petl.fromxml(input_file, '{http://www.timetabling.com.au/TDV9}Timetables/{http://www.timetabling.com.au/TDV9}Timetable',
                                     {
                                          'TimetableID': '{http://www.timetabling.com.au/TDV9}TimetableID',
                                          'RollClassID': '{http://www.timetabling.com.au/TDV9}RollClassID',
                                          'PeriodID': '{http://www.timetabling.com.au/TDV9}PeriodID',
                                          'ClassID': '{http://www.timetabling.com.au/TDV9}ClassID',
                                          'RoomID': '{http://www.timetabling.com.au/TDV9}RoomID',
                                          'TeacherID': '{http://www.timetabling.com.au/TDV9}TeacherID',
                                     })
    attr_fill += (('status', status),)
    staff_enrollments = generic_import_actions(staff_enrollments, attr_map, attr_fill, delete_import_fields)

    enrollments = enrollments.cat(staff_enrollments)
    data.enrollments = enrollments


