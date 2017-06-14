"""Update accounts information."""

import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync

from pycanvas.apis.accounts import AccountsAPI


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
def canvas_list_accounts(data, url, api_key, source,
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
        import pdb; pdb.set_trace()

command = canvas_list_accounts
