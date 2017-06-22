"""PETL Head Command."""
from __future__ import unicode_literals
import unsync
import petl

@unsync.command()
@unsync.option('--source', '-s', multiple=True, required=True, help='Name of the source data table/s.')
@unsync.option('--destination', '-d', required=True, help='Name of the destination data table.')
@unsync.option('--header', '-h', multiple=True, type=str, help='Use the provided list in place of the existing table headers.')
@unsync.option('--missing', default=None, help='The value to store in columns that have no value set.')
def cat(data, source, destination, header, missing):
    """Return the first n rows of the data table and store them in the destination data table."""
    sources = [data.get(s) for s in source]
    if len(header) == 0:
        n = petl.cat(*sources, missing=missing)
    else:
        n = petl.cat(*sources, header=header, missing=missing)
    data.set(destination, n)
