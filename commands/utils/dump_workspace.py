"""Utility command to dump the workspace to a file using python pickle."""
import click
import pickle

from lib.unsync_data import pass_data
from lib.unsync_commands import unsync


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

command = dump_workspace
