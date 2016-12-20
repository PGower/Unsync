"""Assign a term_id to courses using the lifecycle_type."""

import click
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
from unsync.lib.common import select_term_id
import arrow


@unsync.command()
@click.option('--courses', required=True, type=unicode, help='The source courses table containing courses to be merged.')
@click.option('--terms', required=True, help='The term data to use for lookups. Expected to be in Canvas CSV format. The term_id field is expected to be in the form <lifecycle_type><int>_<year>. Ex TERM1_2017, SEM1_2017, ROT1_2017.')
@click.option('--target-date', help='A date in ISO 8601 format to use for term selection. Defaults to the current date. Used to generate course IDs')
@pass_data
def assign_course_term_id(data, courses, terms, target_date):
    """Generate full course_id\'s for the given courses using the value of the lifecycle_type field to append a correct term id."""
    course_table = data.get(courses)
    terms = data.get(terms)

    if not target_date:
        target_date = arrow.now()

    if 'term_id' in course_table.header():
        course_table = course_table.convert('term_id', lambda v, rec: select_term_id(target_date, rec.lifecycle_type, terms), pass_row=True)
    else:
        course_table = course_table.addfield('term_id', lambda rec: select_term_id(target_date, rec.lifecycle_type, terms))

    data.set(courses, course_table)

command = assign_course_term_id
