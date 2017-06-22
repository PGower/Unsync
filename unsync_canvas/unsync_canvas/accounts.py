"""Canvas Accounts API commands for the Unsync Tool."""

import unsync

from pycanvas.apis.accounts import AccountsAPI

import petl


@unsync.command()
@unsync.option('--url', required=True, help='Canvas url to use. Usually something like <schoolname>.instructure.com.')
@unsync.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@unsync.option('--account-id', required=True, type=int, default=1, help='The Canvas Account to search for courses in.')
@unsync.option('--recursive/--no-recursive', default=False, help='Recursively search for sub accounts.')
@unsync.option('--destination', '-d', required=True, help='The destination table that imported Canvas course data will be stored in.')
def get_sub_accounts_of_account(data, url, api_key, account_id, recursive, destination):
    """Import Canvas courses via the REST API and store it in the destination data table."""
    client = AccountsAPI(url, api_key)
    r = client.get_sub_accounts_of_account(account_id, recursive)
    d = petl.fromdicts(r)
    data.set(destination, d)


@unsync.command()
@unsync.option('--url', required=True, help='Canvas url to use. Usually something like <schoolname>.instructure.com.')
@unsync.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@unsync.option('--include', multiple=True, type=unsync.Choice(['lti_guid', 'registration_settings', 'services']), help='Additional information to include in the API response.')
@unsync.option('--destination', '-d', required=True, help='The destination table that imported Canvas course data will be stored in.')
def get_accounts(data, url, api_key, include, destination):
    """List accounts visible to the currently logged on user. Only returns data if the user is an account admin."""
    client = AccountsAPI(url, api_key)
    r = client.list_accounts(include)
    d = petl.fromdicts(r)
    data.set(destination, d)


@unsync.command()
@unsync.option('--url', required=True, help='Canvas url to use. Usually something like <schoolname>.instructure.com.')
@unsync.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@unsync.option('--account-id', type=int, default=1, help='The Canvas Account to search for courses in.')
@unsync.option('--by-subaccounts', type=int, multiple=True, default=None, help='Only return courses which are part of the given subaccount ids.')
@unsync.option('--by-teachers', type=int, multiple=True, default=None, help='Only return courses which are taught by the given teacher ids.')
@unsync.option('--completed/--no-completed', default=None, help='If present and true only return courses whose state is completed. If false exclude completed courses.')
@unsync.option('--enrollment-term-id', default=None, help='If given only return courses from the given term.')
@unsync.option('--enrollment-type', default=None, type=unsync.Choice(["teacher", "student", "ta", "observer", "designer"]), help='Only return courses with at least one of the given enrollments.')
@unsync.option('--hide-enrollmentless-courses/--no-hide-enrollmentless-courses', default=None)
@unsync.option('--include', type=unsync.Choice(["syllabus_body", "term", "course_progress", "storage_quota_used_mb", "total_students", "teachers"]))
@unsync.option('--published/--no-published', default=None)
@unsync.option('--search_term', default=None, type=str)
@unsync.option('--state', default=None, type=unsync.Choice(["created", "claimed", "available", "completed", "deleted", "all"]))
@unsync.option('--with-enrollments/--no-with-enrollments', default=None)
@unsync.option('--destination', '-d', required=True, help='The destination table that imported Canvas course data will be stored in.')
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
@unsync.option('--url', required=True, help='Canvas url to use. Usually something like <schoolname>.instructure.com.')
@unsync.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@unsync.option('--source', '-s', required=True, help='The name of the source data table to use.')
@unsync.option('--account-id-field', required=True, default='id', help='Table field containg the id of the account to edit.')
@unsync.option('--default-group-storage-quota-mb-field', default='default_group_storage_quota_mb', help='Table field containing the default_group_storage_quota_mb data.')
@unsync.option('--default-storage-quota-mb-field', default='default_storage_quota_mb', help='Table field containing the default_storage_quota_mb data.')
@unsync.option('--default-time-zone-field', default='default_time_zone', help='Table field containing the default_time_zone data.')
@unsync.option('--default-user-storage-quota-mb-field', default='default_user_storage_quota_mb', help='Table field containing the default_user_storage_quota_mb data.')
@unsync.option('--name-field', default='name', help='Table field containing the name data.')
@unsync.option('--sis-account-id-field', default='sis_account_id', help='Table field containing the sis_account_id data.')
@unsync.option('--services-field', default='services', help='Table field containing the services data.')
@unsync.option('--settings-lock-all-announcements-locked-field', default='settings_lock_all_announcements_locked', help='Table field containing the settings_lock_all_announcements_locked data.')
@unsync.option('--settings-lock-all-announcements-value-field', default='settings_lock_all_announcements_value', help='Table field containing the settings_lock_all_announcements_value data.')
@unsync.option('--settings-restrict-student-future-listing-locked-field', default='settings_restrict_student_future_listing_locked', help='Table field containing the settings_restrict_student_future_listing_locked data.')
@unsync.option('--settings-restrict-student-future-listing-value-field', default='settings_restrict_student_future_listing_value', help='Table field containing the settings_restrict_student_future_listing_value data.')
@unsync.option('--settings-restrict-student-future-view-locked-field', default='settings_restrict_student_future_view_locked', help='Table field containing the settings_restrict_student_future_view_locked data.')
@unsync.option('--settings-restrict-student-future-view-value-field', default='settings_restrict_student_future_view_value', help='Table field containing the settings_restrict_student_future_view_value data.')
@unsync.option('--settings-restrict-student-past-view-locked-field', default='settings_restrict_student_past_view_locked', help='Table field containing the settings_restrict_student_past_view_locked data.')
@unsync.option('--settings-restrict-student-past-view-value-field', default='settings_restrict_student_past_view_value', help='Table field containing the settings_restrict_student_past_view_value data.')
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
