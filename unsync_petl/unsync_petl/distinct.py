"""PETL Distinct Command."""
import unsync


@unsync.command()
@unsync.option('--source', '-s', required=True, help='Name of the source data table.')
@unsync.option('--destination', '-d', help='Name of the destination data table. Will default to the source table if not specified.')
@unsync.option('--key', '-k', default=None, help='If the key keyword argument is passed, the comparison is done on the given key instead of the full row.')
@unsync.option('--count', '-c', default=None, help='If the count argument is not None, it will be used as the name for an additional field, and the values of the field will be the number of duplicate rows.')
@unsync.option('--presorted/--no-presorted', default=False, help='Are the tables presorted?')
@unsync.option('--buffersize', default=None, type=int, help="Controls how presorting is performed. See http://petl.readthedocs.io/en/latest/transform.html#petl.transform.sorts.sort")
@unsync.option('--tempdir', type=unsync.Path(file_okay=False, dir_okay=True, exists=True, writable=True, resolve_path=True), help='Location to store chunks when sorting.')
@unsync.option('--cache/--no-cache', default=True, help='Controls wether presort results are chaced for use in subsequent operations.')
def distinct(data, source, destination, key, count, presorted, buffersize, tempdir, cache):
    """Return only rows that are distinct within the table."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.distinct(key=key, count=count, presorted=presorted, buffersize=buffersize, tempdir=tempdir, cache=cache)
    data.set(destination, s)
