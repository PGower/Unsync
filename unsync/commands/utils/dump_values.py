"""Utility command to dump the contexts of the values file."""
import click
import yaml
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
from unsync.lib.unsync_option import UnsyncOption


@unsync.command()
@click.option('--output-file', '-o', required=False, type=click.Path(dir_okay=False, readable=True, resolve_path=True, writable=True), help='Values data will be output to this file if given.')
@pass_data
def dump_values(data, output_file, new_val):
    """Dump the contents of the data.values store in YAML format."""
    d = yaml.dump(data.values)
    with open(output_file, 'w+') as f:
        f.write(d)

command = dump_values
