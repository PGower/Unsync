"""Copy between file systems."""
import click
import petl
# import os
import shutil

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, help='The table containing source and destination paths.')
@click.option('--source-field', required=True, default='source', help='Field containg the source path.')
@click.option('--destination-field', required=True, default='destination', help='Field containing the destination path.')
@click.option('--results', help='Table to save the results of the copy operation to.')
@click.option('--quiet/--no-quiet', default=False, help='Do not output status updates while copying.')
@pass_data
def shcopy_files(data, source, source_field, destination_field, results, quiet):
    """Copy files from the source to the destination."""
    source = data.get(source)
    results_data = []
    for i in source.dicts():
        r = {
            source_field: i[source_field],
            destination_field: i[destination_field]
        }
        try:
            shutil.copy(i[source_field], i[destination_field])
            r['success'] = True
            r['message'] = "File copied successfully."
            if not quiet:
                click.secho('Successfully copied {} to {}'.format(i[source_field], i[destination_field]), fg='green')
        except (shutil.Error, IOError) as e:
            r['success'] = False
            r['message'] = str(e)
            if not quiet:
                click.secho('Failed copying {} to {}. Reason was: {}'.format(i[source_field], i[destination_field]), str(e), fg='red')

        results_data.append(r)

    if results:
        results_data = petl.fromdicts(results_data)
        data.set(results, results_data)

command = shcopy_files
