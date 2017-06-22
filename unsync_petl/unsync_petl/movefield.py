"""PETL Head Command."""
import unsync


@unsync.command()
@unsync.option('--source', '-s', required=True, help='Name of the source data table.')
@unsync.option('--destination', '-d', help='Name of the destination data table. Will default to the source table if not specified.')
@unsync.option('--field', required=True, type=str, help='Name of the field to move.')
@unsync.option('--index', required=True, type=int, help='New index of the field.')
def movefield(data, source, destination, field, index):
    """Return the first n rows of the data table and store them in the destination data table."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.movefield(field, index)
    data.set(destination, s)
