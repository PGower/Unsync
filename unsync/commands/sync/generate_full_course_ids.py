"""Generate the full Canvas course_id by looking at the course lifecycle_type and appending the sis_id of the appropriate time period."""

import click
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
from unsync.lib.common import select_term_id
import arrow


@unsync.command()
@click.option('--courses', required=True, type=unicode, help='The source courses table containing courses to be merged.')
@click.option('--course-id-field', required=True, type=unicode, default='course_id', help='The field name for the courses id. Defaults to Canvas standard course_id.')
@click.option('--terms', required=True, help='The term data to use for lookups. Expected to be in Canvas CSV format. The term_id field is expected to be in the form <lifecycle_type><int>_<year>. Ex TERM1_2017, SEM1_2017, ROT1_2017.')
@click.option('--target-date', help='A date in ISO 8601 format to use for term selection. Defaults to the current date. Used to generate course IDs')
@pass_data
def generate_full_course_ids(data, courses, course_id_field, terms, target_date):
    """Generate full course_id\'s for the given courses using the value of the lifecycle_type field to append a correct term id."""
    course_table = data.get(courses)
    terms = data.get(terms)

    if not target_date:
        target_date = arrow.now()

    def term_lookup_func(v, rec):
        term_id = select_term_id(target_date, rec.lifecycle_type, terms)
        return '{}_{}'.format(getattr(rec, course_id_field), term_id)

    course_table = course_table.convert(course_id_field, term_lookup_func, pass_row=True)

    data.set(courses, course_table)

command = generate_full_course_ids
