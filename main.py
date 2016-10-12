import petl
import yaml
import ldap3
import re
import csv
import os
import requests
from canvas_api import CanvasAPI
import arrow
import click
from jinja2 import Environment, FileSystemLoader


BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def ga_path():
    return os.path.join(BASE_PATH, 'source/timetable.ptf9')


def ad_conn():
    s1 = ldap3.Server('10.192.81.55')
    s2 = ldap3.Server('10.192.81.54')
    pool = ldap3.ServerPool([s1, s2])
    conn = ldap3.Connection(server=pool,
                            user='CN=LDAPBinder,OU=System,OU=SMCUsers,DC=stmonicas,DC=qld,DC=edu,DC=au',
                            password='5tm0NICa5198SIx')
    return conn


def jinja2_env():
    return Environment(loader=FileSystemLoader(os.path.join(BASE_PATH, 'templates')), trim_blocks=True)


def render(template, data={}):
    env = jinja2_env()
    template = env.get_template(template)
    return template.render(**data)


@click.group()
def cli():
    pass


@click.command()
@click.option('--config', default='./config.yaml', help='Read configuration from this file.')
@click.option('--published-timetable', default='./source/timetable.ptf9', help='The published timetable ')
def generate(config, published_timetable):
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

    # Add users from fake users
    fake_people = config['fake_users']
    for key, fake_person in fake_people.items():
        if fake_person['expires'] is not None:
            try:
                expiry = arrow.get(fake_person['expires'], 'DD/MM/YY')
            except arrow.ParserError:
                continue
            if not arrow.now() < expiry:
                continue
        p = petl.fromdicts([fake_person['data']], header=['user_id', 'login_id', 'first_name', 'last_name', 'full_name', 'email'])
        p = p.addfield('status', 'active')
        people = people.cat(p)

    # Generate CSV Files
    people.tocsv('csvs/users.csv')
    enrollments.tocsv('csvs/enrollments.csv')
    courses.tocsv('csvs/courses.csv')
    sections.tocsv('csvs/sections.csv')
cli.add_command(generate)


