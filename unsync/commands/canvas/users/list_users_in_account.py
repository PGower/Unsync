import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync

from pycanvas.apis.users import UsersAPI

import petl


@unsync.command()
@click.option('--url', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--account-id', default=1, help='The Canvas account to access. This is usually the main account.')
@click.option('--search-term', help='If provided narrow returned results using the search-term.')
@click.option('--destination', '-d', required=True, help='Table to store retrieved data in.')
@pass_data
def list_account_users(data, url, api_key, account_id, search_term, destination):
    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    client = UsersAPI(url, api_key)
    r = client.list_users_in_account(account_id, search_term)
    data.cat(destination, petl.fromdicts(r))

command = list_account_users
