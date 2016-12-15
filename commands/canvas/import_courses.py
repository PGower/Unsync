"""Import courses from the specified Canvas instance into a local data table."""
import click

from lib.unsync_data import pass_data
from lib.common import extract_api_data
from lib.canvas_api import CanvasAPI


@click.command()
@click.option('--instance', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--account-id', type=int, default=1, help='The Canvas Account to search for courses in.')
@click.option('--term-id', type=int, help='Return only courses that are part of the given Canvas Term.')
@click.option('--destination', '-d', required=True, help='The destination table that imported Canvas course data will be stored in.')
@pass_data
def canvas_import_courses(data, instance, api_key, account_id, term_id, destination):
    """Import Canvas courses via the REST API and store it in the destination data table."""
    client = CanvasAPI(instance, api_key)
    if term_id:
        r = client.list_courses_in_account(account_id, enrollment_term_id=term_id)
    else:
        r = client.list_courses_in_account(account_id)
        header = ['id',
                  'hide_final_grades',
                  'default_view',
                  'is_public_to_auth_users',
                  'root_account_id',
                  'end_at',
                  'apply_assignment_group_weights',
                  'start_at',
                  'account_id',
                  'workflow_state',
                  'public_syllabus',
                  'grading_standard_id',
                  'storage_quota_mb',
                  'enrollment_term_id',
                  'public_syllabus_to_auth',
                  'is_public',
                  'integration_id',
                  'name',
                  'restrict_enrollments_to_course_dates',
                  'time_zone',
                  'sis_course_id',
                  'course_code']
        t = extract_api_data(r, header)
        data.cat(destination, t)

command = canvas_import_courses