@click.command()
@click.option('--config', default='./config.yaml', help='Read configuration from this file.')
def existing_data(config):
    '''Get all existing data for the term and dump it out as CSV.'''
    with open('config.yaml', 'r') as f:
        config = yaml.load(f)

    c = CanvasAPI(config['canvas_url'], config['api_key'])

    terms = c.list_terms_for_account(1)
    terms = dict([(t['sis_term_id'], t['id']) for t in terms['data']['enrollment_terms']])

    try:
        current_term_id = terms[config['term_sis_id']]
    except KeyError:
        raise Exception('Could not find an ID for the term_sis_id')

    users = c.list_users_in_account(1)
    users = petl.fromdicts(users['data'], header=['integration_id', 'login_id', 'sortable_name', 'name', 'short_name', 'sis_user_id', 'sis_import_id', 'sis_login_id', 'id'])
    users = (users
             .cut('sis_user_id', 'login_id', 'sortable_name', 'name')
             .rename({'sis_user_id': 'user_id', 'name': 'full_name'})
             .addfield('last_name', lambda rec: rec['sortable_name'][:rec['sortable_name'].find(',')] if ',' in rec['sortable_name'] else rec['sortable_name'])
             .addfield('first_name', lambda rec: rec['sortable_name'][rec['sortable_name'].find(', ')+2:] if ',' in rec['sortable_name'] else rec['sortable_name'])
             .cutout('sortable_name')
             .addfield('status', 'active'))

    email_map = petl.fromldap(ad_conn(),
                              base_ou='OU=Automated Objects,DC=stmonicas,DC=qld,DC=edu,DC=au',
                              query='(&(objectClass=user)(!(userAccountControl:1.2.840.113556.1.4.803:=2))(userPrincipalName=*stmonicas.qld.edu.au))',
                              attributes=['mail', 'sAMAccountName'])
    email_map = email_map.rename({'mail': 'email', 'sAMAccountName': 'login_id'})

    users = (users
             .join(email_map, key='login_id')
             .cut('user_id', 'login_id', 'first_name', 'last_name', 'full_name', 'email', 'status'))

    accounts = c.list_all_accounts()
    accounts = petl.fromdicts(accounts, header=['integration_id', 'default_time_zone', 'name', 'default_storage_quota_mb', 'workflow_state', 'root_account_id', 'default_group_storage_quota_mb', 'sis_account_id', 'id', 'sis_import_id', 'parent_account_id', 'default_user_storage_quota_mb'])
    accounts = (accounts
                .cut('id', 'sis_account_id')
                .rename('id', 'account_id'))

    courses = c.list_courses_in_account(1, enrollment_term_id=current_term_id)
    courses = petl.fromdicts(courses['data'], header=['calendar', 'id', 'hide_final_grades', 'default_view', 'is_public_to_auth_users', 'root_account_id', 'end_at', 'apply_assignment_group_weights', 'start_at', 'account_id', 'workflow_state', 'public_syllabus', 'grading_standard_id', 'storage_quota_mb', 'enrollment_term_id', 'public_syllabus_to_auth', 'is_public', 'integration_id', 'name', 'restrict_enrollments_to_course_dates', 'time_zone', 'sis_course_id', 'course_code'])
    courses = (courses
               .cut('name', 'course_code', 'sis_course_id', 'account_id', 'id')
               .addfield('term_id', config['term_sis_id'])
               .join(accounts, key='account_id')
               .cutout('account_id')
               .rename({'sis_course_id': 'course_id', 'sis_account_id': 'account_id', 'course_code': 'short_name', 'name': 'long_name'})
               .addfield('status', 'active')
               .cut('course_id', 'short_name', 'long_name', 'term_id', 'status', 'account_id', 'id'))

    enrollments = []
    for course_id in courses.dictlookup('id').keys():
        e = c.list_enrollments_in_course(course_id)
        enrollments.extend(e['data'])
    enrollments = petl.fromdicts(enrollments, header=['associated_user_id', 'course_section_id', 'updated_at', 'grades', 'course_id', 'role_id', 'id', 'user_id', 'sis_user_id', 'root_account_id', 'end_at', 'sis_import_id', 'role', 'enrollment_state', 'type', 'course_integration_id', 'section_integration_id', 'start_at', 'html_url', 'user', 'limit_privileges_to_course_section', 'last_activity_at', 'sis_account_id', 'created_at', 'sis_course_id', 'sis_section_id', 'total_activity_time'])
    sections_courses = enrollments.cut('course_id', 'sis_section_id').select('sis_section_id', lambda v: v is not None).distinct('course_id')  # filter down to just courses with sections
    enrollments = (enrollments
                   .cut('sis_course_id', 'sis_user_id', 'role', 'sis_section_id', 'enrollment_state')
                   .rename({'sis_course_id': 'course_id', 'sis_user_id': 'user_id', 'sis_section_id': 'section_id', 'enrollment_state': 'status'})
                   .convert('role', lambda v: {'StudentEnrollment': 'student', 'TeacherEnrollment': 'teacher'}.get(v, None)))

    # Lookup Sections
    sections = []
    for course_id in sections_courses.dictlookup('course_id').keys():
        s = c.list_sections_in_course(course_id)
        sections.extend(s['data'])
    sections = petl.fromdicts(sections, header=['integration_id', 'start_at', 'name', 'sis_import_id', 'end_at', 'sis_course_id', 'sis_section_id', 'course_id', 'nonxlist_course_id', 'id'])
    sections = (sections
                .cut('sis_section_id', 'sis_course_id', 'name')
                .addfield('status', 'active')
                .rename({'sis_section_id': 'section_id', 'sis_course_id': 'course_id'}))

    users.tocsv('csvs/current/users.csv')

    courses = courses.cut('course_id', 'short_name', 'long_name', 'term_id', 'status', 'account_id')
    courses.tocsv('csvs/current/courses.csv')

    enrollments.tocsv('csvs/current/enrollments.csv')

    sections.tocsv('csvs/current/sections.csv')
cli.add_command(existing_data)

def _pretty_print_canvas_import(import_data):
    pass


@click.command()
@click.option('--config', default='./config.yaml')
def upload_file(config):
    '''Get all existing data for the term and dump it out as CSV.'''
    with open('config.yaml', 'r') as f:
        config = yaml.load(f)

    c = CanvasAPI(config['canvas_url'], config['api_key'])

    r = c.upload_sis_import_file(1, 'csvs/new.zip', diffing_data_set_identifier=config['sync_key'])

    # import pdb;pdb.set_trace()
cli.add_command(upload_file)


@click.command()
@click.option('--config', default='./config.yaml')
@click.option('--show', default=2, help='Number of imports to show')
def list_imports(config, show):
    with open('config.yaml', 'r') as f:
        config = yaml.load(f)

    c = CanvasAPI(config['canvas_url'], config['api_key'])

    r = c.list_sis_imports(1)

    for count, import_data in zip(range(0, len(r['data']['sis_imports'])), r['data']['sis_imports']):
        if count <= show:
            print render('import_info.txt', {'import': import_data})
        else:
            break

cli.add_command(list_imports)


if __name__ == '__main__':
    cli()
