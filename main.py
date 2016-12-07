import click
import os
import importlib
import imp
from lib.common import UnsyncData

COMMAND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'commands')


# TODO: Figure out how to use the default_map context setting to read variables out of a config file or something to that effect.
class UnsyncCommands(click.MultiCommand):
    """Load commands from the plugins folder."""

    def __init__(self, *args, **kwargs):
        """Ensure that an UnsyncData object is initialized in the root context. Replaces @pass_data for this object."""
        kwargs['context_settings'] = {'obj': UnsyncData()}
        super(UnsyncCommands, self).__init__(*args, **kwargs)

    def _recursive_path_walk(self, path):
        r = []
        for name in os.listdir(path):
            if os.path.isdir(os.path.join(path, name)):
                sub_r = self._recursive_path_walk(os.path.join(path, name))
                r += ['{}_{}'.format(name, i) for i in sub_r]
            else:
                if name.endswith('.py'):
                    filename = name
                    name = name[:-3]
                    try:
                        a = imp.load_source(name, os.path.join(path, filename))
                    except Exception as e:
                        click.secho('Unable to import plugin file at {} due to error: {}'.format(os.path.join(path, filename), str(e)), err=True, fg='red')
                        continue
                    if hasattr(a, 'command'):
                        r.append(name)
        return r

    def list_commands(self, ctx):
        """List available commands by trying to import files from the plugins directory."""
        commands = []
        # Walk through the command dir enumerating files and subfolders. Subfolder names turn into command prefixes.
        commands = self._recursive_path_walk(COMMAND_DIR)
        return commands

    def get_command(self, ctx, name):
        """Retrieve and return the command to run."""
        for i in range(name.count('_') + 1):
            try:
                a = importlib.import_module('commands.{}'.format(name))
                return getattr(a, 'command')
            except NameError:
                pass
            except ImportError:
                pass
            name = name.replace('_', '.', 1)

cli = UnsyncCommands(chain=True, help='Canvas Unsync Commands')


if __name__ == '__main__':
    cli()
