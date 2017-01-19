"""Command to generate a set of CSV's from data stored in the local data tables and upload it to Canvas."""
from __future__ import absolute_import
import click
import os
from zipfile import ZipFile
import petl
import petname

from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync
from unsync.lib.canvas_api import CanvasAPI, CanvasAPIError
from unsync.lib.canvas_meta import SIS_TYPES
from unsync.lib.jinja_templates import render


@unsync.command()
@click.option('--url', required=True, help='The url to the Canvas instance. Usually somthing like institution.instructure.com')
@click.option('--api-key', required=True, help='The API Key to use when accessing the Canvas instance.')
@click.option('--account-id', default=1, help='The Canvas Account id to apply this data set to. Defaults to the root account.')
@click.option('--data-set-id', help='The Canvas diffing data set identifier. If set this upload will be part of ')
@click.option('--remaster-data-set/--no-remaster-data-set', default=False, help='When True the remaster flag is set on the upload and the upload will be applied in full rather than diffed against other uploads in the set.')
@click.option('--batch-mode/--no-batch-mode', default=False, help='When True this data will be used as the canonical data and records that do not match will be deleted.')
@click.option('--batch-mode-term-id', help='Must be specified when --batch-mode is set. Limits deletions to a single term_id')
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
def upload_file(data, url, api_key, account_id, data_set_id, remaster_data_set, batch_mode, batch_mode_term_id, users, accounts, terms, courses, sections, enrollments, groups, group_memberships, xlists, user_observers):
    """Upload a set of CSVs to the Canvas SIS Upload API."""
    old_working_dir = os.getcwd()
    data_set_name = petname.Generate(3, "_")

    click.secho('The data set name for this upload is: {}'.format(data_set_name), fg='green')

    app_dir = click.get_app_dir('CANVAS_UNSYNC')
    app_dir = os.path.join(app_dir, data_set_name)
    if not os.path.exists(app_dir):
        # Create if it doesnt exist.
        os.mkdir(app_dir)
    click.secho('All data for this upload can be found in: {}'.format(app_dir), fg='green')

    os.chdir(app_dir)

    if not url.startswith('http') or not url.startswith('https'):
        url = 'https://' + url
        click.secho('Instance URLs should start with http or https. We will automatically fix this. New instance url: {}'.format(url), fg='red')

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
    for name, data_table in sources.items():
        spec = SIS_TYPES[name]
        header = data_table.header()
        # Check that all of the required headers exist
        missing_required_headers = [i for i in spec['required_columns'] if i not in header]
        if len(missing_required_headers) > 0:
            click.secho('Required headers: {} are missing from {}.'.format(','.join(missing_required_headers), name), fg='red')
            raise CanvasCSVValidationError('Required headers: {} are missing from {}.'.format(','.join(missing_required_headers), name))
        # Find out which headers to cut
        headers_to_cut = [i for i in spec['columns'] if i in header]
        sources[name] = data_table.cut(*headers_to_cut)

    used_data_tables = []  # The data tables that actually got zipped.
    zipfile_path = os.path.join(app_dir, 'canvas_data.zip')
    with ZipFile(zipfile_path, 'w') as z:
        for name, data_table in sources.items():
            csv_name = '{}.csv'.format(name)
            csv_path = os.path.join(app_dir, csv_name)
            if petl.nrows(data_table) > 0:
                used_data_tables += (name, )
                petl.tocsv(data_table, csv_path)
                z.write(csv_name)

    click.secho('Uploading data for the folowing SIS Data Types: {}'.format(','.join(used_data_tables)), fg='green')

    c = CanvasAPI(url, api_key)
    kwargs = {}
    if remaster_data_set:
        click.confirm('Are you sure you want to proceed with the remaster_data_set flag?', abort=True)
        kwargs['diffing_remaster_data_set'] = remaster_data_set
    if batch_mode:
        if not batch_mode_term_id:
            click.secho('If --batch-mode is set then --batch-mode-term-id must also be set.')
            raise click.Abort()
        click.confirm('Are you sure you want to proceed with batch_mode set? Data that does not appear in the uploaded dataset will be deleted.', abort=True)
        kwargs['batch_mode'] = batch_mode
        kwargs['batch_mode_term_id'] = batch_mode_term_id
    if data_set_id:
        kwargs['diffing_data_set_identifier'] = data_set_id

    if data.config.debug:
        try:
            import http.client as http_client
        except ImportError:
            # Python 2
            import httplib as http_client
        http_client.HTTPConnection.debuglevel = 1

        import logging
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    try:
        r = c.upload_sis_import_file(account_id, zipfile_path, **kwargs)
    except CanvasAPIError as e:
        click.secho('Upload has failed. {}'.format(str(e)))
    else:
        r['data_set_name'] = data_set_name
        r['data_set_path'] = app_dir
        r['used_data_tables'] = used_data_tables

        if r['response'].status_code == 200:
            click.secho(str(render('csv_upload.txt', r)), fg='green')
        else:
            click.secho(str(render('csv_upload.txt', r)), fg='red')

    # Change the workingdir back again
    os.chdir(old_working_dir)


command = upload_file


class CanvasCSVValidationError(Exception):
    pass