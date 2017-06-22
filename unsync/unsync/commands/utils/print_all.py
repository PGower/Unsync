import petl
import unsync


@unsync.command()
@unsync.option('--offset', '-o', default=0, type=int, help='Offset to begin displaying rows')
@unsync.option('--lines', '-n', default=5, type=int, help='How many lines to show from each table')
@unsync.option('--style', type=unsync.Choice(['grid', 'simple', 'minimal']), default='grid')
def print_all_to_screen(data, offset, lines, style):
    """Print a representation for each table currently stored."""
    for table in data.registry:
        d = data.get(table)
        if offset > 0:
            d = d.rowslice(offset, offset + lines)
        a = petl.look(d, limit=lines, style=style)
        unsync.secho('== {} =='.format(table), fg='green')
        unsync.echo(a)

print_all_to_screen.display_name = 'print_all'