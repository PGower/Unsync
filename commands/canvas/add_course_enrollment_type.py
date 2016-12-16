"""Add an enrollment type to each course.

Applied using a 3 step process.
1. All courses from the specifed courses table that do not have an existing value in the enrollment_type field are assigned a default enrollment value (default_enrollment_type)
2. All courses are itierated through, any course that has a course_id_field value that matches a regex from the enrollment_defaults table has its enrollment_type field set to that new value.
3. All courses are iterated and any course that has a course_id field that exactly matches one in the enrollment_mappings table has its enrollment_type field set to the new value.
"""

import click
import re
from lib.unsync_data import pass_data
from lib.unsync_commands import unsync


@unsync.command()
@click.option('--courses', '-c', required=True, type=unicode, help='The table containing courses data.')
@click.option('--course-id-field', required=True, type=unicode, default='course_id', help='The field name for the courses id. Defaults to Canvas standard course_id.')
@click.option('--default-enrollment-value', default=u'TERM', type=click.Choice(['TERM', 'SEM', 'ROT', 'YEAR']), help='The default lifecycle to assign all courses. If not changed in the enrollment-defaults table or the enrollment-mappings table this will stick.')
@click.option('--enrollment-defaults', required=True, default='enrollment_defaults', type=unicode, help='A two column (regex,value) table of regexes and enrollment values (ROT,TERM,SEM,YEAR). Any course_id that matches the regex will be updated with the new enrollment value.')
@click.option('--enrollment-mappings', required=True, default='enrollment_mappings', type=unicode, help='A two column (id,value) table of course_id and enrollment values (ROT,TERM,SEM,YEAR). Any course_id that exactly matches will be updated with the new enrollment value.')
@pass_data
def add_course_enrollment_type(data, courses, course_id_field, default_enrollment_value, enrollment_defaults, enrollment_mappings):
    """Apply the course enrollment type value."""
    courses_table = data.get(courses)
    enrollment_defaults = data.get(enrollment_defaults)
    enrollment_mappings = data.get(enrollment_mappings)

    if 'enrollment_type' in courses_table.header():
        courses_table = courses_table.convert('enrollment_type', lambda v: default_enrollment_value if v is None else v)
    else:
        courses_table = courses_table.addfield('enrollment_type', default_enrollment_value)

    # Lookup and set defaults from the enrollments_default table. Regex based.
    enrollment_default_lookup = enrollment_defaults.cut('regex', 'value')  # Make sure the ordering is correct.
    enrollment_default_lookup = enrollment_default_lookup.listoftuples()
    enrollment_default_lookup = dict([(re.compile(i[0]), i[1]) for i in enrollment_default_lookup][1:])

    def enrollment_default_lookup_func(v, rec):
        for r, nv in enrollment_default_lookup.items():
            if r.match(getattr(rec, course_id_field)):
                return nv
        return v

    courses_table = courses_table.convert('enrollment_type', enrollment_default_lookup_func, pass_row=True)

    enrollment_mapping_lookup = enrollment_mappings.cut('id', 'value')
    enrollment_mapping_lookup = dict(enrollment_mapping_lookup.listoftuples()[1:])

    def enrollment_mapping_lookup_func(v, rec):
        cid = getattr(rec, course_id_field)
        if cid in enrollment_mapping_lookup:
            return enrollment_mapping_lookup[cid]
        else:
            return v

    courses_table = courses_table.convert('enrollment_type', enrollment_mapping_lookup_func, pass_row=True)

    data.set(courses, courses_table)

command = add_course_enrollment_type
