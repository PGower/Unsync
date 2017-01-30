from unsync.lib.canvas_api import CanvasAPI, CanvasAPIError
import click
import petl

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
from unsync.lib.jinja_templates import render


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

    client = CanvasAPI(url, api_key)
    for user in user_data:
        try:
            r = client.list_logins_for_user(user[user_id_field])
            click.secho('Retrieved {} Canvas Logins for Canvas User ID: {}'.format(len(r), user[user_id_field]), fg='green')
        except CanvasAPIError as e:
            click.secho('Unable to retrieve Canvas Login information for Canvas User ID: {}'.format(user[user_id_field]), fg='red')
        for login in r:
            login_data.append(login)

    login_data = petl.fromdicts(login_data)
    data.set(destination, login_data)

command = get_user_logins
