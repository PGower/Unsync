"""Utility command to load a workspace from a pickle file created with the dump_workspace command."""
import click
import pickle

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Workspace file that will be read.')
@click.option('--prefix', default='', help='Prefix to apply to table names when they are loaded from the workspace file.')
@pass_data
def load_workspace(data, input_file, prefix):
    """Load the workspace from a file created with dump_workspace."""
    with open(input_file, 'r') as f:
        workspace = pickle.load(f)
    for t in workspace.keys():
        data.set('{}{}'.format(prefix, t), workspace[t])

command = load_workspace
