import click
import petl

KINDS = {
    'users': {
        'columns': ['user_id', 'integration_id', 'login_id', 'password', 'ssha_password', 'authentication_provider_id', 'first_name', 'last_name', 'full_name', 'sortable_name', 'short_name', 'email', 'status'],
        'required_columns': ['user_id', 'login_id', 'status'],
        'filename': 'users.csv',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
    'courses': {
        'columns': ['course_id', 'short_name', 'long_name', 'account_id', 'term_id', 'status', 'start_date', 'end_date', 'course_format'],
        'required_columns': ['course_id', 'short_name', 'long_name', 'status'],
        'filename': 'courses.csv',
        'enums': {
            'status': ['active', 'deleted', 'completed'],
            'course_format': ['on_campus', 'online', 'blended']
        }
    },
    'enrollments': {
        'columns': ['course_id', 'root_account', 'user_id', 'role', 'role_id', 'section_id', 'status', 'associated_user_id'],
        'required_columns': ['course_id', 'user_id', 'role_id'],
        'filename': 'enrollments.csv',
        'enums': {
            'status': ['active', 'deleted', 'completed', 'inactive']
        }
    },
    'accounts': {
        'columns': ['account_id', 'parent_acount_id', 'name', 'status'],
        'required_columns': ['account_id', 'parent_acount_id', 'name', 'status'],
        'filename': 'accounts.csv',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
    'terms': {
        'columns': ['term_id', 'name', 'status', 'start_date', 'end_date'],
        'required_columns': ['term_id', 'name', 'status'],
        'filename': 'terms.csv',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
    'sections': {
        'columns': ['section_id', 'course_id', 'name', 'status', 'start_date', 'end_date'],
        'required_columns': ['section_id', 'course_id', 'name', 'status'],
        'filename': 'sections.csv',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
    'groups': {
        'columns': ['group_id', 'account_id', 'name', 'status'],
        'required_columns': ['group_id', 'name', 'status'],
        'filename': 'groups.csv',
        'enums': {
            'status': ['available', 'deleted']
        }
    },
    'group_membership': {
        'columns': ['group_id', 'user_id', 'status'],
        'required_columns': ['group_id', 'user_id', 'status'],
        'filename': 'group_membership.csv',
        'enums': {
            'status': ['accepted', 'deleted']
        }
    },
    'xlist': {
        'columns': ['xlist_course_id', 'section_id', 'status'],
        'required_columns': ['xlist_course_id', 'section_id', 'status'],
        'filename': 'xlist.csv',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
    'user_observers': {
        'columns': ['observer_id', 'student_id', 'status'],
        'required_columns': ['observer_id', 'student_id', 'status'],
        'filename': 'user_observers.csv',
        'enums': {
            'status': ['active', 'deleted']
        }
    },
}

KIND_NAMES = KINDS.keys()

def initialize_context_object(obj):
    if obj is None:
        obj = {}
        for kind in KIND_NAMES:
            obj[kind] = [KINDS[kind]['columns']]
    return obj



class UnsyncData(object):
    """The unsync object that will be passed around"""
    def __init__(self):
        for name in KIND_NAMES:
            t = petl.wrap([KINDS[name]['columns']])
            setattr(self, name, t)


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
