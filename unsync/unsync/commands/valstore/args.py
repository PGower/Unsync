import click
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--pair', multiple=True, required=True, type=click.Tuple([str, str]), help='Store the given data as a (key, value) pair.')
@pass_data
def from_args(data, pair):
    """Load valstore key value pairs from the provided pair arguments given to this command."""
    for k,v in pair:
        if k in data.values:
            click.secho(f'Valstore data already exists for the {k} key. This will be overwritten.', fg='red')
    data.values.update(dict(pair))
