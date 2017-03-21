"""Sync specific command to filter courses based on both regex patterns and also direct matching."""
from __future__ import unicode_literals

import click
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
import re


@unsync.command()
@click.option('--courses', required=True, type=str, help='The source courses to filter.')
@click.option('--course-id-field', required=True, type=str, default='course_id', help='The field name for the courses id. Defaults to Canvas standard course_id.')
@click.option('--filter-patterns', help='Name of a table containing a list of patterns for courses that will be removed.')
@click.option('--filter-pattern-field', required=True, default='regex', help='Name of the field contining patterns to be matched.')
@click.option('--filter-course-ids', help='Name of a table containing course codes to remove from the source data. Uses exact matching.')
@click.option('--filter-course-id-field', required=True, default='course_id', help='Name of the field in the filter-codes table containg the course id.')
@pass_data
def filter_courses(data, courses, course_id_field, filter_patterns, filter_pattern_field, filter_course_ids, filter_course_id_field):
    """Assign accounts to courses where the course id matches the account regex."""
    courses_table = data.get(courses)

    # Match patterns first and remove any matches.
    if filter_patterns:
        filter_patterns = data.get(filter_patterns)
        for filter_pattern in filter_patterns.dicts():
            courses_table = courses_table.searchcomplement(course_id_field, filter_pattern[filter_pattern_field])

    # Match specific course_ids and remove
    if filter_course_ids:
        filter_course_ids = data.get(filter_course_ids)
        course_ids_to_filter = [i[filter_course_id_field] for i in filter_course_ids.dicts()]
        courses_table = courses_table.select(lambda rec, course_id_field=course_id_field, course_ids_to_filter=course_ids_to_filter: rec[course_id_field] not in course_ids_to_filter)

    data.set(courses, courses_table)

command = filter_courses
