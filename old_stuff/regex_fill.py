"""Utility command to filter table rows based on the value of a column and a provided regex."""
import click

from .common import pass_data


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



"""Fill a column with data, either a fixed value or a value generated from other columns in the same row."""
import click

from .common import pass_data


@click.command()
@click.option('--source', '-s', required=True, help='The source data table.')
@click.option('--col', '-c', required=True, help='The column to fill. Will be created if it does not exist.')
@click.option('--value', '-v', required=True, help='The data to fill the column with. Provided value will be evaulated with in python and row data will be provided as locals.')
@click.option('--mode', '-m', default='replace', type=click.Choice(['replace', 'add']), help='Replace values in an existing row or add a new row with values.')
@pass_data
def fill_column(data, source, col, value, mode):
    """Fill the given column with values provided by value."""
    s = data.get(source)
    # compiled_value = compile(value, 'fill_column', mode='single')
    header = s.header()

    def inner_func(rec):
        d = dict(zip(header, [getattr(rec, h) for h in header]))
        return eval(value, None, d)

    if mode == 'replace':
        s = s.convert(col, lambda v, rec: inner_func(rec), pass_row=True)
    else:
        s = s.addfield(col, lambda v, rec: inner_func(rec), pass_row=True)
    data.set(source, s)

command = fill_column