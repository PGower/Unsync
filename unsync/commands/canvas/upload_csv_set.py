"""Command to generate a set of CSV's from data stored in the local data tables and upload it to Canvas."""
from __future__ import absolute_import
import click
import os
from zipfile import ZipFile
import petl
import petname

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
from unsync.lib.canvas_api import CanvasAPI
from unsync.lib.canvas_meta import SIS_TYPES


@unsync.command()
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
    old_working_dir = os.getcwd()

    app_dir = click.get_app_dir('CANVAS_UNSYNC')
    app_dir = os.path.join(app_dir, petname.Generate(3, "_"))
    if not os.path.exists(app_dir):
        # Create if it doesnt exist.
        os.mkdir(app_dir)

    os.chdir(app_dir)

    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url

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

    # Do some house cleaning, make sure only releveant fields are in the data.
    for name, data in sources.items():
        spec = SIS_TYPES[name]
        header = data.header()
        # Check that all of the required headers exist
        missing_required_headers = [i for i in spec['required_columns'] if i not in header]
        if len(missing_required_headers) > 0:
            raise CanvasCSVValidationError('Required headers: {} are missing from {}.'.format(','.join(missing_required_headers), name))
        # Find out which headers to cut
        headers_to_cut = [i for i in spec['columns'] if i in header]
        sources[name] = data.cut(*headers_to_cut)

    zipfile_path = os.path.join(app_dir, 'canvas_data.zip')
    with ZipFile(zipfile_path, 'w') as z:
        for name, data in sources.items():
            csv_name = '{}.csv'.format(name)
            csv_path = os.path.join(app_dir, csv_name)
            if petl.nrows(data) > 0:
                petl.tocsv(data, csv_path)
                z.write(csv_name)

    c = CanvasAPI(url, api_key)
    kwargs = {}
    if remaster_data_set:
        kwargs['diffing_remaster_data_set'] = remaster_data_set
    if data_set_id:
        kwargs['diffing_data_set_identifier'] = data_set_id

    r = c.upload_sis_import_file(account_id, zipfile_path, **kwargs)

    if r['response'].status_code == 200:
        click.secho(str(r), fg='green')
    else:
        click.secho(str(r), fg='red')

    # Change the workingdir back again
    os.chdir(old_working_dir)


command = upload_file


class CanvasCSVValidationError(Exception):
    pass