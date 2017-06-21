import click
from pycanvas.apis.logins import LoginsAPI
from pycanvas.apis.base import CanvasAPIError

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
@click.option('--results-table', default="_results", help='Data table that will be filled with the results of the edit logins operation.')
@pass_data
def update_user_logins(data, url, api_key, source, account_id_field, login_id_field, unique_id_field, password_field, sis_user_id_field, integration_id_field, results_table):
    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    client = LoginsAPI(url, api_key)

    source = data.get(source)

    debug = data.config.debug

    results = []

    for row in petl.dicts(source):
        account_id = row[account_id_field]
        login_id = row[login_id_field]

        kwargs = {}
        if unique_id_field is not None and row[unique_id_field] is not None:
            kwargs['login_unique_id'] = row[unique_id_field]
        if password_field is not None and row[password_field] is not None:
            kwargs['login_password'] = row[password_field]
        if sis_user_id_field is not None and row[sis_user_id_field] is not None:
            kwargs['login_sis_user_id'] = row[sis_user_id_field]
        if integration_id_field is not None and row[integration_id_field] is not None:
            kwargs['login_integration_id'] = row[integration_id_field]

        try:
            r = client.edit_user_login(login_id, account_id, **kwargs)
            click.secho('Successfully updated login: {} with data: {}'.format(login_id, str(kwargs)), fg='green')

            if results_table:
                row['_data'] = str(kwargs)
                row['_response_status'] = r
                row['_response_content'] = r
                results.append(row)

            if debug:
                click.secho(str(r), fg='yellow')
        except (CanvasAPIError) as e:
            click.secho('Failed updating login: {} with data: {}'.format(login_id, str(kwargs)), fg='red')
            click.secho('Response Status: {} Response Reason: {}'.format(e.response.status_code, e.response.content), fg='red')

            if results_table:
                row['_data'] = str(kwargs)
                row['_response_status'] = e.response.status_code
                row['_response_content'] = e.response.content
                results.append(row)

    results = petl.fromdicts(results)
    data.cat(results_table, results)


@unsync.command()
@click.option('--url', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--account-id', default=1, help='The Canvas account to access. This is usually the main account.')
@click.option('--destination', '-d', required=True, help='The destination data table for the retieved data.')
@pass_data
def get_account_logins(data, url, api_key, account_id, destination):
    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    client = LoginsAPI(url, api_key)
    r = client.list_user_logins_accounts(account_id)
    d = petl.fromdicts(r)
    data.set(destination, d)


@unsync.command()
@click.option('--url', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--user-data', required=True, help='Name of a data table containing Canvas user IDs')
@click.option('--user-id-field', required=True, default='id', help='Name of the column that contains Canvas user IDs')
@click.option('--destination', '-d', required=True, help='The destination table for all retrieved data.')
@pass_data
def get_user_logins(data, url, api_key, user_data, user_id_field, destination):

    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    user_data = data.get(user_data)
    user_data = user_data.dicts()

    login_data = []

    debug = data.config.debug

    client = LoginsAPI(url, api_key)
    for user in user_data:
        try:
            r = client.list_user_logins_users(user[user_id_field])
            if debug:
                click.secho('Retrieved {} Canvas Logins for Canvas User ID: {}'.format(len(r), user[user_id_field]), fg='green')
        except CanvasAPIError:
            click.secho('Unable to retrieve Canvas Login information for Canvas User ID: {}'.format(user[user_id_field]), fg='red')
        for login in r:
            login_data.append(login)

    login_data = petl.fromdicts(login_data)
    data.set(destination, login_data)
