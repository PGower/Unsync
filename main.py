import click
import os
import importlib
from plugins.common import UnsyncData

PLUGIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plugins')


# TODO: Figure out how to use the default_map context setting to read variables out of a config file or something to that effect.
class UnsyncCommands(click.MultiCommand):
    """Load commands from the plugins folder."""

    def __init__(self, *args, **kwargs):
        """Ensure that an UnsyncData object is initialized in the root context. Replaces @pass_data for this object."""
        kwargs['context_settings'] = {'obj': UnsyncData()}
        super(UnsyncCommands, self).__init__(*args, **kwargs)

    def list_commands(self, ctx):
        """List available commands by trying to import files from the plugins directory."""
        rv = []
        for filename in os.listdir(PLUGIN_DIR):
            if filename.endswith('.py'):
                try:
                    # attempt to import module
                    a = importlib.import_module('plugins.{}'.format(filename[:-3]))
                except Exception as e:
                    # I know this is bad but in this case I think its justified. I dont want any weirdness in the plugin files stopping this process.
                    click.secho('Could not parse plugin file {} because: {}'.format(filename, str(e)), err=True, fg='red')
                    continue
                if hasattr(a, 'command'):
                    rv += (filename[:-3],)
                else:
                    continue
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        """Retrieve and return the command to run."""
        try:
            a = importlib.import_module('plugins.{}'.format(name))
            return getattr(a, 'command')
        except NameError:
            pass
        except ImportError:
            pass


cli = UnsyncCommands(chain=True, help='Canvas Unsync Commands. Loaded automatically from the plugins folder.', context_settings={'obj': UnsyncData()})


if __name__ == '__main__':
    cli()
