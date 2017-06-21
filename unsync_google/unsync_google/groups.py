import click

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync

REQUIRED_SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.group.member',
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.orgunit',
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.user.alias'
]


@unsync.command()
@click.option('--client-secrets', required=True, default='./client-secrets.json', type=click.Path(dir_okay=False, file_okay=True, readable=True, resolve_path=True), help='Location of the client-secrets.json file.')
@click.option('--credentials-path', type=click.Path(dir_okay=True, file_okay=False, resolve_path=True), help='Location of stored credentials. Defaults to a credentials directory in the app data folder.')
@click.option('--apps-domain', required=True, help='The Google Apps domain name.')
@click.option('--')
@pass_data
def list_groups(data, output_file):
    """Query the Google Apps domain and retrieve group information."""
    pass
