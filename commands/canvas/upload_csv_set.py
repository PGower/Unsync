"""Command to generate a set of CSV's from data stored in the local data tables and upload it to Canvas."""
from __future__ import absolute_import
import click
import os
from zipfile import ZipFile
import petl

from lib.unsync_data import pass_data
from lib.canvas_api import CanvasAPI


@click.command()
@click.option('--url', required=True, help='The url to the Canvas instance. Usually somthing like institution.instructure.com')
@click.option('--api-key', required=True, help='The API Key to use when accessing the Canvas instance.')
@click.option('--account-id', default=1, help='The Canvas Account id to apply this data set to. Defaults to the root account.')
@click.option('--data-set-id', help='The Canvas diffing data set identifier. If set this upload will be part of ')
@click.option('--remaster-data-set/--no-remaster-data-set', default=False, help='When True the remaster flag is set on the upload and the upload will be applied in full rather than diffed against other uploads in the set.')
@click.option('--users', default="users", help='The table holding users data to use for the upload.')
@click.option('--accounts', default="accounts", help='The table holding accounts data to use for the upload.')
@click.option('--terms', default="terms", help='The table holding terms data to use for the upload.')
@click.option('--courses', default="courses", help='The table holding courses data to use for the upload.')
@click.option('--sections', default="sections", help='The table holding sections data to use for the upload.')
@click.option('--enrollments', default="enrollments", help='The table holding enrollments data to use for the upload.')
@click.option('--groups', default="groups", help='The table holding groups data to use for the upload.')
@click.option('--group_memberships', default="group_memberships", help='The table holding group_memberships data to use for the upload.')
@click.option('--xlists', default="xlists", help='The table holding xlists data to use for the upload.')
@click.option('--user_observers', default="user_observers", help='The table holding user_observers data to use for the upload.')
@pass_data
def upload_file(data, url, api_key, account_id, data_set_id, remaster_data_set, users, accounts, terms, courses, sections, enrollments, groups, group_memberships, xlists, user_observers):
    """Upload a set of CSVs to the Canvas SIS Upload API."""
    app_dir = click.get_app_dir('CANVAS_UNSYNC')
    sources = dict([('users', data.get(users)),
                    ('accounts', data.get(accounts)),
                    ('terms', data.get(terms)),
                    ('courses', data.get(courses)),
                    ('sections', data.get(sections)),
                    ('enrollments', data.get(enrollments)),
                    ('groups', data.get(groups)),
                    ('group_memberships', data.get(group_memberships)),
                    ('xlists', data.get(xlists)),
                    ('user_observers', data.get(user_observers))])

    zipfile_path = os.path.join(app_dir, 'canvas_data.zip')
    with ZipFile(zipfile_path, 'w') as z:
        for name, data in sources.items():
            csv_path = os.path.join(app_dir, '{}.csv'.format(name))
            petl.tocsv(data, csv_path)
            z.write(csv_path)

    c = CanvasAPI(url, api_key)
    kwargs = {}
    if remaster_data_set:
        kwargs['diffing_remaster_data_set'] = remaster_data_set
    if data_set_id:
        kwargs['diffing_data_set_identifier'] = data_set_id

    r = c.upload_sis_import_file(account_id, zipfile_path, **kwargs)
    if r.status.startwsith('2'):
        click.secho(str(r), fg='green')
    else:
        click.secho(str(r), fg='red')





    with open(os.path.abspath(config), 'r') as f:
        config = yaml.load(f)

    c = CanvasAPI(config['canvas_url'], config['api_key'])

    file_path = os.path.abspath(zipfile)

    r = c.upload_sis_import_file(1, file_path, diffing_data_set_identifier=config['sync_key'], diffing_remaster_data_set=remaster)
    print str(r)



    cfg = os.path.join(click.get_app_dir(APP_NAME), 'config.ini')
    parser = ConfigParser.RawConfigParser()
    parser.read([cfg])
    rv = {}
    for section in parser.sections():
        for key, value in parser.items(section):
            rv['%s.%s' % (section, key)] = value
    return rv