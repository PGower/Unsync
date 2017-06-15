import click
import petl
from unsync.lib.unsync_data import pass_data
from unsync.lib.unsync_commands import unsync


@unsync.command()
@click.option('--offset', '-o', default=0, type=int, help='Offset to begin displaying rows')
@click.option('--lines', '-n', default=50, type=int, help='How many lines to show from the table')
@click.option('--source', '-s', required=True, help='Source table to print data from.')
@click.option('--column', '-c', multiple=True, default=[None], help='Which columns should be shown? By default all columns for the selected category are shown.')
@click.option('--style', type=click.Choice(['grid', 'simple', 'minimal']), default='grid')
@pass_data
def print_to_screen(data, offset, lines, source, column, style):
    """Print out a text version of the data contained in the source table."""
    d = data.get(source)
    if offset > 0:
        d = d.rowslice(offset, offset+lines)
    if not column[0] is None:
        d = d.cut(*column)
    a = petl.look(d, limit=lines, style=style)
    click.secho('== {} =='.format(source), fg='green')
    click.echo(a)

print_to_screen.display_name = 'print'
