"""Canvas Accounts API commands for the Unsync Tool."""

import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
# from unsync.lib.unsync_option import UnsyncOption

from pycanvas.apis.accounts import AccountsAPI

import petl


@unsync.command()
@click.option('--url', required=True, help='Canvas url to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--account-id', required=True, type=int, default=1, help='The Canvas Account to search for courses in.')
@click.option('--recursive/--no-recursive', default=False, help='Recursively search for sub accounts.')
@click.option('--destination', '-d', required=True, help='The destination table that imported Canvas course data will be stored in.')
@pass_data
def get_sub_accounts_of_account(data, url, api_key, account_id, recursive, destination):
    """Import Canvas courses via the REST API and store it in the destination data table."""
    client = AccountsAPI(url, api_key)
    r = client.get_sub_accounts_of_account(account_id, recursive)
    d = petl.fromdicts(r)
    data.set(destination, d)


@unsync.command()
@click.option('--url', required=True, help='Canvas url to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--include', multiple=True, type=click.Choice(['lti_guid', 'registration_settings', 'services']), help='Additional information to include in the API response.')
@click.option('--destination', '-d', required=True, help='The destination table that imported Canvas course data will be stored in.')
@pass_data
def get_accounts(data, url, api_key, include, destination):
    """List accounts visible to the currently logged on user. Only returns data if the user is an account admin."""
    client = AccountsAPI(url, api_key)
    r = client.list_accounts(include)
    d = petl.fromdicts(r)
    data.set(destination, d)


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
def get_courses(data, url, api_key, account_id, by_subaccounts, by_teachers, completed, enrollment_term_id, enrollment_type, hide_enrollmentless_courses, include, published, search_term, state, with_enrollments, destination):
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


