"""PETL Validate Command."""
import click
import petl
from lib.unsync_data import pass_data
from lib.unsync_commands import unsync


@unsync.command()
@click.option('--source', '-s', required=True, type=unicode, help='Name of the source data table/s.')
@click.option('--header', '-h', multiple=True, type=unicode, help='The set of required headers.')
@click.option('--test', '-t', multiple=True, type=click.Tuple([unicode, unicode, unicode]), help='Apply a test to a row/value and pass if no Exception is raised. \
                                                                                                  Tests are specified as 3 strings, first is a name \
                                                                                                  for the test, second is the fieldname to test against or \
                                                                                                  the special name __row__ to test the entire row and the \
                                                                                                  third is a string which will be evaluated with eval()')
@click.option('--assertion', '-a', multiple=True, type=click.Tuple([unicode, unicode, unicode]), help='Apply an assertion to a row/value and pass if the assertion returns True. \
                                                                                                       Assertions are specified as 3 strings, first is a name \
                                                                                                       for the assertion, second is the fieldname to test against or \
                                                                                                       the special name __row__ to test the entire row and the \
                                                                                                       third is a string which will be evaluated with eval()')
@pass_data
def petl_update(data, source, header, test, assertion):
    """Validate that a table meets the required constraints."""
    s = data.get(source)

    constraints = []
    for kind, data in zip(['test' for i in test], test) + zip(['assertion' for i in assertion], assertion):
        constraint = {'name': data[0]}
        if data[1] != '_row_':
            constraint['field'] = data[1]
        if kind == 'test':
            constraint['test'] = eval(data[2], 'petl_validate', {})
        if kind == 'assertion':
            constraint['assertion'] = eval(data[2], 'petl_validate', {})

    params = {}
    if header and len(header != 0):
        params['header'] = header
    if len(constraints) != 0:
        params['constraints'] = constraints

    problems = petl.validate(s, **params)

    if problems.nrows() > 0:
        click.secho('Validation Failed!', fg='red')
        click.secho(problems.lookall(), fg='red')
        raise PETLValidationError(problems)
    else:
        if data.config.debug is True:
            click.secho('Validation Passed!', fg='green')

command = petl_update


class PETLValidationError(Exception):
    def __init__(self, error_table):
        self.error_table = error_table

    def __unicode__(self):
        return self.error_table.lookall()