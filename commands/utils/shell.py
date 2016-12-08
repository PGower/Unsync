"""Launch an iPython shell with access to the current context."""

import click
from IPython import embed


@click.command()
@click.pass_context
def shell_now(ctx):
    """Launch an IPython shell with access to the current context."""
    data = ctx.obj # noqa
    embed()

command = shell_now
