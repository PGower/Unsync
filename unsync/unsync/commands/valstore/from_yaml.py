import yaml
import click
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--values-data', multiple=True, required=False, type=click.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Read data from a YAML file and update the data.values store. This is shared between all commands.')
@pass_data
def values_from_yaml(data, values_data):
    # Process any values data given.
    if values_data is not None and len(values_data) >= 1:
        for values_data_file in values_data:
            with open(values_data_file, 'r') as f:
                try:
                    yaml_data = yaml.load(f)
                except yaml.scanner.ScannerError as e:
                    click.secho(f'An error occured processing the values data in: {values_data_file}', fg='red')
                    click.secho(str(e), fg='red')
                else:
                    for k in yaml_data.keys():
                        if k in data.values:
                            click.secho(f'Values data already exists for the {k} key. This will be overwritten in the current context.', fg='red')
                    data.values.update(yaml_data)

command = values_from_yaml
