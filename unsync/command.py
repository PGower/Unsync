import sys
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# When this has been installed using setuptool the unsync package exists, when in development it wont.
# Make sure that import calls succeed.
try:
    from unsync.lib.unsync_commands import UnsyncCommands
except ImportError:
    sys.path.insert(0, os.path.join(BASE_PATH, '../'))


import click  # noqa
from unsync.lib.unsync_commands import UnsyncCommands  # noqa
from unsync.lib.unsync_data import pass_data  # noqa

MODULE_COMMAND_DIR = os.path.join(BASE_PATH, 'commands')
LOCAL_COMMAND_DIR = os.path.join(os.getcwd(), 'commands')


@click.group(cls=UnsyncCommands, chain=True, help='Canvas Unsync Commands', command_dir=MODULE_COMMAND_DIR)
@click.option('--debug/--no-debug', default=False, help='Turn on debugging for all commands.')
@click.option('--force-table-realization/--no-force-table-realization', default=False, help='When turned on the data tables will be "realised" after each processing step. This will force errors to become apparent earlier.')
@pass_data
def cli_prototype(data, debug, force_table_realization):
    data.config.debug = debug
    data.config.force_table_realization = force_table_realization

    # If debug is set turn on debug logging for requests
    if data.config.debug:
        try:
            import http.client as http_client
        except ImportError:
            # Python 2
            import httplib as http_client
        http_client.HTTPConnection.debuglevel = 1

        import logging
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

cli = cli_prototype


if __name__ == '__main__':
    cli()
