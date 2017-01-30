from unsync.lib.canvas_api import CanvasAPI
import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
from unsync.lib.jinja_templates import render


@unsync.command()
@click.option('--url', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--user-id', default=1, help='The Canvas user account to retrieve logins for.')
@pass_data
def list_user_logins(data, url, api_key, user_id):
    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    client = CanvasAPI(url, api_key)
    r = client.list_logins_for_user(user_id)
    for login in r:
        click.echo(render('canvas_login.txt', login))


command = list_user_logins
