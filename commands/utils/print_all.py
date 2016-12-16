import click
import petl
from lib.unsync_data import pass_data
from lib.unsync_commands import unsync


@unsync.command()
@click.option('--offset', '-o', default=0, type=int, help='Offset to begin displaying rows')
@click.option('--lines', '-n', default=5, type=int, help='How many lines to show from each table')
@click.option('--style', type=click.Choice(['grid', 'simple', 'minimal']), default='grid')
@pass_data
def print_all_to_screen(data, offset, lines, style):
    """Print a representation for each table currently stored."""
    for table in data.registry:
        d = data.get(table)
        if offset > 0:
            d = d.rowslice(offset, offset+lines)
        a = petl.look(d, limit=lines, style=style)
        click.secho('== {} =='.format(table), fg='green')
        click.echo(a)

command = print_all_to_screen
