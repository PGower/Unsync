"""Utility command to cutout columns in a table. Removes only those columns specified. (Opposite of cut_columns)."""
import click

from .common import pass_data


@click.command()
@click.option('--source', '-s', required=True, help='The source data table.')
@click.option('--cols', '-c', required=True, multiple=True, type=str, help='The columns to be copied.')
@pass_data
def cutout_columns(data, source, cols):
    """Cut the specified columns out of the table."""
    s = data.get(source)
    valid_cols = []
    for col in cols:
        if col not in s.header():
            click.secho('Could not find the {} column in the source data table {}.'.format(col, source), err=True, fg='red')
        else:
            valid_cols.append(col)
    i = s.cutout(*valid_cols)
    data.set(source, i)

command = cutout_columns
