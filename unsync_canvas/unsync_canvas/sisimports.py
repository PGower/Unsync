import click

from pycanvas.apis.sis_imports import SisImportsAPI

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
from unsync.lib.jinja_templates import render

from datetime import datetime, timedelta

import petl


@unsync.command()
@click.option('--url', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--account-id', default=1, help='The Canvas account to access. This is usually the main account.')
@click.option('--created-since', default=(datetime.now() - timedelta(hours=12)), help='Filter imports shown to only those created since the given time.')
@click.option('--destination', '-d', required=True, help='The data table to store the results in.')
@click.option('--include-errors/--no-include-errors', default=False, help='Weather to include the full content of the processing_errors field.')
@click.option('--include-warnings/--no-include-warnings', default=False, help='Include the full content of the processing_warnings field.')
@click.option('--flatten-data/--no-flatten-data', default=True, help='Flatten the data field of the response.')
@pass_data
def list_imports(data, url, api_key, account_id, created_since, destination, include_errors, include_warnings, flatten_data):
    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

    client = SisImportsAPI(url, api_key)
    r = client.get_sis_import_list(account_id, created_since=created_since)
    t = []
    for i in r:
        if not include_errors:
            i['processing_errors'] = "{} Errors Ocurrred".format(len(i.get('processing_errors', [])))
        if not include_warnings:
            i['processing_warnings'] = "{} Warnings Ocurrred".format(len(i.get('processing_warnings', [])))
        if flatten_data:
            d = i['data']
            i['diffed_against_sis_batch_id'] = d.get('diffed_against_sis_batch_id', None)
            i['import_type'] = d.get('import_type', None)
            c = d.get('counts', {})
            i['counts'] = ';'.join(["{}: {}".format(k, c[k]) for k in c.keys()])
            i['supplied_batches'] = ';'.join(d.get('supplied_batches', []))
            del(i['data'])
        t.append(i)

    import_data = petl.fromdicts(t)

    data.set(destination, import_data)

command = list_imports
