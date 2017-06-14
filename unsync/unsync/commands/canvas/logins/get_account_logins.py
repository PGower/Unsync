import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync

from pycanvas.apis.logins import LoginsAPI

import petl


@unsync.command()
@click.option('--url', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--account-id', default=1, help='The Canvas account to access. This is usually the main account.')
@click.option('--destination', '-d', required=True, help='The destination data table for the retieved data.')
@pass_data
def list_account_logins(data, url, api_key, account_id, destination):
    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    client = LoginsAPI(url, api_key)
    r = client.list_user_logins_accounts(account_id)
    d = petl.fromdicts(r)
    data.set(destination, d)

command = list_account_logins
