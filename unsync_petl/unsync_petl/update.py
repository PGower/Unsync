"""PETL Update Command."""
import unsync


@unsync.command()
@unsync.option('--source', '-s', required=True, type=str, help='Name of the source data table/s.')
@unsync.option('--destination', '-d', type=str, help='Name of the destination data table.')
@unsync.option('--field', '-f', required=True, help='The field name to modify')
@unsync.option('--value', '-v', required=True, help='the value to fill the field with.')
def update(data, source, destination, field, value):
    """Update a given column with a static value."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.update(field, value)
    data.set(destination, s)
