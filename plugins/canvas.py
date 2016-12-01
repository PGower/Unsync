

@click.command()
@click.option('--config', default='./config.yaml')
@click.option('--show', default=2, help='Number of imports to show')
def list_imports(config, show):
    with open(os.path.abspath(config), 'r') as f:
        config = yaml.load(f)

    c = CanvasAPI(config['canvas_url'], config['api_key'])

    r = c.list_sis_imports(1)

    for count, import_data in zip(range(0, len(r['data']['sis_imports'])), r['data']['sis_imports']):
        if count <= show:
            print render('import_info.txt', {'import': import_data})
        else:
            break

cli.add_command(list_imports)



@click.command()
@click.option('--config', default='./config.yaml')
@click.option('--zipfile')
@click.option('--remaster/--no-remaster', default=None)
def upload_file(config, zipfile, remaster):
    '''Upload a file to the Canvas sis import api.'''
    with open(os.path.abspath(config), 'r') as f:
        config = yaml.load(f)

    c = CanvasAPI(config['canvas_url'], config['api_key'])

    file_path = os.path.abspath(zipfile)

    r = c.upload_sis_import_file(1, file_path, diffing_data_set_identifier=config['sync_key'], diffing_remaster_data_set=remaster)
    print str(r)
cli.add_command(upload_file)


def render(template, data={}):
    env = jinja2_env()
    template = env.get_template(template)
    return template.render(**data)


def jinja2_env():
    return Environment(loader=FileSystemLoader(os.path.join(BASE_PATH, 'templates')), trim_blocks=True)

def ad_conn():
s1 = ldap3.Server('10.192.81.55')
s2 = ldap3.Server('10.192.81.54')
pool = ldap3.ServerPool([s1, s2])
conn = ldap3.Connection(server=pool,
                        user='CN=LDAPBinder,OU=System,OU=SMCUsers,DC=stmonicas,DC=qld,DC=edu,DC=au',
                        password='5tm0NICa5198SIx')
return conn


import petl
import yaml
import ldap3
import re
import csv
import os
import requests
from canvas_api import CanvasAPI
import arrow
import click
from jinja2 import Environment, FileSystemLoader