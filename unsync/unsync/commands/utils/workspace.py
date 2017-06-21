"""Unsync commands that will dump or restore the entire workspace (all tables)."""
import click
import pickle

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--output-file', '-o', type=click.Path(dir_okay=False, readable=True, resolve_path=True), help='File that the pickle representation will be written to.')
@pass_data
def dump_workspace(data, output_file):
    """Dump the entire workspace as a python pickle file."""
    workspace = {}
    for t in data.registry:
        workspace[t] = data.get(t).listoflists()
    with open(output_file, 'w') as f:
        pickle.dump(workspace, f)


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
