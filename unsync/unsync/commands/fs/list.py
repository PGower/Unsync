"""File system list functions. Generates an optionally recursive table of data representing the files and folders at a given path."""
import click
import petl
import os

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync

from fs import open_fs


@unsync.command()
@click.option('--path', '-p', required=True, type=str, help='The path to the file data we are going to be working with.')  # Not a click.path because it needs to accept url type paths as well.
@click.option('--destination', '-d', required=True, help='The table to store file data in.')
@pass_data
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


command = list_files
