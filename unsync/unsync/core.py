"""Subclasses for the Click commands which implement custom functionality."""
import os
import logging
import warnings
import importlib
import inspect
import re
import collections
import pickle
import pkgutil
import traceback

import petl

import click
from click.core import Option
from click.decorators import _param_memo
from click.decorators import _make_command

from datetime import datetime, timedelta

from timeit import default_timer as timer


VALUE_OPTION_REGEX = r'^@\[.*\]$'
VARIABLE_ATTRIBUTE_SEPARATOR = '.'
COMMAND_CACHE_EXPIRY_DELTA = timedelta(seconds=10)
APP_NAME = 'unsync'

logger = logging.getLogger('unsync.core')

# Code to make ipython launch whenever an exception occurs  TODO: add this into the unsync commands
# import sys
# from IPython.core import ultratb
# sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=1)


class Bunch(object):
    """Its da Bunch!!. http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/."""
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


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
                    click.secho(f'\nUnable to search {module_info.name} for commands, an exception occured. {e.__class__.__name__}: {e}\n')
                    # if ctx.obj.debug is True:
                    stdout_binary = click.get_text_stream('stdout')
                    traceback.print_exc(file=stdout_binary)
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


class UnsyncOption(Option):
    def consume_value(self, ctx, opts):
        value = opts.get(self.name)
        if value is not None:
            try:
                is_match = re.match(VALUE_OPTION_REGEX, value)
            except TypeError:
                pass
            else:
                if is_match:
                    v = Variable(value)
                    try:
                        new_value = v.resolve(ctx.obj.values)
                    except ValueResolutionFailed:
                        pass
                    else:
                        return new_value
        return super(UnsyncOption, self).consume_value(ctx, opts)


class UnsyncData(object):
    """The unsync object that will be passed around."""
    initialized = False
    tables = {}  # Tabular Data
    values = {}  # Single Value Data (or really any python object that needs to be stored.)
    config = Bunch()  # Globally stored config for the Unsync commands.

    def __init__(self):
        """Initialize the UnsyncData object. Use class methods to share data between instances."""
        if self.initialized is False:
            click.secho('Creating UnsyncData - ObjectID: {}'.format(id(self)), fg='yellow', bg='red')
            import os,threading;
            click.secho('Current environment PID: {} ThreadID: {}'.format(os.getpid(), threading.current_thread().ident), fg='yellow', bg='red')
            # Setup an execution start timer.
            self.config._execution_start = timer()

            # Seed the data tables with empty Canvas specific tables
            # for name in SIS_TYPE_NAMES:
            #     t = petl.wrap([SIS_TYPES[name]['columns']])
            #     self.tables[name] = t
            UnsyncData.initialized = True
        else:
            click.secho('ReCreating UnsyncData - objectID: {}'.format(id(self)), fg='yellow', bg='green')

    def get(self, name):
        """Return the requested table. If it does not exist then create it."""
        try:
            return UnsyncData.tables[name]
        except KeyError:
            UnsyncData.tables[name] = petl.wrap([[]])
            return UnsyncData.tables[name]

    def set(self, name, table):
        """Set the requested table, overwriting existing data."""
        if getattr(UnsyncData.config, 'force_table_realization', False):
            click.secho('Stored {} rows in table {}.'.format(table.nrows(), name), fg='yellow')
        UnsyncData.tables[name] = petl.wrap(table)

    def drop(self, name):
        """Drop the given table of data and remove its name from the registry."""
        try:
            del(UnsyncData.tables[name])
        except KeyError:
            click.secho('Cannot delete {} as it does not exist.'.format(name), fg='red')

    def cat(self, name, table):
        """Convenience method, cat the given table against the existing table. Creates the table if it doesnt exist."""
        t = self.get(name)
        t = t.cat(petl.wrap(table))
        self.set(name, t)

    def filename(self, name, extension):
        """Come up with a filename for a given table name."""
        return name + '.' + extension

    @property
    def registry(self):
        """All of the data tables currently held in self.tables."""
        return UnsyncData.tables.keys()





class ExpiredCommandCacheError(Exception):
    """Raised when the command cache __generated_at__ value is too far in the past."""
    pass


class ValueSyntaxError(Exception):
    '''Raised when the value accessor has invalid syntax.'''
    pass


