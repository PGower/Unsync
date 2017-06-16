"""Subclasses for the Click commands which implement custom functionality."""
import click
import os
import logging
import warnings
from click.decorators import _make_command
import importlib
from timeit import default_timer as timer
import collections
import pickle
import pkgutil
from datetime import datetime, timedelta


COMMAND_CACHE_EXPIRY_DELTA = timedelta(seconds=10)
APP_NAME = 'unsync'

# Code to make ipython launch whenever an exception occurs  TODO: add this into the unsync commands
# import sys
# from IPython.core import ultratb
# sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=1)


# TODO: Figure out how to use the default_map context setting to read variables out of a config file or something to that effect.
class UnsyncCommands(click.MultiCommand):
    """A Custom MultiCommand which loads commands from individual files in the command_dir."""

    def __init__(self, *args, **kwargs):
        """Ensure that an UnsyncData object is initialized in the root context. Replaces @pass_data for this object."""
        # kwargs['context_settings'] = {'obj': UnsyncData()}
        self.logger = logging.getLogger('unsync.commands')
        super(UnsyncCommands, self).__init__(*args, **kwargs)

    def _generate_command_mappings(self, quiet=False):
        """Using the currently configured sys.path setting look for packages that hold unsync commands and generate a mapping of names to actual commands."""
        command_map = {}

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=Warning)
            module_iter = pkgutil.walk_packages()
            if quiet is True:
                for module_info in module_iter:
                    module_commands = self._extract_commands_from_package(module_info, quiet)
                    command_map.update(module_commands)
            else:
                module_info_list = [i for i in module_iter]
                with click.progressbar(module_info_list, length=len(module_info_list), label='Discovering Unsync Commands') as module_iter_progress:
                    for module_info in module_iter_progress:
                        module_commands = self._extract_commands_from_package(module_info, quiet)
                        command_map.update(module_commands)

        app_dir = click.get_app_dir(APP_NAME)

        if not os.path.exists(app_dir):
            # Create if it doesnt exist.
            os.mkdir(app_dir)

        with open(os.path.join(app_dir, 'command_cache.pickle'), 'wb') as f:
            command_path_map = dict([(k, v[1]) for k,v in command_map.items()])
            command_path_map['__generated_at__'] = datetime.now()
            pickle.dump(command_path_map, f)

        return command_map

    def _get_package_command(self, pkg_path, command_name, quiet=False):
        try:
            package = importlib.import_module(pkg_path)
        except (NameError, ModuleNotFoundError) as e:
            if not quiet:
                click.secho(f'Unable to import command package {pkg_path}', fg='red')
                click.secho(f'Encountered Exception: {e}')
            return None

        try:
            command = getattr(package, command_name)
        except AttributeError as e:
            if not quiet:
                click.secho(f'Unable to import command {command_name} from {pkg_path}', fg='red')
                click.secho(f'Encountered Exception: {e}')
            return None

        command_display_name = getattr(command, 'display_name', command_name)
        return (command_display_name, command)


    def _extract_commands_from_package(self, module_info, quiet=False):
        commands = {}

        if module_info.name.startswith('unsync_') or module_info.name.startswith('unsync.'):
            try:
                a = importlib.import_module(module_info.name)
            except Exception as e:
                # This seems like a terrible thing to do but its the only way to ensure that Unsync can continue to function even
                # if some of the files it wants to imort are horribly broken.
                if not quiet:
                    click.secho(f'\nUnable to search {module_info.name} for commands due to the raised exception: {e}\n')
                return commands
            
            # Get the prefix for the Usync command.
            try:
                prefix = a.unsync_prefix
            except AttributeError:
                prefix = module_info.name

            module_commands = getattr(a, 'unsync_commands', [])
            if not isinstance(module_commands, collections.Iterable):
                # its possible there is a module somewhere called unsync_commands that is going to 
                # trip this up. This check fixes that issue.
                return commands
            else:
                for command_path in module_commands:
                    pkg_path = [module_info.name]
                    pkg_path = pkg_path + command_path.split('.')[:-1]
                    pkg_path = '.'.join(pkg_path)
                    command_name = command_path.split('.')[-1:][0]
                    full_command_path = pkg_path + '.' + command_name

                    try:
                        command_display_name, command = self._get_package_command(pkg_path, command_name, quiet)
                    except TypeError:
                        continue

                    commands[(f'{prefix}.{command_display_name}')] = (command, full_command_path)
                return commands
        else:
            return commands


    def list_commands(self, ctx):
        """List available commands by trying to import files from the plugins directory."""
        command_mappings = self._generate_command_mappings()
        return command_mappings.keys()

    def get_command(self, ctx, name):
        """Retrieve and return the command to run."""
        try:
            # If they exist try to load the command_cache, this can save us alot of time.
            app_dir = click.get_app_dir(APP_NAME)
            with open(os.path.join(app_dir, 'command_cache.pickle'), 'rb') as f:
                command_path_mappings = pickle.load(f)

            # Check the command_cache age, if its too old, walk packages to discover commands again
            command_cache_generated_at = command_path_mappings['__generated_at__']
            command_cache_delta = datetime.now() - command_cache_generated_at
            if command_cache_delta > COMMAND_CACHE_EXPIRY_DELTA:
                click.secho(f'Command cache has expired, it is {command_cache_delta} seconds old. Regenerating.',fg='green')
                raise ExpiredCommandCacheError()

            # Try to turn the path into an actual command
            if name in command_path_mappings:
                full_command_path = command_path_mappings[name]
                pkg_path = '.'.join(full_command_path.split('.')[:-1])
                command_name = full_command_path.split('.')[-1]
                try:
                    command_display_name, command = self._get_package_command(pkg_path, command_name)
                    return command
                except TypeError:
                    click.secho(f'Unable to find command: {name}', fg='red')
        except (FileNotFoundError, IOError, ExpiredCommandCacheError):
            command_mappings = self._generate_command_mappings(quiet=True)  # We dont need to see errors more than once.
            if name in command_mappings:
                return command_mappings[name][0]
            else:
                click.secho(f'Unable to find command: {name}', fg='red')


