"""Subclasses for the Click commands which implement custom functionality."""
import click
import os
import imp
import logging
import warnings
from click.decorators import _make_command
import importlib
from timeit import default_timer as timer

import pkgutil


# Code to make ipython launch whenever an exception occurs  TODO: add this into the unsync commands
# import sys
# from IPython.core import ultratb
# sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=1)


# TODO: Figure out how to use the default_map context setting to read variables out of a config file or something to that effect.
class UnsyncCommands(click.MultiCommand):
    """A Custom MultiCommand which loads commands from individual files in the command_dir."""

    def __init__(self, command_dir=None, *args, **kwargs):
        """Ensure that an UnsyncData object is initialized in the root context. Replaces @pass_data for this object."""
        # kwargs['context_settings'] = {'obj': UnsyncData()}
        self.logger = logging.getLogger('unsync.commands')
        self.command_dir = command_dir
        super(UnsyncCommands, self).__init__(*args, **kwargs)

    def _generate_command_mappings(self, quiet=False):
        """Using the currently configured sys.path setting look for packages that hold unsync commands and generate a mapping of names to actual commands."""
        commands = {}

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=Warning)
            for module_info in pkgutil.walk_packages():
                # Only look in packages that start with unsync_
                if module_info.name.startswith('unsync_'):
                    a = importlib.import_module(module_info.name)
                    
                    # Get the prefix for the Usync command.
                    try:
                        prefix = a.unsync_prefix
                    except AttributeError:
                        prefix = module_info.name

                    module_commands = getattr(a, 'unsync_commands', [])
                    for command_path in module_commands:
                        pkg_path = [module_info.name]
                        pkg_path = pkg_path + command_path.split('.')[:-1]
                        pkg_path = '.'.join(pkg_path)
                        command_name = command_path.split('.')[-1:][0]

                        try:
                            package = importlib.import_module(pkg_path)
                        except (NameError, ModuleNotFoundError) as e:
                            if not quiet:
                                click.secho(f'Unable to import command package {pkg_path}', fg='red')
                                click.secho(f'Encountered Exception: {e}')
                            continue

                        try:
                            command = getattr(package, command_name)
                        except AttributeError as e:
                            if not quiet:
                                click.secho(f'Unable to import command {command_name} from {pkg_path}', fg='red')
                                click.secho(f'Encountered Exception: {e}')
                            continue

                        command_display_name = getattr(command, 'display_name', command_name)
                        commands[(f'{prefix}.{command_display_name}')] = command
        return commands


    def list_commands(self, ctx):
        """List available commands by trying to import files from the plugins directory."""
        command_mappings = self._generate_command_mappings()
        return command_mappings.keys()

    def get_command(self, ctx, name):
        """Retrieve and return the command to run."""
        command_mappings = self._generate_command_mappings(quiet=True)  # We dont need to see errors more than once.
        if name in command_mappings:
            return command_mappings[name]
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