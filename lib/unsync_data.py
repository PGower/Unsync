"""The CanvasUnsync data object. Passed between all commands."""
import petl
import click
from canvas_meta import SIS_TYPES, SIS_TYPE_NAMES


class UnsyncData(object):
    """The unsync object that will be passed around."""

    d = {}

    def __init__(self):
        """Initialize the UnsyncData object. Use class methods to share data between instances."""
        if 'users' not in self.d:
            # users should always be present, if not create it.
            for name in SIS_TYPE_NAMES:
                t = petl.wrap([SIS_TYPES[name]['columns']])
                self.d[name] = t

    def get(self, name):
        """Return the requested table. If it does not exist then create it."""
        try:
            return self.d[name]
        except KeyError:
            self.d[name] = petl.wrap([[]])
            return self.d[name]

    def set(self, name, table):
        """Set the requested table, overwriting existing data."""
        self.d[name] = petl.wrap(table)

    def drop(self, name):
        """Drop the given table of data and remove its name from the registry."""
        if name not in SIS_TYPE_NAMES:
            try:
                del(self.d[name])
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
        """All of the data tables currently held in self.d."""
        return self.d.keys()

pass_data = click.make_pass_decorator(UnsyncData, ensure=True)
