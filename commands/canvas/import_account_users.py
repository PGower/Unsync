"""Import users from the specified Canvas instance into a local data table."""
from __future__ import absolute_import
import click

from lib.common import pass_data, extract_api_data
from lib.canvas_api import CanvasAPI


@click.command()
@click.option('--instance', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--account-id', type=int, default=1, help='The Canvas Account to search for courses in.')
@click.option('--destination', '-d', required=True, help='The destination table that imported Canvas course data will be stored in.')
@pass_data
def canvas_import_account_users(data, instance, api_key, account_id, destination):
    """Import User information from the Canvas instance via the REST API and store it in the destination table."""
    client = CanvasAPI(instance, api_key)
    r = client.list_users_in_account(account_id)
    if r['response'].status_code == 200:
        header = ['integration_id',
                  'login_id',
                  'sortable_name',
                  'name',
                  'short_name',
                  'sis_user_id',
                  'sis_import_id',
                  'sis_login_id',
                  'id',
                  'email']
        t = extract_api_data(r, header)
        data.cat(destination, t)


command = canvas_import_account_users
