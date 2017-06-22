import unsync


@unsync.command()
@unsync.option('--source', '-s', required=True, help='Source table to print data from.')
def stats(data, source):
    """Print a text representation of the data table for a given KIND."""
    d = data.get(source)
    unsync.secho('Row Count: {}'.format(d.nrows()), fg='green')
    unsync.secho('Column Count: {}'.format(len(d[0])), fg='green')
