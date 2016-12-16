"""Apply the course lifecycle type to all of the current courses.

Lifecycle is assigned in 3 steps.
1. All courses from the specifed courses table that do not have an existing value in the lifecycle_value field are assigned a default lifecycle value (default_lifecycle_value)
2. All courses are itierated through, any course that has a course_id_field value that matches a regex from the lifecycle_defaults table has its lifecycle_value field set to that new value.
3. All courses are iterated and any course that has a course_id field that exactly matches one in the lifecycle_mappings table has its lifecycle_value field set to the new value.
"""

import click
import re
from lib.unsync_data import pass_data
from lib.unsync_commands import unsync


@unsync.command()
@click.option('--courses', '-c', required=True, type=unicode, help='The table containing courses data.')
@click.option('--course-id-field', required=True, type=unicode, default='course_id', help='The field name for the courses id. Defaults to Canvas standard course_id.')
@click.option('--default-lifecycle-value', default=u'TERM', type=click.Choice(['TERM', 'SEM', 'ROT', 'YEAR']), help='The default lifecycle to assign all courses. If not changed in the lifecycle-defaults table or the lifecycle-mappings table this will stick.')
@click.option('--lifecycle-defaults', required=True, default='lifecycle_defaults', type=unicode, help='A two column (regex,value) table of regexes and lifecycle values (ROT,TERM,SEM,YEAR). Any course_id that matches the regex will be updated with the new lifecycle value.')
@click.option('--lifecycle-mappings', required=True, default='lifecycle_mappings', type=unicode, help='A two column (id,value) table of course_id and lifecycle values (ROT,TERM,SEM,YEAR). Any course_id that exactly matches will be updated with the new lifecycle value.')
@pass_data
def add_course_lifecycle(data, courses, course_id_field, default_lifecycle_value, lifecycle_defaults, lifecycle_mappings):
    """Apply the course lifecycle_value."""
    courses_table = data.get(courses)
    lifecycle_defaults = data.get(lifecycle_defaults)
    lifecycle_mappings = data.get(lifecycle_mappings)

    if 'lifecycle_type' in courses_table.header():
        # Start by setting all of the existing lifeycle_type fields values to the default unless they are already set, then leave.
        courses_table = courses_table.convert('lifecycle_type', lambda v: default_lifecycle_value if v is None else v)
    else:
        courses_table = courses_table.addfield('lifecycle_type', default_lifecycle_value)

    # Lookup and set defaults from the lifecycle_defaults table. Regex based.
    lifecycle_default_lookup = lifecycle_defaults.cut('regex', 'value')  # Make sure the ordering is correct.
    lifecycle_default_lookup = lifecycle_default_lookup.listoftuples()
    lifecycle_default_lookup = dict([(re.compile(i[0]), i[1]) for i in lifecycle_default_lookup][1:])

    def lifecycle_default_lookup_func(v, rec):
        for r, nv in lifecycle_default_lookup.items():
            if r.match(getattr(rec, course_id_field)):
                return nv
        return v

    # Lookup and set values from the lifecycle_mappings table. Extact matches.
    courses_table = courses_table.convert('lifecycle_type', lifecycle_default_lookup_func, pass_row=True)

    lifecycle_mapping_lookup = lifecycle_mappings.cut('id', 'value')
    lifecycle_mapping_lookup = lifecycle_mapping_lookup.listoftuples()
    lifecycle_mapping_lookup = dict(lifecycle_mapping_lookup[1:])

    def lifecycle_mapping_lookup_func(v, rec):
        cid = getattr(rec, course_id_field)
        if cid in lifecycle_mapping_lookup:
            return lifecycle_mapping_lookup[cid]
        else:
            return v

    courses_table = courses_table.convert('lifecycle_type', lifecycle_mapping_lookup_func, pass_row=True)

    data.set(courses, courses_table)

command = add_course_lifecycle
