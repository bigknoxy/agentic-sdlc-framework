"""Colorized console output helpers.

Uses Click's built-in ANSI support (backed by colorama on Windows).
All helpers write to stdout unless noted otherwise.
"""

import click


def success(message: str) -> None:
    """Print a green success message with a checkmark prefix."""
    click.echo(click.style(f"  {message}", fg="green", bold=True))


def error(message: str) -> None:
    """Print a red error message with an X prefix."""
    click.echo(click.style(f"  {message}", fg="red", bold=True))


def warn(message: str) -> None:
    """Print a yellow warning message."""
    click.echo(click.style(f"  {message}", fg="yellow"))


def info(message: str) -> None:
    """Print a cyan info message."""
    click.echo(click.style(f"{message}", fg="cyan"))


def step(message: str) -> None:
    """Print a dim step/hint message."""
    click.echo(click.style(f"{message}", dim=True))


def header(title: str) -> None:
    """Print a bold section header with an underline separator."""
    click.echo("")
    click.echo(click.style(title, bold=True, underline=True))
