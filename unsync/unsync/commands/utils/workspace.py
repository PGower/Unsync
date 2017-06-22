"""Unsync commands that will dump or restore the entire workspace (all tables)."""
import unsync
import pickle


@unsync.command()
@unsync.option('--output-file', '-o', type=unsync.Path(dir_okay=False, readable=True, resolve_path=True), help='File that the pickle representation will be written to.')
def dump_workspace(data, output_file):
    """Dump the entire workspace as a python pickle file."""
    workspace = {}
    for t in data.registry:
        workspace[t] = data.get(t).listoflists()
    with open(output_file, 'w') as f:
        pickle.dump(workspace, f)


@unsync.command()
@unsync.option('--input-file', '-i', type=unsync.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Workspace file that will be read.')
@unsync.option('--prefix', default='', help='Prefix to apply to table names when they are loaded from the workspace file.')
def load_workspace(data, input_file, prefix):
    """Load the workspace from a file created with dump_workspace."""
    with open(input_file, 'r') as f:
        workspace = pickle.load(f)
    for t in workspace.keys():
        data.set('{}{}'.format(prefix, t), workspace[t])
