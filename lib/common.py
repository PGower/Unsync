"""Common junk for CanvasUnsync. Will need to be tied at some stage."""
# from __future__ import absolute_import
import click
import petl
from lib.canvas_api import CanvasAPIError

KINDS = {
    'users': {
        'columns': ['user_id', 'integration_id', 'login_id', 'password', 'ssha_password', 'authentication_provider_id', 'first_name', 'last_name', 'full_name', 'sortable_name', 'short_name', 'email', 'status'],
        'required_columns': ['user_id', 'login_id', 'status'],
        'filename': 'users',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
    'courses': {
        'columns': ['course_id', 'short_name', 'long_name', 'account_id', 'term_id', 'status', 'start_date', 'end_date', 'course_format'],
        'required_columns': ['course_id', 'short_name', 'long_name', 'status'],
        'filename': 'courses',
        'enums': {
            'status': ['active', 'deleted', 'completed'],
            'course_format': ['on_campus', 'online', 'blended']
        }
    },
    'enrollments': {
        'columns': ['course_id', 'root_account', 'user_id', 'role', 'role_id', 'section_id', 'status', 'associated_user_id'],
        'required_columns': ['course_id', 'user_id', 'role_id'],
        'filename': 'enrollments',
        'enums': {
            'status': ['active', 'deleted', 'completed', 'inactive']
        }
    },
    'accounts': {
        'columns': ['account_id', 'parent_acount_id', 'name', 'status'],
        'required_columns': ['account_id', 'parent_acount_id', 'name', 'status'],
        'filename': 'accounts',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
    'terms': {
        'columns': ['term_id', 'name', 'status', 'start_date', 'end_date'],
        'required_columns': ['term_id', 'name', 'status'],
        'filename': 'terms',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
    'sections': {
        'columns': ['section_id', 'course_id', 'name', 'status', 'start_date', 'end_date'],
        'required_columns': ['section_id', 'course_id', 'name', 'status'],
        'filename': 'sections',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
    'groups': {
        'columns': ['group_id', 'account_id', 'name', 'status'],
        'required_columns': ['group_id', 'name', 'status'],
        'filename': 'groups',
        'enums': {
            'status': ['available', 'deleted']
        }
    },
    'group_membership': {
        'columns': ['group_id', 'user_id', 'status'],
        'required_columns': ['group_id', 'user_id', 'status'],
        'filename': 'group_membership',
        'enums': {
            'status': ['accepted', 'deleted']
        }
    },
    'xlist': {
        'columns': ['xlist_course_id', 'section_id', 'status'],
        'required_columns': ['xlist_course_id', 'section_id', 'status'],
        'filename': 'xlist',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
    'user_observers': {
        'columns': ['observer_id', 'student_id', 'status'],
        'required_columns': ['observer_id', 'student_id', 'status'],
        'filename': 'user_observers',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
}

KIND_NAMES = KINDS.keys()


class UnsyncData(object):
    """The unsync object that will be passed around."""

    d = {}

    def __init__(self):
        """Initialize the UnsyncData object. Use class methods to share data between instances."""
        if 'users' not in self.d:
            # users should always be present, if not create it.
            for name in KIND_NAMES:
                t = petl.wrap([KINDS[name]['columns']])
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
        if name not in KIND_NAMES:
            try:
                del(d[name])
            except KeyError:
                click.echo('Cannot delete {} as it does not exist.'.format(name))
        else:
            click.echo('Cannot delete {} as it is a core Canvas data table.'.format(name))

    def cat(self, name, table):
        """Convenience method, cat the given table against the existing table. Creates the table if it doesnt exist."""
        t = self.get(name)
        t = t.cat(petl.wrap(table))
        self.set(name, t)

    def filename(self, name, extension):
        """Come up with a filename for a given table name."""
        if name in KIND_NAMES:
            return KINDS[name]['filename'] + '.' + extension
        else:
            return name + '.' + extension

    @property
    def registry(self):
        """All of the data tables currently held in self.d."""
        return self.d.keys()


pass_data = click.make_pass_decorator(UnsyncData, ensure=True)


def apply_attr_map(t, attr_map):
    for a_map in attr_map:
        src = a_map[0]
        dest = a_map[1]
        t = t.addfield(dest, lambda rec, src=src: rec[src])
    return t


def apply_attr_fill(t, attr_fill):
    for a_fill_map in attr_fill:
        name = a_fill_map[0]
        value = a_fill_map[1]
        t = t.addfield(name, value)
    return t


def generic_import_actions(t, attr_map, attr_fill, delete_import_fields):
    t = apply_attr_map(t, attr_map)
    t = apply_attr_fill(t, attr_fill)
    if delete_import_fields is True:
        t = t.cut(*[a[1] for a in attr_map] + [a[0] for a in attr_fill])
    return t


def validate_source(ctx, param, value):
    # how do I get the UnsyncData object from the context?
    pass


def extract_api_data(response, header, empty_value=None):
    if response['response'].status_code == 200:
        t = [header]
        for i in response['data']:
            t.append([i.get(j, empty_value) for j in header])
        return petl.wrap(t)
    else:
        click.secho('Looks like something went wrong: {} {}.'.format(response['response'].status_code, response['response'].reason), err=True, fg='red')
        raise CanvasAPIError(response['response'])
