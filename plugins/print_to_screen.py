from __future__ import absolute_import
import click
import petl
from .common import KINDS, KIND_NAMES, pass_data, UnsyncData


# def validate_show(ctx, param, value):
#     """If show is specified then the columns provided must belong to the kind selected."""
#     if len(value) == 1 and value[0] is None:
#         return [None]
#     else:
#         kind = ctx.params['kind']
#         # o = ctx.find_object(UnsyncData)
#         valid_columns = KINDS[kind]['columns']
#         # valid_columns += getattr(o, kind).header()
#         # valid_columns = set(valid_columns)
#         import pdb;pdb.set_trace()
#         invalid_columns = []
#         for col in value:
#             if col not in valid_columns:
#                 invalid_columns.append(col)
#         if len(invalid_columns) > 0:
#             raise click.BadParameter('{} are not valid columns for kind {}. Allowed columns are {}'.format(invalid_columns, kind, valid_columns))
#         else:
#             return value


@click.command()
@click.option('--offset', '-o', default=0, type=int, help='Offset to begin displaying rows')
@click.option('--lines', '-n', default=50, type=int, help='How many lines to show from the table')
@click.option('--kind', '-k', type=click.Choice(KIND_NAMES), required=True)
@click.option('--show', '-s', multiple=True, default=[None], help='Which columns should be shown? By default all columns for the selected category are shown.')
@click.option('--style', type=click.Choice(['grid', 'simple', 'minimal']), default='grid')
@pass_data
def print_to_screen(data, offset, lines, kind, show, style):
    """Print a text representation of the data table for a given KIND."""
    d = getattr(data, kind)
    if offset > 0:
        d = d.rowslice(offset, offset+lines)
    if not show[0] is None:
        d = d.cut(*show)
    a = petl.look(d, limit=lines, style=style)
    click.echo(a)
