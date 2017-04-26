"""Return all sub accounts of the given account."""

import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
from unsync.lib.unsync_option import UnsyncOption

from pycanvas.apis.accounts import AccountsAPI

import petl


@unsync.command()
@click.option('--url', required=True, help='Canvas url to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--account-id', required=True, type=int, default=1, help='The Canvas Account to search for courses in.')
@click.option('--recursive/--no-recursive', default=False, help='Recursively search for sub accounts.')
@click.option('--destination', '-d', required=True, help='The destination table that imported Canvas course data will be stored in.')
@pass_data
def canvas_get_sub_accounts_of_account(data, url, api_key, account_id, recursive, destination):
    """Import Canvas courses via the REST API and store it in the destination data table."""
    client = AccountsAPI(url, api_key)
    r = client.get_sub_accounts_of_account(account_id, recursive)
    d = petl.fromdicts(r)
    data.set(destination, d)

command = canvas_get_sub_accounts_of_account
