"""PETL Join Command."""
from __future__ import unicode_literals

import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--strategy', '-st', required=True, default='join', type=click.Choice(['join', 'leftjoin', 'lookupjoin', 'rightjoin', 'outerjoin', 'antijoin', 'hashjoin', 'hashleftjoin', 'hashlookupjoin', 'hashrightjoin', 'hashantijoin']), help='See http://petl.readthedocs.io/en/latest/transform.html#joins')
@click.option('--source-left', '-sl', required=True, help='The "left" table in the join.')
@click.option('--source-right', '-sr', required=True, help='The "right table in the join.')
@click.option('--destination', '-d', required=True, help='The destination for the joined tables.')
@click.option('--key-left', '-kl', multiple=True, required=True, type=str, help='The key field for the left table. May be repeated to form a compound key.')
@click.option('--key-right', '-kr', multiple=True, required=True, type=str, help='The key field for the right table. May be repeated to form a compound key.')
@click.option('--prefix-left', '-pl', default=None, type=str, help='The left prefix.')
@click.option('--prefix-right', '-pr', default=None, type=str, help='The right prefix.')
@click.option('--presorted/--no-presorted', default=False, help='Are the tables presorted?')
@click.option('--buffersize', default=None, type=int, help="Controls how presorting is performed. See http://petl.readthedocs.io/en/latest/transform.html#petl.transform.sorts.sort")
@click.option('--tempdir', type=click.Path(file_okay=False, dir_okay=True, exists=True, writable=True, resolve_path=True), help='Location to store chunks when sorting.')
@click.option('--cache/--no-cache', default=True, help='Controls wether presort results are chaced for use in subsequent operations.')
@click.option('--missing', default=None, help='Value to use for fields missing in a join. Only used for certain types of join.')
@pass_data
def join(data, strategy, source_left, source_right, destination, key_left, key_right, prefix_left, prefix_right, presorted, buffersize, tempdir, cache, missing):
    """Perform a join on two data tables."""
    source_left = data.get(source_left)
    source_right = data.get(source_right)

    kwargs = {}
    if key_left == key_right:
        kwargs['key'] = key_left
    else:
        kwargs['lkey'] = key_left
        kwargs['rkey'] = key_right

    if presorted is True:
        kwargs['presorted'] = presorted

    if buffersize is not None:
        kwargs['buffersize'] = buffersize

    if tempdir:
        kwargs['tempdir'] = tempdir

    if 'anti' not in strategy:
        if prefix_left is not None:
            kwargs['lprefix'] = prefix_left
        if prefix_right is not None:
            kwargs['rprefix'] = prefix_right

    if strategy not in ['join', 'antijoin', 'hashjoin', 'hashantijoin']:
        kwargs['missing'] = missing

    if strategy == 'join':
        o = petl.join(source_left, source_right, **kwargs)
    elif strategy == 'leftjoin':
        o = petl.leftjoin(source_left, source_right, **kwargs)
    elif strategy == 'lookupjoin':
        o = petl.lookupjoin(source_left, source_right, **kwargs)
    elif strategy == 'rightjoin':
        o = petl.rightjoin(source_left, source_right, **kwargs)
    elif strategy == 'outerjoin':
        o = petl.outerjoin(source_left, source_right, **kwargs)
    elif strategy == 'antijoin':
        o = petl.antijoin(source_left, source_right, **kwargs)
    elif strategy == 'hashjoin':
        o = petl.antijoin(source_left, source_right, **kwargs)
    elif strategy == 'hashleftjoin':
        o = petl.hashleftjoin(source_left, source_right, **kwargs)
    elif strategy == 'hashlookupjoin':
        o = petl.hashlookupjoin(source_left, source_right, **kwargs)
    elif strategy == 'hashrightjoin':
        o = petl.hashrightjoin(source_left, source_right, **kwargs)

    data.set(destination, o)

command = join
