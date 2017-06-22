"""PETL Addfield Command."""
import unsync
import petl


@unsync.command()
@unsync.option('--source', '-s', required=True, help='Name of the source data table.')
@unsync.option('--field', '-f', required=True, help='Name of the new field.')
@unsync.option('--value', '-v', required=True, help='Either a static value or a string that can be evaluated by petl.expr')
def addfield(data, source, field, value):
    """Return the first n rows of the data table and store them in the destination data table."""
    s = data.get(source)
    s = s.addfield(field, petl.expr(value))
    data.set(source, s)
