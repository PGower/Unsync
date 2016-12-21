from unsync.lib.canvas_api import CanvasAPI
import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
from unsync.lib.jinja_templates import render

from timeit import default_timer as timer
import time


@unsync.command()
@click.option('--limit', '-n', default=5, help='Number of imports to show.')
@click.option('--url', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--account-id', default=1, help='The Canvas account to access. This is usually the main account.')
@click.option('--import-id', type=int, required=True, help='The SIS Import ID returned in the SIS Upload Response.')
@click.option('--watch/--no-watch', default=False, help='If set this command will poll the Canvas API and update the SIS Import Status. Will stop when either the import status changes to "imported", "imported_with_messages", "failed", "failed_with_messages" or when the timeout is reached. Whichever happens first.')
@click.option('--watch-timeout', default=180, help='Upper limit on the number of seconds to poll the API for changes.')
@click.option('--watch-interval', default=5, help='How often should the Canvas API be polled. Default is every 5 seconds.')
@pass_data
def get_import(data, limit, url, api_key, account_id, import_id, watch, watch_timeout, watch_interval):
    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url
    client = CanvasAPI(url, api_key)
    rev_length = 0

    def api_call():
        r = client.get_sis_import_status(account_id, import_id)
        s = r['data']['workflow_state']
        t = str(render('sis_import_status.txt', r))
        if s in ['imported', 'importing']:
            click.secho(t, fg='green')
        elif s in ['imported_with_messages', 'cleanup_batch']:
            click.secho(t, fg='yellow')
        elif s in ['failed', 'failed_with_messages']:
            click.secho(t, fg='red')
        return len(t.splitlines())

    if watch:
        start = timer()
        while ((timer() - start) < watch_timeout):
            click.echo('\r' * rev_length)
            rev_length = api_call()
            time.sleep(watch_interval)
    else:
        api_call()

command = get_import
