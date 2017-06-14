import click
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--value', multiple=True, required=True, type=click.Tuple([str, str]), help='Store the given data as a (key, value) pair.')
@pass_data
def values_from_args(data, value):
    for k,v in value:
        if k in data.values:
            click.secho(f'Values data already exists for the {k} key. This will be overwritten in the current context.', fg='red')
    data.values.update(dict(value))

command = values_from_args
