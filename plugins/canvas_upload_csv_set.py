"""Command to generate a set of CSV's from data stored in the local data tables and upload it to Canvas."""
from __future__ import absolute_import
import click
import os

from .common import pass_data
from 

@click.command()

@click.option('--remaster/--no-remaster', default=None)
def upload_file(config, zipfile, remaster):
    '''Upload a file to the Canvas sis import api.'''
    with open(os.path.abspath(config), 'r') as f:
        config = yaml.load(f)

    c = CanvasAPI(config['canvas_url'], config['api_key'])

    file_path = os.path.abspath(zipfile)

    r = c.upload_sis_import_file(1, file_path, diffing_data_set_identifier=config['sync_key'], diffing_remaster_data_set=remaster)
    print str(r)

