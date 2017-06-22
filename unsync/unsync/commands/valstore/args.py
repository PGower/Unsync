import unsync


@unsync.command()
@unsync.option('--pair', multiple=True, required=True, type=unsync.Tuple([str, str]), help='Store the given data as a (key, value) pair.')
def from_args(data, pair):
    """Load valstore key value pairs from the provided pair arguments given to this command."""
    for k,v in pair:
        if k in data.values:
            unsync.secho(f'Valstore data already exists for the {k} key. This will be overwritten.', fg='red')
    data.values.update(dict(pair))
