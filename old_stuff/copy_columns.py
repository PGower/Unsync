"""Utility command to copy columns from one table to another. Copied columns are catted to the bottom of existing data."""
import click

from lib.common import pass_data


@click.command()
@click.option('--source', '-s', required=True, help='The source data table.')
@click.option('--destination', '-d', required=True, help='The destination data table.')
@click.option('--cols', '-c', required=True, multiple=True, type=str, help='The columns to be copied.')
@click.option('--overwrite/--no-overwrite', default=False, help='If set then all data in the destination table will be replaced. Otherwise new columns will be catted to existing table.')
@pass_data
def copy_columns(data, source, destination, cols, overwrite):
    """Copy columns from the source table to the destination table."""
    s = data.get(source)
    valid_cols = []
    for col in cols:
        if col not in s.header():
            click.secho('Could not find the {} column in the source data table {}.'.format(col, source), err=True, fg='red')
        else:
            valid_cols.append(col)
    i = s.cut(*valid_cols)
    if overwrite:
        data.set(destination, i)
    else:
        data.cat(destination, i)

command = copy_columns
