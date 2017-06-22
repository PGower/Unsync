"""PETL Rename Command."""
import unsync


@unsync.command()
@unsync.option('--source', '-s', required=True, type=str, help='Name of the source data table/s.')
@unsync.option('--destination', '-d', type=str, help='Name of the destination data table.')
@unsync.option('--transform', '-t', multiple=True, type=unsync.Tuple([str, str]), help='Header transforms, FROM, TO.')
def rename(data, source, destination, transform):
    """Rename columns based on Transform parameters."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.rename(dict(transform))
    data.set(destination, s)
