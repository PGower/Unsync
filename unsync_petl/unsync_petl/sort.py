"""PETL Sort Command."""
import unsync


@unsync.command()
@unsync.option('--source', '-s', required=True, type=str, help='Name of the source data table/s.')
@unsync.option('--destination', '-d', type=str, help='Name of the destination data table.')
@unsync.option('--key', '-k', multiple=True, help='The field names to sort by. Can be None, a single field or multiple fields.')
@unsync.option('--reverse/--no-reverse', default=False, help='Perform a reverse sort.')
def sort(data, source, destination, key, reverse):
    """Return rows that match the given selector."""
    if not destination:
        destination = source
    s = data.get(source)
    if key == ():  # An empty key is okay but must be None
        key = None
    s = s.sort(key=key, reverse=reverse)
    data.set(destination, s)
