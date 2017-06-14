"""Import courses from the specified Canvas instance into a local data table."""
import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync

from pycanvas.apis.accounts import AccountsAPI

import petl


@unsync.command()
@click.option('--url', required=True, help='Canvas url to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--account-id', type=int, default=1, help='The Canvas Account to search for courses in.')
@click.option('--by-subaccounts', type=int, multiple=True, default=None, help='Only return courses which are part of the given subaccount ids.')
@click.option('--by-teachers', type=int, multiple=True, default=None, help='Only return courses which are taught by the given teacher ids.')
@click.option('--completed/--no-completed', default=None, help='If present and true only return courses whose state is completed. If false exclude completed courses.')
@click.option('--enrollment-term-id', default=None, help='If given only return courses from the given term.')
@click.option('--enrollment-type', default=None, type=click.Choice(["teacher", "student", "ta", "observer", "designer"]), help='Only return courses with at least one of the given enrollments.')
@click.option('--hide-enrollmentless-courses/--no-hide-enrollmentless-courses', default=None)
@click.option('--include', type=click.Choice(["syllabus_body", "term", "course_progress", "storage_quota_used_mb", "total_students", "teachers"]))
@click.option('--published/--no-published', default=None)
@click.option('--search_term', default=None, type=str)
@click.option('--state', default=None, type=click.Choice(["created", "claimed", "available", "completed", "deleted", "all"]))
@click.option('--with-enrollments/--no-with-enrollments', default=None)
@click.option('--destination', '-d', required=True, help='The destination table that imported Canvas course data will be stored in.')
@pass_data
def canvas_import_courses(data, url, api_key, account_id, by_subaccounts, by_teachers, completed, enrollment_term_id, enrollment_type, hide_enrollmentless_courses, include, published, search_term, state, with_enrollments, destination):
    """Import Canvas courses via the REST API and store it in the destination data table."""
    client = AccountsAPI(url, api_key)
    r = client.list_active_courses_in_account(account_id,
                                              by_subaccounts=by_subaccounts,
                                              by_teachers=by_teachers,
                                              completed=completed,
                                              enrollment_term_id=enrollment_term_id,
                                              enrollment_type=enrollment_type,
                                              hide_enrollmentless_courses=hide_enrollmentless_courses,
                                              include=include,
                                              published=published,
                                              search_term=search_term,
                                              state=state,
                                              with_enrollments=with_enrollments)
    d = petl.fromdicts(r)
    data.set(destination, d)

command = canvas_import_courses
