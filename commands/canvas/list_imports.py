from canvas_api import CanvasAPI
import click

from lib.common import pass_data
from lib.jinja_templates import render


@click.command()
@click.option('--limit', '-n', default=5, help='Number of imports to show.')
@click.option('--instance', required=True, help='Canvas instance to use. Usually something like <schoolname>.instructure.com.')
@click.option('--api-key', required=True, help='API Key to use when accessing the Canvas instance. Can be generated in your profile section.')
@click.option('--account-id', default=1, help='The Canvas account to access. This is usually the main account.')
@pass_data
def list_imports(data, limit, instance, api_key, account_id):
    client = CanvasAPI(instance, api_key)
    r = client.list_sis_imports(1)

    for count, import_data in zip(range(0, len(r['data']['sis_imports'])), r['data']['sis_imports']):
        if count <= limit:
            click.echo(render('import_info.txt', {'import': import_data}))
        else:
            break

command = list_imports