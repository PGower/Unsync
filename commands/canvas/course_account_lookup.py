"""Canvas specific command to assign sis_account_ids to courses based on their course_id."""

import click
from lib.common import pass_data
import re


@click.command()
@click.option('--courses', required=True, type=unicode, help='The source courses table containing courses to be merged.')
@click.option('--course-id-field', required=True, type=unicode, default='course_id', help='The field name for the courses id. Defaults to Canvas standard course_id.')
@click.option('--account-id-field', required=True, type=unicode, default='account_id', help='The field name for the account id. Defaults to Canvas standard account_id.')
@click.option('--account-data', required=True, type=unicode, help='Table containing pairs of Account Names and Matching Regexes.')
@click.option('--missing-account', default=None, help='Value to use if no match is made.')
@pass_data
def account_lookup(data, courses, course_id_field, account_id_field, account_data, missing_account):
    """Assign accounts to courses where the course id matches the account regex."""
    courses_table = data.get(courses)
    account_data = data.get(account_data)

    # Massage the account data into something more useable
    account_lookup = account_data.cut('regex', 'account_id')
    account_lookup = account_lookup.listoftuples()
    account_lookup = dict([(re.compile(i[0]), i[1]) for i in account_lookup])

    def account_lookup_func(rec):
        for r, v in account_lookup.items():
            if r.match(getattr(rec, course_id_field)):
                return v
        return missing_account


    courses_table = courses_table.addfield(account_id_field, account_lookup_func)
    data.set(courses, courses_table)

command = account_lookup
