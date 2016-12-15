"""Canvas Constants"""

SIS_TYPES = {
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

SIS_TYPE_NAMES = SIS_TYPES.keys()