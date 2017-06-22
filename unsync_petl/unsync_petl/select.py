"""PETL Select Command."""
import unsync


@unsync.command()
@unsync.option('--source', '-s', required=True, type=str, help='Name of the source data table/s.')
@unsync.option('--destination', '-d', type=str, help='Name of the destination data table.')
@unsync.option('--selector', required=True, type=str, help='A string expression to be applied against the row. See http://petl.readthedocs.io/en/latest/transform.html#petl.transform.selects.select')
def select(data, source, destination, selector):
    """Return rows that match the given selector."""
    if not destination:
        destination = source
    s = data.get(source)
    s = s.select(selector)
    data.set(destination, s)