class UnsyncCommand(click.Command):
    """A custom command used in Unsync."""

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('unsync.command')
        super(UnsyncCommand, self).__init__(*args, **kwargs)

    def invoke(self, ctx):
        start = timer()
        if ctx.obj.config.debug is True:
            click.secho('== {} =='.format(ctx.info_name), fg='yellow')
            click.secho('Total Execution Time: {}'.format(timer() - ctx.obj.config._execution_start), fg='yellow')
            if len(ctx.args) > 0:
                click.secho('    Args: {}'.format(','.join(ctx.args)), fg='yellow')
            if len(ctx.params.keys()) > 0:
                click.secho('    Params:', fg='yellow')
                for name, value in ctx.params.items():
                    click.secho('      {} = {}'.format(name, value), fg='yellow')

        r = super(UnsyncCommand, self).invoke(ctx)

        if ctx.obj.config.debug is True:
            end = timer()
            delta = end - start
            if delta > 3:
                click.secho('Command took: {}'.format(end - start), fg='red')
            else:
                click.secho('Command took: {}'.format(end - start), fg='yellow')
            click.echo('\n')

        return r


# Custom Decorator that Always uses the UnsyncCommand class
# Unsync class is syntactic sugar.

class Unsync(object):
    @staticmethod
    def command(name=None, cls=UnsyncCommand, **attrs):
        if cls is None:
            cls = click.Command

        def decorator(f):
            cmd = _make_command(f, name, attrs, cls)
            cmd.__doc__ = f.__doc__
            return cmd
        return decorator
unsync = Unsync


# This is a handy way to define a set of options once and the reuse them across commands.
def add_options(options):
    '''Using callbacks append all of the common options from the options list to the passed function.'''
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options


class ExpiredCommandCacheError(Exception):
    """Raised when the command cache __generated_at__ value is too far in the past."""
    pass
