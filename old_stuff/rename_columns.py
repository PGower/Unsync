"""Utility command to rename columns in a local data table."""
import click

from lib.common import pass_data


@click.command()
@click.option('--rename', '-r', multiple=True, type=click.Tuple([unicode, unicode]), required=True, help='Rename columns, first param is from, second is to.')
@click.option('--source', '-s', required=True, help='The local data table to use for renaming.')
@pass_data
def rename_columns(data, rename, source):
    """Rename columns from the source data table."""
    d = data.get(source)
    for pair in rename:
        if pair[0] not in d.header():
            click.secho('Could not find the {} column in the data table {}'.format(pair[0], source), err=True, fg='red')
        else:
            d = d.rename(pair[0], pair[1])
    data.set(source, d)

command = rename_columns
