"""Utility command to filter table rows based on wether the row value exists in the column of another table."""
import click

from .common import pass_data


@click.command()
@click.option('--source', '-s', required=True, help='The source data table.')
@click.option('--source-col', required=True, help='The column in the source data table to use for lookups.')
@click.option('--lookup', required=True, help='The table to use for lookups.')
@click.option('--lookup-col', required=True, help='The column in the lookup table containing data you want to match against.')
@click.option('--mode', '-m', type=click.Choice(['include', 'exclude']), required=True, help='When set to include any matched rows will be included in the result, when exclude they will be removed.')
@click.option('--destination', '-d', help='The destination data table for matched rows. If blank will overwrite the source table.')
@pass_data
def lookup_filter(data, source, source_col, lookup, lookup_col, mode, destination):
    """Filter the source table based on wether the source-col value exists in the lookup table."""
    if not destination:
        destination = source
    s = data.get(source)

    l = data.get(lookup)
    l = l.cut(lookup_col)
    l = l.unique(lookup_col)
    l = l.values(lookup_col)
    l = list(l)

    if mode == 'include':
        s = s.select(source_col, lambda v, l=l: v in l)
    elif mode == 'exclude':
        s = s.select(source_col, lambda v, l=l: v not in l)

    data.set(destination, s)

command = lookup_filter
