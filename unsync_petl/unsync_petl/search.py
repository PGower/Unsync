"""Utility command to filter table rows based on the value of a column and a provided regex."""
import unsync


@unsync.command()
@unsync.option('--source', '-s', required=True, help='The source data table.')
@unsync.option('--filter', '-f', type=unsync.Tuple([str, str]), multiple=True, required=True, help='A tuple of values, first is the column to filter on and second is the regex to use.')
@unsync.option('--destination', '-d', help='The destination data table for matched rows. If blank will overwrite the source table.')
def search(data, source, filter, destination):
    """Include rows where the specified column matches the given regex."""
    if not destination:
        destination = source
    s = data.get(source)
    for column, pattern in filter:
        s = s.search(column, pattern)
    data.set(destination, s)
