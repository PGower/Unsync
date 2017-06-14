"""A subclass of the click option that can lookup values from the data.values store."""

import re
from click.core import Option
import logging
import inspect

VALUE_OPTION_REGEX = r'^@\[.*\]$'
VARIABLE_ATTRIBUTE_SEPARATOR = '.'

logger = logging.getLogger('unsync.option')


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