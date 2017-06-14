"""Process all enrollments using the generated courses to produce final enrollment records."""

import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
from unsync.lib.common import select_term_id
import arrow


@unsync.command()
@click.option('--enrollments', required=True, help='Enrollments in Canvas CSV format.')
@click.option('--courses', required=True, help='Courses in Canvas CSV format. Expects the three additional fields lifecycle_type, enrollment_type and old_course_id')
@click.option('--merged-courses', required=True, help='A table containing a mapping of course_ids to merged_course_ids')
@click.option('--terms', required=True, help='The term data to use for lookups. Expected to be in Canvas CSV format. The term_id field is expected to be in the form <lifecycle_type><int>_<year>. Ex TERM1_2017, SEM1_2017, ROT1_2017.')
@click.option('--target-date', help='A date in ISO 8601 format to use for term selection. Defaults to the current date. Used to generate section IDs.')
@click.option('--raw-standard-enrollment-data', help="An optional table name to store processed raw standard enrollment data in.")
@click.option('--raw-merged-enrollment-data', help="An optional table name to store processed raw merged enrollment data in.")
@pass_data
def process_enrollments(data, enrollments, courses, merged_courses, terms, target_date, raw_standard_enrollment_data, raw_merged_enrollment_data):
    """Process the output of the prep commands to filter enrollments to only valid courses and also generate section id\'s suing the enrollment_type field."""
    enrollments_table = data.get(enrollments)
    courses = data.get(courses)
    merged_courses = data.get(merged_courses)
    terms = data.get(terms)

    if not target_date:
        target_date = arrow.now()

    # Common lookup tables
    enrollment_type_lookup = courses.cut('old_course_id', 'enrollment_type')
    course_rename_table = courses.cut('course_id', 'old_course_id')

    # Find out which courses are merged and mark them with their merged course name, all others are marked as NOT_MERGED
    if merged_courses.nrows() > 0:
        enrollments_table = petl.lookupjoin(enrollments_table, merged_courses, key='course_id', missing='NOT_MERGED')
    else:
        # There is no merged_courses data so the lookup will fail. Mark all courses as NOT_MERGED
        enrollments_table = enrollments_table.addfield('merged_course_id', 'NOT_MERGED')
    enrollments_table = enrollments_table.sort('course_id')

    # Split the enrollments into merged and unmerged. Need to treat them differently
    merged_enrollments = enrollments_table.select('merged_course_id', lambda v: v != 'NOT_MERGED')
    standard_enrollments = enrollments_table.select('merged_course_id', lambda v: v == 'NOT_MERGED')

    # == STANDARD COURSE ENROLLMENTS ==
    # Filter out enrollments for courses that do not appear in the courses table.
    course_filter_table = courses.cut('old_course_id').addfield('FILTERED_COURSE', 'FALSE')
    standard_enrollments = petl.hashlookupjoin(standard_enrollments, course_filter_table, lkey='course_id', rkey='old_course_id', missing='TRUE')
    standard_enrollments = standard_enrollments.selecteq('FILTERED_COURSE', 'FALSE').cutout('FILTERED_COURSE')

    # Fill enrollment type
    standard_enrollments = petl.lookupjoin(standard_enrollments, enrollment_type_lookup, lkey='course_id', rkey='old_course_id')

    # Change the course_id of the enrollments to the new style
    standard_enrollments = standard_enrollments.rename('course_id', 'old_course_id')
    standard_enrollments = petl.hashlookupjoin(standard_enrollments, course_rename_table, key='old_course_id', missing='BROKEN_COURSE')
    # TODO: Save the broken courses somewhere and then takes stpes to fix them.

    # Generate the section ids
    def standard_course_section_id_generator(v, rec):
        """Standard course section ids will be the original_course_id + enrollment_type->term_id."""
        term_id = select_term_id(target_date, rec.enrollment_type, terms)
        return '{}_{}'.format(rec.old_course_id, term_id)

    standard_enrollments = standard_enrollments.convert('section_id', standard_course_section_id_generator, pass_row=True)

    # Store raw processed enrollment data if raw_standard_enrollment_data was passed
    if raw_standard_enrollment_data is not None:
        data.set(raw_standard_enrollment_data, standard_enrollments)

    # Remove extraneous fields
    standard_enrollments = standard_enrollments.cut('course_id', 'root_account', 'user_id', 'role', 'role_id', 'section_id', 'status', 'associated_user_id')

    all_enrollments = standard_enrollments

    # == MERGED COURSE ENROLLMENTS ==
    if merged_courses.nrows() > 0:
        # Only process merged enrollments if there is merged_courses data
        # Fill the enrollment type
        merged_enrollments = petl.lookupjoin(merged_enrollments, enrollment_type_lookup, lkey='merged_course_id', rkey='old_course_id')

        # Save old course id and fill new course id
        merged_enrollments = merged_enrollments.rename('course_id', 'old_course_id')
        merged_enrollments = petl.hashlookupjoin(merged_enrollments, course_rename_table, lkey='merged_course_id', rkey='old_course_id')

        # Generate the section IDs
        def merged_course_section_id_generator(v, rec):
            term_id = select_term_id(target_date, rec.enrollment_type, terms)
            return '{}_{}_{}'.format(rec.old_course_id, rec.merged_course_id, term_id)

        merged_enrollments = merged_enrollments.convert('section_id', merged_course_section_id_generator, pass_row=True)

        # Store raw processed enrollment data if raw_merged_enrollment_data was passed
        if raw_merged_enrollment_data is not None:
            data.set(raw_merged_enrollment_data, merged_enrollments)

        # Remove extraneous fields
        merged_enrollments = merged_enrollments.cut('course_id', 'root_account', 'user_id', 'role', 'role_id', 'section_id', 'status', 'associated_user_id')

        all_enrollments = all_enrollments.cat(merged_enrollments)

    # TODO: There is an issue here with raw_merged_enrollment_data never being set if there is no merged_courses data. I think a set of headers should be generated at the very least.

    data.set(enrollments, all_enrollments)

command = process_enrollments