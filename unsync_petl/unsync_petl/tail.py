"""PETL Tail Command."""
import unsync


@unsync.command()
@unsync.option('--source', '-s', required=True, help='Name of the source data table.')
@unsync.option('--destination', '-d', help='Name of the destination data table. Will default to the source table if not specified.')
@unsync.option('-n', type=int, required=True, help='Number of rows to select.')
def tail(data, source, destination, n):
    """Return the last n rows of the data table and store them in the destination data table."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.tail(n)
    data.set(destination, s)
