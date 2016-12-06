"""Fill a column in the source table by looking up a value in the lookup table."""
import click

from .common import pass_data


@click.command()
@click.option('--source', '-s', required=True, help='The source data table.')
@click.option('--source-col', required=True, help='The column in the source data table to use for lookups.')
@click.option('--source-dst-col', help='The column to store the looked up value in.')
@click.option('--lookup', required=True, help='The table to use for lookups.')
@click.option('--lookup-col', required=True, help='The column in the lookup table containing data you want to match against.')
@click.option('--lookup-value', required=True, help='The column containing the value to insert into the source table.')
@click.option('--missing-value', default=None, help='The value to return if no match is made.')
@pass_data
def lookup_fill(data, source, source_col, source_dst_col, lookup, lookup_col, lookup_value, missing_value):
    """Fill a column in the source table by looking up a value in the lookup table."""
    if not source_dst_col:
        source_dst_col = source_col
    s = data.get(source)
    l = data.get(lookup)
    l = l.cut(lookup_col, lookup_value)
    l = l.unique(lookup_col)
    l = l.lookupone(lookup_col, lookup_value)

    s = s.convert(source_dst_col, lambda v, rec, l=l: l.get(getattr(rec, source_col), missing_value), pass_row=True)
    data.set(source, s)

command = lookup_fill