@unsync.command()
@click.option('--url', required=True, help='Canvas url to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--source', '-s', required=True, help='The name of the source data table to use.')
@click.option('--account-id-field', required=True, default='id', help='Table field containg the id of the account to edit.')
@click.option('--default-group-storage-quota-mb-field', default='default_group_storage_quota_mb', help='Table field containing the default_group_storage_quota_mb data.')
@click.option('--default-storage-quota-mb-field', default='default_storage_quota_mb', help='Table field containing the default_storage_quota_mb data.')
@click.option('--default-time-zone-field', default='default_time_zone', help='Table field containing the default_time_zone data.')
@click.option('--default-user-storage-quota-mb-field', default='default_user_storage_quota_mb', help='Table field containing the default_user_storage_quota_mb data.')
@click.option('--name-field', default='name', help='Table field containing the name data.')
@click.option('--sis-account-id-field', default='sis_account_id', help='Table field containing the sis_account_id data.')
@click.option('--services-field', default='services', help='Table field containing the services data.')
@click.option('--settings-lock-all-announcements-locked-field', default='settings_lock_all_announcements_locked', help='Table field containing the settings_lock_all_announcements_locked data.')
@click.option('--settings-lock-all-announcements-value-field', default='settings_lock_all_announcements_value', help='Table field containing the settings_lock_all_announcements_value data.')
@click.option('--settings-restrict-student-future-listing-locked-field', default='settings_restrict_student_future_listing_locked', help='Table field containing the settings_restrict_student_future_listing_locked data.')
@click.option('--settings-restrict-student-future-listing-value-field', default='settings_restrict_student_future_listing_value', help='Table field containing the settings_restrict_student_future_listing_value data.')
@click.option('--settings-restrict-student-future-view-locked-field', default='settings_restrict_student_future_view_locked', help='Table field containing the settings_restrict_student_future_view_locked data.')
@click.option('--settings-restrict-student-future-view-value-field', default='settings_restrict_student_future_view_value', help='Table field containing the settings_restrict_student_future_view_value data.')
@click.option('--settings-restrict-student-past-view-locked-field', default='settings_restrict_student_past_view_locked', help='Table field containing the settings_restrict_student_past_view_locked data.')
@click.option('--settings-restrict-student-past-view-value-field', default='settings_restrict_student_past_view_value', help='Table field containing the settings_restrict_student_past_view_value data.')
@pass_data
def update_accounts(data, url, api_key, source,
                    account_id_field,
                    default_group_storage_quota_mb_field,
                    default_storage_quota_mb_field,
                    default_time_zone_field,
                    default_user_storage_quota_mb_field,
                    name_field,
                    sis_account_id_field,
                    services_field,
                    settings_lock_all_announcements_locked_field,
                    settings_lock_all_announcements_value_field,
                    settings_restrict_student_future_listing_locked_field,
                    settings_restrict_student_future_listing_value_field,
                    settings_restrict_student_future_view_locked_field,
                    settings_restrict_student_future_view_value_field,
                    settings_restrict_student_past_view_locked_field,
                    settings_restrict_student_past_view_value_field):
    """Update accounts using information supplied from a table."""
    client = AccountsAPI(url, api_key)
    data_source = data.get(source)
    for row in data_source.dicts():
        kwargs = {}

        if ((default_group_storage_quota_mb_field is not None) and
           (default_group_storage_quota_mb_field in row) and
           (row[default_group_storage_quota_mb_field] is not None)):
            kwargs['account_default_group_storage_quota_mb'] = row[default_group_storage_quota_mb_field]

        if ((default_storage_quota_mb_field is not None) and
           (default_storage_quota_mb_field in row) and
           (row[default_storage_quota_mb_field] is not None)):
            kwargs['account_default_storage_quota_mb'] = row[default_storage_quota_mb_field]

        if ((default_time_zone_field is not None) and
           (default_time_zone_field in row) and
           (row[default_time_zone_field] is not None)):
            kwargs['account_default_time_zone'] = row[default_time_zone_field]

        if ((default_user_storage_quota_mb_field is not None) and
           (default_user_storage_quota_mb_field in row) and
           (row[default_user_storage_quota_mb_field] is not None)):
            kwargs['account_default_user_storage_quota_mb'] = row[default_user_storage_quota_mb_field]

        if ((name_field is not None) and
           (name_field in row) and
           (row[name_field] is not None)):
            kwargs['account_name'] = row[name_field]

        if ((sis_account_id_field is not None) and
           (sis_account_id_field in row) and
           (row[sis_account_id_field] is not None)):
            kwargs['account_sis_account_id'] = row[sis_account_id_field]

        if ((services_field is not None) and
           (services_field in row) and
           (row[services_field] is not None)):
            kwargs['account_services'] = row[services_field]

        if ((settings_lock_all_announcements_locked_field is not None) and
           (settings_lock_all_announcements_locked_field in row) and
           (row[settings_lock_all_announcements_locked_field] is not None)):
            kwargs['account_settings_lock_all_announcements_locked'] = row[settings_lock_all_announcements_locked_field]

        if ((settings_lock_all_announcements_value_field is not None) and
           (settings_lock_all_announcements_value_field in row) and
           (row[settings_lock_all_announcements_value_field] is not None)):
            kwargs['account_settings_lock_all_announcements_value'] = row[settings_lock_all_announcements_value_field]

        if ((settings_restrict_student_future_listing_locked_field is not None) and
           (settings_restrict_student_future_listing_locked_field in row) and
           (row[settings_restrict_student_future_listing_locked_field] is not None)):
            kwargs['account_settings_restrict_student_future_listing_locked'] = row[settings_restrict_student_future_listing_locked_field]

        if ((settings_restrict_student_future_listing_value_field is not None) and
           (settings_restrict_student_future_listing_value_field in row) and
           (row[settings_restrict_student_future_listing_value_field] is not None)):
            kwargs['account_settings_restrict_student_future_listing_value'] = row[settings_restrict_student_future_listing_value_field]

        if ((settings_restrict_student_future_view_locked_field is not None) and
           (settings_restrict_student_future_view_locked_field in row) and
           (row[settings_restrict_student_future_view_locked_field] is not None)):
            kwargs['account_settings_restrict_student_future_view_locked'] = row[settings_restrict_student_future_view_locked_field]

        if ((settings_restrict_student_future_view_value_field is not None) and
           (settings_restrict_student_future_view_value_field in row) and
           (row[settings_restrict_student_future_view_value_field] is not None)):
            kwargs['account_settings_restrict_student_future_view_value'] = row[settings_restrict_student_future_view_value_field]

        if ((settings_restrict_student_past_view_locked_field is not None) and
           (settings_restrict_student_past_view_locked_field in row) and
           (row[settings_restrict_student_past_view_locked_field] is not None)):
            kwargs['account_settings_restrict_student_past_view_locked'] = row[settings_restrict_student_past_view_locked_field]

        if ((settings_restrict_student_past_view_value_field is not None) and
           (settings_restrict_student_past_view_value_field in row) and
           (row[settings_restrict_student_past_view_value_field] is not None)):
            kwargs['account_settings_restrict_student_past_view_value'] = row[settings_restrict_student_past_view_value_field]

        r = client.update_account(row[account_id_field], **kwargs)
