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

    courses.tocsv('csvs/courses.csv')

    # USERS / PERSONS
    ad_students = petl.fromldap(ad_conn(),
                                base_ou='OU=Student Users,OU=Automated Objects,DC=stmonicas,DC=qld,DC=edu,DC=au',
                                query='(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))',
                                attributes=['givenName', 'sn', 'mail', 'employeeID', 'sAMAccountName'])
    ga_students = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Students/{http://www.timetabling.com.au/TDV9}Student',
                               {
                                 'Student Code': '{http://www.timetabling.com.au/TDV9}Code',
                                 'Gender': '{http://www.timetabling.com.au/TDV9}Gender',
                                 'House': '{http://www.timetabling.com.au/TDV9}House',
                                 'Home Group': '{http://www.timetabling.com.au/TDV9}HomeGroup',
                                 'Year Level': '{http://www.timetabling.com.au/TDV9}YearLevel',
                                 'Roll Class Code': '{http://www.timetabling.com.au/TDV9}RollClass',
                                 'Last Name': '{http://www.timetabling.com.au/TDV9}FamilyName',
                                 'First Name': '{http://www.timetabling.com.au/TDV9}FirstName',
                                 'Middle Name': '{http://www.timetabling.com.au/TDV9}MiddleName'
                               })

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

    # Students
    ad_students_1 = petl.transform.rename(ad_students, {
                                          'givenName': 'firstname',
                                          'sn': 'surname',
                                          'mail': 'email'
                                          })
    ad_students_1 = petl.sort(ad_students_1, 'employeeID')
    ad_students_1 = petl.convert(ad_students_1, 'employeeID', lambda v: str(v))

    ga_students_1 = petl.transform.rename(ga_students, {
                                          'Student Code': 'sas_id',
                                          'Gender': 'gender',
                                          'House': 'homeform',
                                          'Home Group': 'homeform',
                                          'Year Level': 'yearlevel'
                                          })
    ga_students_2 = petl.transform.cut(ga_students_1, 'sas_id', 'gender', 'homeform', 'yearlevel')
    ga_students_3 = petl.transform.addfield(ga_students_2, 'employeeID', lambda rec: 'c{}'.format(rec['sas_id']))
    ga_students_3 = petl.sort(ga_students_3, 'employeeID')
    ga_students_3 = petl.convert(ga_students_3, 'employeeID', lambda v: str(v))

    combined_students = petl.transform.join(ad_students_1, ga_students_3, 'employeeID')
    combined_students = petl.wrap(combined_students)
    combined_students = (combined_students
                         .addfield('preferredname', lambda rec: rec['firstname'])
                         .addfield('middlename', '')
                         .addfield('birthdate', None)
                         .convert('yearlevel', int)
                         .addfield('role', 'student'))

    # Teachers
    ad_staff = petl.transform.addfield(ad_staff, 'role', 'staff')
    ad_staff = petl.rename(ad_staff, 'extensionAttribute2', 'sas_id')
    ad_relief_staff = petl.transform.addfield(ad_relief_staff, 'role', 'relief_teacher')
    ad_relief_staff = petl.rename(ad_relief_staff, 'extensionAttribute2', 'sas_id')

    combined_staff = petl.transform.cat(ad_staff, ad_relief_staff)
    combined_staff = petl.wrap(combined_staff)
    combined_staff = (combined_staff
                      .rename({
                          'givenName': 'firstname',
                          'sn': 'surname',
                          'mail': 'email',
                      })
                      .addfield('gender', None)
                      .addfield('homeform', None)
                      .addfield('yearlevel', None)
                      .addfield('preferredname', lambda rec: rec['firstname'])
                      .addfield('birthdate', None)
                      .addfield('middlename', None)
                      .convert('role', lambda v, rec: 'teacher' if rec['sas_id'] is not None else rec['role'], pass_row=True))
    people_1 = petl.transform.cat(combined_students, combined_staff)
    people_2 = petl.transform.addfield(people_1, 'id', lambda rec: rec['employeeID'][1:] if rec['employeeID'].startswith(('c', 'C')) else rec['employeeID'])
    people = petl.transform.convert(people_2, 'id', int)
    people = petl.wrap(people)
    people = (people
              .rename('id', 'user_id')
              .rename('sAMAccountName', 'login_id')
              .addfield('full_name', lambda rec: '{} {}'.format(rec['firstname'], rec['surname']))
              .addfield('status', 'active')
              .rename('firstname', 'first_name')
              .rename('surname', 'last_name')
              .cut('user_id', 'login_id', 'first_name', 'last_name', 'full_name', 'email', 'status'))

    people.tocsv('csvs/users.csv')
    
    # ENROLLMENTS
    student_source = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}StudentLessons/{http://www.timetabling.com.au/TDV9}StudentLesson',
                                  {
                                     'student_id': '{http://www.timetabling.com.au/TDV9}StudentID',
                                     'Class Code': '{http://www.timetabling.com.au/TDV9}ClassCode'
                                  })
    student_source = petl.wrap(student_source)
    student_codes = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Students/{http://www.timetabling.com.au/TDV9}Student',
                                 {
                                    'student_id': '{http://www.timetabling.com.au/TDV9}StudentID',
                                    'Student Code': '{http://www.timetabling.com.au/TDV9}Code',
                                 })
    student_source = petl.join(student_source, student_codes, key='student_id')
    student_source = (student_source
                      .rename('Student Code', 'person_id')
                      .rename('Class Code', 'klass_id')
                      .addfield('kind', 'student')
                      .addfieldusingcontext('id', lambda prv, cur, nxt: '{}_{}_{}'.format(cur.person_id, cur.klass_id, cur.kind))
                      .cut('kind', 'person_id', 'klass_id', 'id'))

    ad_staff = petl.fromldap(ad_conn(),
                             base_ou='OU=School Staff,OU=Staff Users,OU=Automated Objects,DC=stmonicas,DC=qld,DC=edu,DC=au',
                             query='(&(objectClass=user)(extensionAttribute2=*))',
                             attributes=['employeeID', 'extensionAttribute2'])
    ad_staff = petl.convert(ad_staff, 'extensionAttribute2', str)
    ad_staff = petl.convert(ad_staff, 'employeeID', str)

    teacher_source = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Timetables/{http://www.timetabling.com.au/TDV9}Timetable',
                                  {
                                     'teacher_id': '{http://www.timetabling.com.au/TDV9}TeacherID',
                                     'room_id': '{http://www.timetabling.com.au/TDV9}RoomID',
                                     'period_id': '{http://www.timetabling.com.au/TDV9}PeriodID',
                                     'class_id': '{http://www.timetabling.com.au/TDV9}ClassID'
                                  })
    class_codes = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Classes/{http://www.timetabling.com.au/TDV9}Class',
                               {
                                  'class_id': '{http://www.timetabling.com.au/TDV9}ClassID',
                                  'Class Code': '{http://www.timetabling.com.au/TDV9}Code'
                               })
    teacher_codes = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Teachers/{http://www.timetabling.com.au/TDV9}Teacher', {
                                    'teacher_id': '{http://www.timetabling.com.au/TDV9}TeacherID',
                                    'Teacher Code': '{http://www.timetabling.com.au/TDV9}Code'
                                 })
    day_codes = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Days/{http://www.timetabling.com.au/TDV9}Day', 
                             {
                                'day_id': '{http://www.timetabling.com.au/TDV9}DayID',
                             })
    day_codes = petl.addrownumbers(day_codes)
    day_codes = petl.rename(day_codes, 'row', 'Day No')
    period_codes = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Periods/{http://www.timetabling.com.au/TDV9}Period',
                                {
                                    'period_id': '{http://www.timetabling.com.au/TDV9}PeriodID',
                                    'day_id': '{http://www.timetabling.com.au/TDV9}DayID',
                                    'Period No': '{http://www.timetabling.com.au/TDV9}Number'
                                })
    period_codes = petl.join(period_codes, day_codes, key='day_id')
    room_codes = petl.fromxml(ga_path(), '{http://www.timetabling.com.au/TDV9}Rooms/{http://www.timetabling.com.au/TDV9}Room',
                              {
                                  'room_id': '{http://www.timetabling.com.au/TDV9}RoomID',
                                  'Room Code': '{http://www.timetabling.com.au/TDV9}Code',
                              })
    teacher_source = petl.join(teacher_source, teacher_codes, key='teacher_id')
    teacher_source = petl.join(teacher_source, class_codes, key='class_id')
    teacher_source = petl.join(teacher_source, period_codes, key='period_id')
    teacher_source = petl.join(teacher_source, room_codes, key='room_id')
    teacher_source = petl.cut(teacher_source, 'Room Code', 'Teacher Code', 'Class Code', 'Period No', 'Day No', 'Room Code')

    teacher_source = petl.join(teacher_source, ad_staff, lkey='Teacher Code', rkey='extensionAttribute2')

    teacher_source = petl.wrap(teacher_source)
    teacher_source = (teacher_source
                      .rename('Class Code', 'klass_id')
                      .rename('employeeID', 'person_id')
                      .addfield('kind', 'teacher')
                      .addfieldusingcontext('id', lambda prv, cur, nxt: '{}_{}_{}'.format(cur.person_id, cur.klass_id, cur.kind))
                      .cut('kind', 'person_id', 'klass_id', 'id'))

    enrollments = petl.cat(student_source, teacher_source)
    enrollments = petl.transform.dedup.distinct(enrollments, key='id')

    enrollments = petl.wrap(enrollments)

    # remove ignored courses
    for i in config['ignored_course_patterns']:
        enrollments = enrollments.searchcomplement('klass_id', i)

    enrollments = (enrollments
                   .rename('kind', 'role')
                   .rename('person_id', 'user_id')
                   .rename('klass_id', 'course_id')
                   .addfield('old_course_id', lambda rec: rec['course_id'])
                   .addfield('status', 'active')
                   .addfield('merged', lambda rec: merged_course_lookup(rec['course_id']))
                   .addfield('section_id', lambda rec: '{}_{}'.format(rec['course_id'], term_id) if rec['merged'] else None)
                   .convert('course_id', lambda v, rec: rec['course_id'] if rec['merged'] is None else rec['merged'], pass_row=True)
                   .convert('course_id', lambda v, rec: '{}_{}'.format(rec['course_id'], term_id) if rec['merged'] is None else rec['course_id'], pass_row=True))
    section_enrollments = enrollments
    enrollments = enrollments.cut('course_id', 'user_id', 'role', 'section_id', 'status')

    enrollments.tocsv('csvs/enrollments.csv')

    # SECTIONS
    sections = section_enrollments.distinct('section_id')
    sections = (sections
                .addfield('name', lambda rec: rec['old_course_id'])
                .addfield('status', 'active')
                .cut('section_id', 'course_id', 'name', 'status'))

    sections.tocsv('csvs/sections.csv')

    # find merged and convert to sections
    # get all sections and turn into deduped sections 
    # dump to csv in Canvas format


if __name__ == '__main__':
    main()