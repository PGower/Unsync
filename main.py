import petl
import yaml
import ldap3
import re
import csv
import os


def ga_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'source/timetable.ptf9')


def ad_conn():
    s1 = ldap3.Server('10.192.81.55')
    s2 = ldap3.Server('10.192.81.54')
    pool = ldap3.ServerPool([s1, s2])
    conn = ldap3.Connection(server=pool,
                            user='CN=LDAPBinder,OU=System,OU=SMCUsers,DC=stmonicas,DC=qld,DC=edu,DC=au',
                            password='5tm0NICa5198SIx')
    return conn


def main():
    # import config
    with open('config.yaml', 'r') as f:
        config = yaml.load(f)

    # Setup some constants
    term_id = config['term_sis_id']

    merged_course_lookup_dict = {}
    for parent_course, children in config['merged_courses'].items():
        for child_course in children:
            merged_course_lookup_dict[child_course] = parent_course

    def merged_course_lookup(course_id):
        if course_id in merged_course_lookup_dict:
            return merged_course_lookup_dict[course_id]
        else:
            None

    compiled_ignored_courses = []
    for ignored_course_pattern in config['ignored_course_patterns']:
        compiled_ignored_courses.append(re.compile(ignored_course_pattern))

    def ignore_course(course_id):
        for i in compiled_ignored_courses:
            if i.match(course_id):
                return True
        return False

    account_lookup_dict = {}
    for k, v in config['account_course_patterns'].items():
        account_lookup_dict[re.compile(v)] = k

    def account_lookup(course_id):
        for k in account_lookup_dict:
            if k.match(course_id):
                return account_lookup_dict[k]
        return ''

    # COURSES / CLASSES
    courses = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Classes/{http://www.timetabling.com.au/TDV9}Class', {
                               'Class Code': '{http://www.timetabling.com.au/TDV9}Code',
                               'Class Name': '{http://www.timetabling.com.au/TDV9}Name',
                               })
    courses = petl.wrap(courses)
    courses = (courses
               .rename('Class Code', 'course_id')
               .addfield('short_name', lambda rec: rec['course_id'])
               .rename('Class Name', 'long_name')
               .addfield('term_id', term_id)
               .addfield('status', 'active')
               .addfield('account_id', lambda rec: account_lookup(rec['course_id']))
               .addfield('merged', lambda rec: merged_course_lookup(rec['course_id']))
               .select('merged', lambda v: v is None)
               .cut('course_id', 'short_name', 'long_name', 'term_id', 'status', 'account_id'))

    # remove ignored courses
    for i in config['ignored_course_patterns']:
        courses = courses.searchcomplement('course_id', i)

    courses = courses.convert('course_id', lambda v: '{}_{}'.format(v, term_id))

    # add merged courses
    for i in config['merged_courses']:
        courses = courses.cat([['course_id', 'short_name', 'long_name', 'term_id', 'status', 'account_id'], [i, i, i, term_id, 'active', '']])

    # USERS / PERSONS
    students = petl.fromldap(ad_conn(),
                             base_ou='OU=Student Users,OU=Automated Objects,DC=stmonicas,DC=qld,DC=edu,DC=au',
                             query='(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))',
                             attributes=['givenName', 'sn', 'mail', 'employeeID', 'sAMAccountName'])
    students = petl.wrap(students)
    students = (students
                .rename({'givenName': 'first_name', 'sn': 'last_name', 'mail': 'email', 'employeeID': 'user_id', 'sAMAccountName': 'login_id'})
                .select('user_id', lambda v: v is not None and v != '')  # Filter out records with no user_id, they are useless
                .convert('user_id', lambda v: str(v)[1:] if str(v).startswith('c') else v))  # Remove the c from the user_id

    ad_staff = petl.fromldap(ad_conn(),
                             base_ou='OU=School Staff,OU=Staff Users,OU=Automated Objects,DC=stmonicas,DC=qld,DC=edu,DC=au',
                             query='(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))',
                             attributes=['givenName', 'sn', 'mail', 'employeeID', 'sAMAccountName', 'extensionAttribute2'],
                             defaults={'extensionAttribute2': None})
    ad_relief_staff = petl.fromldap(ad_conn(),
                                    base_ou='OU=Relief Staff,OU=Staff Users,OU=Automated Objects,DC=stmonicas,DC=qld,DC=edu,DC=au',
                                    query='(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))',
                                    attributes=['givenName', 'sn', 'mail', 'employeeID', 'sAMAccountName', 'extensionAttribute2'],
                                    defaults={'extensionAttribute2': None})

    staff = petl.cat(ad_staff, ad_relief_staff)
    staff = petl.wrap(staff)
    staff = (staff
             .rename({'givenName': 'first_name', 'sn': 'last_name', 'mail': 'email', 'employeeID': 'user_id', 'sAMAccountName': 'login_id'})
             .select('user_id', lambda v: v is not None and v != '')  # Filter out records with no user_id, they are useless
             .convert('user_id', lambda v: str(v)[1:] if str(v).startswith('c') else v))  # Remove the c from the user_id
    staff_id_map = staff.cut('user_id', 'extensionAttribute2')
    staff = staff.cut('first_name', 'last_name', 'email', 'user_id', 'login_id')
    staff_id_map = (staff_id_map
                    .rename({'user_id': 'canvas_id', 'extensionAttribute2': 'teacher_code'})
                    .select('teacher_code', lambda v: v is not None)
                    .convert('teacher_code', lambda v: str(v)))

    people = petl.cat(students, staff)
    people = (people
              .addfield('status', 'active')
              .addfield('full_name', lambda rec: '{} {}'.format(rec['first_name'], rec['last_name']))
              .cut('user_id', 'login_id', 'first_name', 'last_name', 'full_name', 'email', 'status')
              .sort('user_id'))

    # ENROLLMENTS
    student_enrollments = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}StudentLessons/{http://www.timetabling.com.au/TDV9}StudentLesson',
                                       {
                                          'student_id': '{http://www.timetabling.com.au/TDV9}StudentID',
                                          'class_code': '{http://www.timetabling.com.au/TDV9}ClassCode'
                                       })
    student_enrollments = petl.wrap(student_enrollments)

    teacher_enrollments = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Timetables/{http://www.timetabling.com.au/TDV9}Timetable',
                                       {
                                          'teacher_id': '{http://www.timetabling.com.au/TDV9}TeacherID',
                                          'class_id': '{http://www.timetabling.com.au/TDV9}ClassID'
                                       })
    teacher_enrollments = petl.wrap(teacher_enrollments)

    class_codes = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Classes/{http://www.timetabling.com.au/TDV9}Class',
                               {
                                  'class_id': '{http://www.timetabling.com.au/TDV9}ClassID',
                                  'class_code': '{http://www.timetabling.com.au/TDV9}Code'
                               })

    teacher_codes = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Teachers/{http://www.timetabling.com.au/TDV9}Teacher', {
                                'teacher_id': '{http://www.timetabling.com.au/TDV9}TeacherID',
                                'teacher_code': '{http://www.timetabling.com.au/TDV9}Code'
                             })

    student_codes = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Students/{http://www.timetabling.com.au/TDV9}Student',
                                 {
                                    'student_id': '{http://www.timetabling.com.au/TDV9}StudentID',
                                    'student_code': '{http://www.timetabling.com.au/TDV9}Code',
                                 })

    teacher_enrollments = (teacher_enrollments
                           .distinct()
                           .join(teacher_codes, key='teacher_id')
                           .join(staff_id_map, key='teacher_code')
                           .join(class_codes, key='class_id')
                           .cut('class_code', 'canvas_id')
                           .rename('canvas_id', 'user_id')
                           .addfield('role', 'teacher'))

    student_enrollments = (student_enrollments
                           .distinct()
                           .join(student_codes, key='student_id')
                           .cut('class_code', 'student_code')
                           .rename('student_code', 'user_id')
                           .addfield('role', 'student'))

    enrollments = petl.cat(student_enrollments, teacher_enrollments)

    # remove ignored courses
    for i in config['ignored_course_patterns']:
        # TODO: Figure out a way to indicate how many or which class_id's were removed
        enrollments = enrollments.searchcomplement('class_code', i)

    enrollments = (enrollments
                   .rename('class_code', 'course_id')
                   .addfield('old_course_id', lambda rec: rec['course_id'])
                   .addfield('status', 'active')
                   .addfield('merged', lambda rec: merged_course_lookup(rec['course_id']))
                   .addfield('section_id', lambda rec: '{}_{}'.format(rec['course_id'], term_id) if rec['merged'] else None)
                   .convert('course_id', lambda v, rec: rec['course_id'] if rec['merged'] is None else rec['merged'], pass_row=True)
                   .convert('course_id', lambda v, rec: '{}_{}'.format(rec['course_id'], term_id) if rec['merged'] is None else rec['course_id'], pass_row=True))
    section_enrollments = enrollments
    enrollments = enrollments.cut('course_id', 'user_id', 'role', 'section_id', 'status')

    # SECTIONS
    sections = section_enrollments.distinct('section_id')
    sections = (sections
                .addfield('name', lambda rec: rec['old_course_id'])
                .addfield('status', 'active')
                .cut('section_id', 'course_id', 'name', 'status'))

    # Remove users with no enrollments
    enrolled_users = enrollments.cut('user_id').addfield('enrolled', True).distinct(key='user_id')
    people = people.join(enrolled_users, key='user_id').select('enrolled', lambda v: v is True).cutout('enrolled')

    people.tocsv('csvs/users.csv')
    enrollments.tocsv('csvs/enrollments.csv')
    courses.tocsv('csvs/courses.csv')
    sections.tocsv('csvs/sections.csv')

    # find merged and convert to sections
    # get all sections and turn into deduped sections 
    # dump to csv in Canvas format


if __name__ == '__main__':
    main()