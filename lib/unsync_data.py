"""The CanvasUnsync data object. Passed between all commands."""
import petl
import click
from canvas_meta import SIS_TYPES, SIS_TYPE_NAMES
from timeit import default_timer as timer


class Bunch:
    """Its da Bunch!!. http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/."""
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class UnsyncData(object):
    """The unsync object that will be passed around."""

    tables = {}  # Tabular Data
    values = {}  # Single Value Data (or really any python object that needs to be stored.)
    config = Bunch()  # Globally stored config for the Unsync commands.

    def __init__(self):
        """Initialize the UnsyncData object. Use class methods to share data between instances."""
        if not hasattr(self.config, '_execution_start'):
            self.config._execution_start = timer()

        if 'users' not in self.tables:
            # users should always be present, if not create it.
            for name in SIS_TYPE_NAMES:
                t = petl.wrap([SIS_TYPES[name]['columns']])
                self.tables[name] = t

    def get(self, name):
        """Return the requested table. If it does not exist then create it."""
        try:
            return self.tables[name]
        except KeyError:
            self.tables[name] = petl.wrap([[]])
            return self.tables[name]

    def set(self, name, table):
        """Set the requested table, overwriting existing data."""
        if getattr(self.config, 'force_table_realization', False):
            click.secho('Stored {} rows in table {}.'.format(table.nrows(), name))
        self.tables[name] = petl.wrap(table)

    def drop(self, name):
        """Drop the given table of data and remove its name from the registry."""
        if name not in SIS_TYPE_NAMES:
            try:
                del(self.tables[name])
            except KeyError:
                click.secho('Cannot delete {} as it does not exist.'.format(name), fg='red')
        else:
            click.secho('Cannot delete {} as it is a core Canvas data table.'.format(name), fg='red')

    def cat(self, name, table):
        """Convenience method, cat the given table against the existing table. Creates the table if it doesnt exist."""
        t = self.get(name)
        t = t.cat(petl.wrap(table))
        self.set(name, t)

    def validate_header(self, name, header, allow_subset=False):
        """Validate the the header of the table matches the header provided. If allow_subset is True then check that the provider header is a subset of the table header not exactly equal."""
        if allow_subset:


    def filename(self, name, extension):
        """Come up with a filename for a given table name."""
        if name in SIS_TYPE_NAMES:
            return SIS_TYPES[name]['filename'] + '.' + extension
        else:
            return name + '.' + extension

    @property
    def registry(self):
        """All of the data tables currently held in self.tables."""
        return self.tables.keys()

pass_data = click.make_pass_decorator(UnsyncData, ensure=True)


class TableHeaderValidationError(Exception):
    def __init__(self, table_name, table_header, expected_header, allow_subset):
        self.table_name = table_name
        self.table_header = table_header
        self.expected_header = expected_header
        self.allow_subset

    def __unicode__(self):
        if allow_subset:
            return ''

