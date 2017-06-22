"""PETL Head Command."""
import unsync


@unsync.command()
@unsync.option('--source', '-s', required=True, help='Name of the source data table.')
@unsync.option('--destination', '-d', help='Name of the destination data table. Will default to the source table if not specified.')
@unsync.option('--start', default=None, type=int, help='Row number to start the slice from.')
@unsync.option('--stop', required=True, type=int, help='Row number to stop the slice at.')
@unsync.option('--step', default=None, type=int, help='Slice step.')
def rowslice(data, source, destination, start, stop, step):
    """Return the first n rows of the data table and store them in the destination data table."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.rowslice(start, stop, step)
    data.set(destination, s)
