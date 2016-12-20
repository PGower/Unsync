"""Launch an iPython shell with access to the current context."""

from IPython import embed
from unsync.lib.unsync_commands import unsync
import click


@unsync.command()
@click.pass_context
def shell_now(ctx):
    """Launch an IPython shell with access to the current context."""
    data = ctx.obj # noqa
    embed()

command = shell_now
