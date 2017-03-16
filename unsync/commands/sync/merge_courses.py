"""Canvas specific command to merge specified courses together."""
from __future__ import unicode_literals

import click
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--courses', required=True, type=str, help='The source courses table containing courses to be merged.')
@click.option('--course-id-field', required=True, type=str, default='course_id', help='The field name for the courses id. Defaults to Canvas standard course_id.')
@click.option('--course-name-field', required=True, type=str, default='long_name', help='The field name for the course name. Defaults to Canvas standard long_name.')
@click.option('--merge-data', required=True, type=str, help='Table containing pairs of Merged Name -> Source Name mappings.')
@click.option('--save-removed-courses/--no-save-removed-courses', default=True, help='If True then save the removed course data in a table specificed by removed-courses-destination.')
@click.option('--removed-courses-destination', default='removed_merged_course_data', help='The destination table for any courses that were removed as part of the merge.')
@pass_data
def merge_courses(data, courses, course_id_field, course_name_field, merge_data, save_removed_courses, removed_courses_destination):
    """Merge courses acording to pairs in the merge table. If save-removed-courses is set then save the removed courses to a table named removed-courses-destination"""
    merge_data = data.get(merge_data)
    courses_table = data.get(courses)

    # Turn the merge data into a dict where source_course_name is the key and merged_course_name is the value.
    merge_mappings = merge_data.lookupone('source_id', 'merged_id')

    # Work out which source courses need to be removed and remove them
    source_courses_to_remove = courses_table.select(course_id_field, lambda v: v in merge_mappings)
    source_course_ids_to_remove = source_courses_to_remove.columns()[course_id_field]
    courses_table = courses_table.select(course_id_field, lambda v: v not in source_course_ids_to_remove)

    # Save the removed courses to a seperate table for later use
    if save_removed_courses and merge_data.nrows() > 0:
        source_courses_to_remove = (source_courses_to_remove
                                    .lookupjoin(merge_data, lkey='course_id', rkey='source_id')
                                    # .cut('course_id', 'merged_id')
                                    .rename('merged_id', 'merged_course_id'))
        data.set(removed_courses_destination, source_courses_to_remove)

    # Work out which merge courses I need to create, this will be any merge course that has a source course to be removed
    merge_courses_to_create = merge_data.select('source_id', lambda v: v in source_course_ids_to_remove)
    new_merge_course_data = merge_courses_to_create.cut('merged_id', 'merged_name')
    new_merge_course_data = new_merge_course_data.rename({'merged_id': course_id_field, 'merged_name': course_name_field})
    new_merge_course_data = new_merge_course_data.distinct()
    courses_table = courses_table.cat(new_merge_course_data)

    data.set(courses, courses_table)

command = merge_courses
