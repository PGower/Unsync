"""Launch an iPython shell with access to the current context."""

from IPython import embed
import unsync
import click


@unsync.command()
@click.pass_context
def ipython_shell(ctx):
    """Launch an IPython shell with access to the current context."""
    data = ctx.obj # noqa
    embed()

ipython_shell.display_name = 'shell'
