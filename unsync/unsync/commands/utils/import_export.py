"""Commands to import or export the current command stack to or from a file."""

import click
import unsync
from unsync.core import NestedUnsyncCommands
import pickle


@unsync.command()
@click.option('--output-file', '-o', type=click.Path(dir_okay=False, readable=True, resolve_path=True), help='File that the command stack will be written too.')
@click.option('--exit-after', type=bool, default=True, help='Automatically exit from the unsync tool and do not run any of the exported commands after the export is complete.')
@click.pass_context
def export_command_stack(ctx, data, output_file, exit_after):
    """Export all of the commands following the export command in the call stack."""
    # Perform a quick check and make sure that there are no nested export calls. It wont work and I wont support it.
    if ctx.info_name in ctx.command_stack:
        raise ExportNestingError('Export commands cannot be nested.')
    with open(output_file, 'wb') as f:
        pickle.dump(ctx.command_stack, f)
    if exit_after is True:
        raise click.Abort()


@unsync.command()
@click.option('--input-file', '-i', type=click.Path(dir_okay=False, readable=True, exists=True, resolve_path=True), help='File that extra commands will be read from.')
@click.pass_context
def import_command_stack(ctx, data, input_file):
    """Import the given set of commands from the input_file and insert them into the command stream after that current command."""
    with open(input_file, 'rb') as f:
        command_stack = pickle.load(f)
    n = NestedUnsyncCommands(command_stack)
    n.invoke(ctx)


class ExportNestingError(Exception):
    pass