class ValueResolutionFailed(Exception):
    '''Raised when a value accessor causes an unhandled exception.'''

    def __init__(self, inner_exception):
        self.inner_exception = inner_exception


class ValueDoesNotExist(Exception):
    '''Raised when the accessor does not exist.'''

    def __init__(self, msg, params=()):
        self.msg = msg
        self.params = params

    def __str__(self):
        return self.msg % self.params


# This was stolen from the Django template code. https://github.com/django/django/blob/master/django/template/base.py
class Variable:
    """
    A template variable, resolvable against a given context. The variable may
    be a hard-coded string (if it begins and ends with single or double quote
    marks)::
        >>> c = {'article': {'section':'News'}}
        >>> Variable('article.section').resolve(c)
        'News'
        >>> Variable('article').resolve(c)
        {'section': 'News'}
        >>> class AClass: pass
        >>> c = AClass()
        >>> c.article = AClass()
        >>> c.article.section = 'News'
    (The example assumes VARIABLE_ATTRIBUTE_SEPARATOR is '.')
    """

    def __init__(self, var):
        var = var[2:-1]
        self.var = var
        self.lookups = tuple(var.split(VARIABLE_ATTRIBUTE_SEPARATOR))

    def resolve(self, context):
        """Resolve this variable against a given context."""
        # We're dealing with a variable that needs to be resolved
        value = self._resolve_lookup(context)
        return value

    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.var)

    def __str__(self):
        return self.var

    def _resolve_lookup(self, context):
        """
        Perform resolution of a real variable (i.e. not a literal) against the
        given context.
        As indicated by the method's name, this method is an implementation
        detail and shouldn't be called by external code. Use Variable.resolve()
        instead.
        """
        current = context
        try:  # catch-all for silent variable failures
            for bit in self.lookups:
                try:  # dictionary lookup
                    current = current[bit]
                    # ValueError/IndexError are for numpy.array lookup on
                    # numpy < 1.9 and 1.9+ respectively
                except (TypeError, AttributeError, KeyError, ValueError, IndexError):
                    try:  # attribute lookup
                        # Don't return class attributes if the class is the context:
                        # if isinstance(current, BaseContext) and getattr(type(current), bit):
                        #     raise AttributeError
                        current = getattr(current, bit)
                    except (TypeError, AttributeError):
                        # Reraise if the exception was raised by a @property
                        # if not isinstance(current, BaseContext) and bit in dir(current):
                        #     raise
                        try:  # list-index lookup
                            current = current[int(bit)]
                        except (IndexError,  # list index out of range
                                ValueError,  # invalid literal for int()
                                KeyError,    # current is a dict without `int(bit)` key
                                TypeError):  # unsubscriptable object
                            raise ValueDoesNotExist("Failed lookup for key "
                                                    "[%s] in %r",
                                                    (bit, current))  # missing attribute
                if callable(current):
                    try:  # method call (assuming no args required)
                        current = current()
                    except TypeError:
                        raise
        except Exception as e:
            logger.debug(
                "Exception while resolving variable '%s' in values context.",
                bit,
                exc_info=True,
            )

            raise ValueResolutionFailed(e)

        return current


pass_data = click.make_pass_decorator(UnsyncData, ensure=True)

def option(*param_decls, **attrs):
    """Attaches an UnsyncOption to the command.  All positional arguments are
    passed as parameter declarations to :class:`Option`; all keyword
    arguments are forwarded unchanged (except ``cls``).
    This is equivalent to creating an :class:`Option` instance manually
    and attaching it to the :attr:`Command.params` list.
    :param cls: the option class to instantiate.  This defaults to
                :class:`Option`.
    """
    def decorator(f):
        if 'help' in attrs:
            attrs['help'] = inspect.cleandoc(attrs['help'])
        OptionClass = attrs.pop('cls', UnsyncOption)  # noqa
        _param_memo(f, OptionClass(param_decls, **attrs))
        return f
    return decorator


def command(name=None, cls=UnsyncCommand, **attrs):
    
    def cmd_decorator(f):
        cmd_with_data = pass_data(f)
        cmd = _make_command(cmd_with_data, name, attrs, cls)
        cmd.__doc__ = f.__doc__
        return cmd
    return cmd_decorator


# This is a handy way to define a set of options once and the reuse them across commands.
def add_options(options):
    '''Using callbacks append all of the common options from the options list to the passed function.'''
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options