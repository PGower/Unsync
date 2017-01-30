from unsync.lib.canvas_api import CanvasAPI
import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
import petl


@unsync.command()
@click.option('--url', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--source', '-s', required=True, help='The name of the source data table to use.')
@click.option('--account-id-field', default='account_id', help='The field containing the account this user belongs to.')
@click.option('--login-id-field', default='login_id', help='The field containing the login_id to change.')
@click.option('--unique-id-field', help='The field containing the new unique_id for the user. If not specified this will be skipped. If specified but the value is None will be skipped for that user.')
@click.option('--password-field', help='The field containing the new password for the user. If not specified this will be skipped. If specified but the value is None will be skipped for that user.')
@click.option('--sis-user-id-field', help='The field containing the new sis_user_id for the user. If not specified this will be skipped. If specified but the value is None will be skipped for that user.')
@click.option('--integration-id-field', help='The field containing the new integration_id for the user. If not specified this will be skipped. If specified but the value is None will be skipped for that user.')
@pass_data
def edit_user_login(data, url, api_key, source, account_id_field, login_id_field, unique_id_field, password_field, sis_user_id_field, integration_id_field):
    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    client = CanvasAPI(url, api_key)
    
    r = client.list_users_for_account(account_id, search_term)
    data.cat(destination, petl.fromdicts(r))


command = edit_user_login
