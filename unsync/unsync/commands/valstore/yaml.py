import yaml
import unsync


@unsync.command()
@unsync.option('--values-data', multiple=True, required=False, type=unsync.Path(exists=True, dir_okay=False, readable=True, resolve_path=True), help='Read data from a YAML file and update the data.values store. This is shared between all commands.')
def from_yaml(data, values_data):
    """Load key value data from the provided YAML file and load it into the valstore. Existing keys with the same name will be overwritten."""
    if values_data is not None and len(values_data) >= 1:
        for values_data_file in values_data:
            with open(values_data_file, 'r') as f:
                try:
                    yaml_data = yaml.load(f)
                except yaml.scanner.ScannerError as e:
                    unsync.secho(f'An error occured processing the values data in: {values_data_file}', fg='red')
                    unsync.secho(str(e), fg='red')
                else:
                    for k in yaml_data.keys():
                        if k in data.values:
                            unsync.secho(f'Values data already exists for the {k} key. This will be overwritten in the current context.', fg='red')
                    data.values.update(yaml_data)


@unsync.command()
@unsync.option('--output-file', '-o', required=True, type=unsync.Path(dir_okay=False, readable=True, resolve_path=True), help='File to export valstore data to.')
def to_yaml(data, output_file):
    """Dump the current key value data from the valstore into the given output file in YAML format."""
    yaml_data = yaml.dumps(data.values)
    with open(output_file, 'w+') as f:
        f.write(yaml_data)
