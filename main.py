import click
import os
from lib import UnsyncCommands
from lib.unsync_data import pass_data


COMMAND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'commands')


@click.group(cls=UnsyncCommands, chain=True, help='Canvas Unsync Commands', command_dir=COMMAND_DIR)
@click.option('--debug/--no-debug', default=False, help='Turn on debugging for all commands.')
@click.option('--force-table-realization/--no-force-table-realization', default=False, help='When turned on the data tables will be "realised" after each processing step. This will force errors to become apparent earlier.')
@pass_data
def cli(data, debug, force_table_realization):
    data.config.debug = debug
    data.config.force_table_realization = force_table_realization


if __name__ == '__main__':
    cli()
