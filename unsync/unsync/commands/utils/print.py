import unsync
import petl


@unsync.command()
@unsync.option('--offset', '-o', default=0, type=int, help='Offset to begin displaying rows')
@unsync.option('--lines', '-n', default=50, type=int, help='How many lines to show from the table')
@unsync.option('--source', '-s', required=True, help='Source table to print data from.')
@unsync.option('--column', '-c', multiple=True, default=[None], help='Which columns should be shown? By default all columns for the selected category are shown.')
@unsync.option('--style', type=unsync.Choice(['grid', 'simple', 'minimal']), default='grid')
def print_to_screen(data, offset, lines, source, column, style):
    """Print out a text version of the data contained in the source table."""
    d = data.get(source)
    if offset > 0:
        d = d.rowslice(offset, offset + lines)
    if not column[0] is None:
        d = d.cut(*column)
    a = petl.look(d, limit=lines, style=style)
    unsync.secho('== {} =='.format(source), fg='green')
    unsync.echo(a)

print_to_screen.display_name = 'print'
