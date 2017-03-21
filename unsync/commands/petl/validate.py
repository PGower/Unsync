"""PETL Validate Command."""
from __future__ import unicode_literals

import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--name', type=str, help='A name for this validation step. Will be printed in the output. Cosmetic only.')
@click.option('--source', '-s', required=True, type=str, help='Name of the source data table/s.')
@click.option('--header', '-h', multiple=True, type=str, help='The set of required headers.')
@click.option('--test', '-t', multiple=True, type=click.Tuple([str, str, str]), help='Apply a test to a row/value and pass if no Exception is raised. \
                                                                                                  Tests are specified as 3 strings, first is a name \
                                                                                                  for the test, second is the fieldname to test against or \
                                                                                                  the special name __row__ to test the entire row and the \
                                                                                                  third is a string which will be evaluated with eval()')
@click.option('--assertion', '-a', multiple=True, type=click.Tuple([str, str, str]), help='Apply an assertion to a row/value and pass if the assertion returns True. \
                                                                                                       Assertions are specified as 3 strings, first is a name \
                                                                                                       for the assertion, second is the fieldname to test against or \
                                                                                                       the special name __row__ to test the entire row and the \
                                                                                                       third is a string which will be evaluated with eval()')
@pass_data
def petl_validate(data, name, source, header, test, assertion):
    """Validate that a table meets the required constraints."""
    s = data.get(source)

    if name:
        name = name + ' '
    else:
        name = ''

    constraints = []
    for c_data in test:
        constraint = {'name': c_data[0]}
        if c_data[1] != '_row_':
            constraint['field'] = c_data[1]
        constraint['test'] = eval(c_data[2])
        constraints.append(constraint)

    for c_data in assertion:
        constraint = {'name': c_data[0]}
        if c_data[1] != '_row_':
            constraint['field'] = c_data[1]
        constraint['assertion'] = eval(c_data[2])
        constraints.append(constraint)         

    params = {}
    if header is not None and len(header) != 0:
        params['header'] = header
    if len(constraints) != 0:
        params['constraints'] = constraints

    problems = petl.validate(s, **params)

    if problems.nrows() > 0:
        click.secho('{}Validation Failed!'.format(name), fg='red')
        click.secho(str(problems.lookall()), fg='red')
        raise PETLValidationError(problems)
    else:
        if data.config.debug is True:
            click.secho('{}Validation Passed!'.format(name), fg='green')

command = petl_validate


class PETLValidationError(Exception):
    def __init__(self, error_table):
        self.error_table = error_table

    def __unicode__(self):
        return str(self.error_table.lookall())