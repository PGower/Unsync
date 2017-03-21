"""The CanvasUnsync data object. Passed between all commands."""
import petl
import click
from .canvas_meta import SIS_TYPES, SIS_TYPE_NAMES
from timeit import default_timer as timer


class Bunch:
    """Its da Bunch!!. http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/."""
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


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
            for name in SIS_TYPE_NAMES:
                t = petl.wrap([SIS_TYPES[name]['columns']])
                self.tables[name] = t
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
        if name not in SIS_TYPE_NAMES:
            try:
                del(UnsyncData.tables[name])
            except KeyError:
                click.secho('Cannot delete {} as it does not exist.'.format(name), fg='red')
        else:
            click.secho('Cannot delete {} as it is a core Canvas data table.'.format(name), fg='red')

    def cat(self, name, table):
        """Convenience method, cat the given table against the existing table. Creates the table if it doesnt exist."""
        t = self.get(name)
        t = t.cat(petl.wrap(table))
        self.set(name, t)

    def filename(self, name, extension):
        """Come up with a filename for a given table name."""
        if name in SIS_TYPE_NAMES:
            return SIS_TYPES[name]['filename'] + '.' + extension
        else:
            return name + '.' + extension

    @property
    def registry(self):
        """All of the data tables currently held in self.tables."""
        return UnsyncData.tables.keys()

pass_data = click.make_pass_decorator(UnsyncData, ensure=True)