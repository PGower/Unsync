"""Subclasses for the Click commands which implement custom functionality."""
import click
import os
import imp
from click.decorators import _make_command
import importlib
from timeit import default_timer as timer

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
        self.command_dir = command_dir
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
        commands = self._recursive_path_walk(self.command_dir)
        return commands

    def get_command(self, ctx, name):
        """Retrieve and return the command to run."""
        for i in range(name.count('_') + 1):
            # click.secho(name, fg='blue', bg='green')
            try:
                a = importlib.import_module('.commands.{}'.format(name), package='unsync')
            except (NameError, ImportError, AttributeError) as e:
                # Something went wrong with the import
                # click.secho(str(e), fg='red')
                if '_' in name:
                    name = name.replace('_', '.', 1)
                else:
                    click.secho(str(e), fg='red')
            else:
                # click.secho(name, fg='blue', bg='green')
                if hasattr(a, 'command'):
                    return a.command


class UnsyncCommand(click.Command):
    """A custom command used in Unsync."""

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
                click.secho('Command took: {}'.format(end-start), fg='red')
            else:
                click.secho('Command took: {}'.format(end-start), fg='yellow')
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