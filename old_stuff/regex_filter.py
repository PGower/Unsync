"""Utility command to filter table rows based on the value of a column and a provided regex."""
import click

from lib.common import pass_data


@click.command()
@click.option('--source', '-s', required=True, help='The source data table.')
@click.option('--filter', '-f', type=click.Tuple([unicode, unicode]), multiple=True, required=True, help='A tuple of values, first is the column to filter on and second is the regex to use.')
@click.option('--mode', '-m', type=click.Choice(['include', 'exclude']), required=True, help='When set to include any matched rows will be included in the result, when exclude they will be removed.')
@click.option('--destination', '-d', help='The destination data table for matched rows. If blank will overwrite the source table.')
@pass_data
def regex_filter(data, source, filter, mode, destination):
    """Filter the table with the given regexes."""
    if not destination:
        destination = source
    s = data.get(source)
    for column, pattern in filter:
        if mode == 'include':
            s = s.search(column, pattern)
        elif mode == 'exclude':
            s = s.searchcomplement(column, pattern)
    data.set(destination, s)

command = regex_filter
