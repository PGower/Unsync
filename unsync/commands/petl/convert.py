"""PETL Convert Command."""
import click
import petl
import re
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


def this_expr(s):
    """
    Construct a function operating on a table record.

    The expression string is converted into a lambda function by prepending
    the string with ``'lambda v, rec: '``, then replacing anything enclosed in
    curly braces (e.g., ``"{foo}"``) with a lookup on the record (e.g.,
    ``"rec['foo']"``), then finally calling :func:`eval`.

    So, e.g., the expression string ``"{foo} * {bar}"`` is converted to the
    function ``lambda rec: rec['foo'] * rec['bar']``

    """

    prog = re.compile('\{([^}]+)\}')

    def repl(matchobj):
        return "rec['%s']" % matchobj.group(1)

    return eval("lambda v, rec: " + prog.sub(repl, s))


@unsync.command()
@click.option('--source', '-s', required=True, help='Name of the source data table.')
@click.option('--field', '-f', required=True, help='Name of the new field.')
@click.option('--value', '-v', required=True, help='Either a static value or a string that can be evaluated by petl.expr')
@pass_data
def petl_convert(data, source, field, value):
    """Convert the given field using the given value. Value is compiled to a lambda by prepending with lambda v, rec: and replacing curly bracket fieldnames with appropriate lookups."""
    s = data.get(source)
    s = s.convert(field, this_expr(value), pass_row=True)
    data.set(source, s)

command = petl_convert
