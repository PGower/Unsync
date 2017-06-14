"""List visible accounts."""

import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync

from pycanvas.apis.accounts import AccountsAPI

import petl


@unsync.command()
@click.option('--url', required=True, help='Canvas url to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--include', multiple=True, type=click.Choice(['lti_guid', 'registration_settings', 'services']), help='Additional information to include in the API response.')
@click.option('--destination', '-d', required=True, help='The destination table that imported Canvas course data will be stored in.')
@pass_data
def canvas_list_accounts(data, url, api_key, include, destination):
    """List accounts visible to the currently logged on user. Only returns data if the user is an account admin."""
    client = AccountsAPI(url, api_key)
    r = client.list_accounts(include)
    d = petl.fromdicts(r)
    data.set(destination, d)

command = canvas_list_accounts
