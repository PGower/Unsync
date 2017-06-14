"""Process all enrollments using the generated courses to produce final enrollment records."""

import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--enrollments', required=True, help='Generated Enrollment information in Canvas CSV format.')
@click.option('--users', required=True, help='Generated User information in Canvas CSV format.')
@click.option('--shadow-users', required=True, help='Shadow user source data. Requires source_user_id, shadow_user_id, role.')
@click.option('--shadow-user-source-id-field', required=True, default='source_user_id', help='The field containing the source user ID.')
@click.option('--shadow-user-target-id-field', required=True, default='target_user_id', help='The field containing the target user ID.')
@click.option('--shadow-user-role-field', required=True, default='role', help='The field containing the target user role. Will replace the source user role in copied enrollments.')
@click.option('--destination', '-d', help='The destination to store new enrollments in.')
@pass_data
def process_shadow_users(data, enrollments, users, shadow_users, shadow_user_source_id_field, shadow_user_target_id_field, shadow_user_role_field, destination):
    """Copy enrollments for source users and add them for shadow users, replacing the role as we go."""
    shadow_users = data.get(shadow_users)
    enrollments_data = data.get(enrollments)
    users_data = data.get(users)

    shadow_enrollments = petl.wrap([[]])

    user_ids = set(users_data.values('user_id'))

    # Filter the shadow users table, remove any rows where the source_user or target_user do not exist in the users_data table.
    for row in shadow_users.dicts():
        source_id = row[shadow_user_source_id_field]
        if source_id not in user_ids:
            click.secho('Unable to find source user id: {}. This row of the shadow users table will not be processed.'.format(source_id), fg='red')
            continue
        target_id = row[shadow_user_target_id_field]
        if target_id not in user_ids:
            click.secho('Unable to find target user id: {}. This row of the shadow users table will not be processed.'.format(target_id), fg='red')
            continue
        new_role = row[shadow_user_role_field]

        source_enrollments = enrollments_data.select('user_id', lambda v, source_id=source_id: v == source_id)
        target_enrollments = (source_enrollments
                              .convert('user_id', lambda v, target_id=target_id: target_id)
                              .convert('role', lambda v, role=new_role: role))
        shadow_enrollments = shadow_enrollments.cat(target_enrollments)
        click.secho('Sucessfully copied {} enrollments from user: {} to user: {}'.format(target_enrollments.nrows(), source_id, target_id), fg='green')

    enrollments_data = enrollments_data.cat(shadow_enrollments)

    if destination is not None:
        data.set(destination, enrollments_data)
    else:
        data.set(enrollments, enrollments_data)

command = process_shadow_users