"""Utility command to cut columns in a table. Removes all columns not explicitly specified."""
import click

from lib.common import pass_data


@click.command()
@click.option('--source', '-s', required=True, help='The source data table.')
@click.option('--cols', '-c', required=True, multiple=True, type=str, help='The columns to be copied.')
@pass_data
def cut_columns(data, source, cols):
    """Cut the given table down to the set of provided columns. This will discard data in columns not specified."""
    s = data.get(source)
    valid_cols = []
    for col in cols:
        if col not in s.header():
            click.secho('Could not find the {} column in the source data table {}.'.format(col, source), err=True, fg='red')
        else:
            valid_cols.append(col)
    i = s.cut(*valid_cols)
    data.set(source, i)

command = cut_columns
