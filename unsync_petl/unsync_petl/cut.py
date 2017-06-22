"""PETL Cut Command."""
import unsync


@unsync.command()
@unsync.option('--source', '-s', required=True, help='Name of the source data table.')
@unsync.option('--destination', '-d', help='Name of the destination data table. Will default to the source table if not specified.')
@unsync.option('--field', multiple=True, type=str, help='Field names to cut from the source table.')
@unsync.option('--index', multiple=True, type=int, help='Field indexes to cut from the source table.')
def cut(data, source, destination, field, index):
    """Return only columns that are specified in field on index options."""
    if not destination:
        destination = source
    s = data.get(source)
    a = field + index
    s = s.cut(*a)
    data.set(destination, s)
