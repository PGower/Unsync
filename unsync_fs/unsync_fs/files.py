"""File system list functions. Generates an optionally recursive table of data representing the files and folders at a given path."""
import unsync
import petl
import os

from fs import open_fs
import shutil


@unsync.command()
@unsync.option('--path', '-p', required=True, type=str, help='The path to the file data we are going to be working with.')  # Not a click.path because it needs to accept url type paths as well.
@unsync.option('--destination', '-d', required=True, help='The table to store file data in.')
def list_files(data, path, destination):
    """List files in the given directory and save them in the destination table."""
    walk_data = []
    full_path = os.path.abspath(path)

    filesystem = open_fs(full_path)
    for info in filesystem.scandir('./', namespaces=['details', 'access']):
        file_data = {}
        file_data['name'] = info.name  # name
        file_data['path'] = os.path.normcase(info.make_path(full_path))  # path
        file_data['created'] = info.created
        file_data['accessed'] = info.accessed
        file_data['modified'] = info.modified
        file_data['size'] = info.size  # size bytes
        kind = info.type
        if kind == 4:
            file_data['type'] = 'block_special_file'
        elif kind == 3:
            file_data['type'] = 'character'
        elif kind == 1:
            file_data['type'] = 'directory'
        elif kind == 5:
            file_data['type'] = 'fifo'
        elif kind == 2:
            file_data['type'] = 'file'
        elif kind == 6:
            file_data['type'] = 'socket'
        elif kind == 7:
            file_data['type'] = 'symlink'
        else:
            file_data['type'] = 'unknown'
        file_data['user'] = info.user
        file_data['uid'] = info.uid
        file_data['group'] = info.group
        file_data['gid'] = info.gid
        file_data['permissions'] = info.permissions.as_str()

        walk_data.append(file_data)

    walk_data = petl.fromdicts(walk_data)
    data.set(destination, walk_data)

list_files.display_name = 'list'


@unsync.command()
@unsync.option('--source', '-s', required=True, help='The table containing source and destination paths.')
@unsync.option('--source-field', required=True, default='source', help='Field containg the source path.')
@unsync.option('--destination-field', required=True, default='destination', help='Field containing the destination path.')
@unsync.option('--results', help='Table to save the results of the copy operation to.')
@unsync.option('--quiet/--no-quiet', default=False, help='Do not output status updates while copying.')
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
                unsync.secho('Successfully copied {} to {}'.format(i[source_field], i[destination_field]), fg='green')
        except (shutil.Error, IOError) as e:
            r['success'] = False
            r['message'] = str(e)
            if not quiet:
                unsync.secho('Failed copying {} to {}. Reason was: {}'.format(i[source_field], i[destination_field]), str(e), fg='red')

        results_data.append(r)

    if results:
        results_data = petl.fromdicts(results_data)
        data.set(results, results_data)

shcopy_files.display_name = 'copy'
