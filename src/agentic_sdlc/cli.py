"""Main CLI entry point for the Agentic SDLC Framework."""

import click
from colorama import init as colorama_init

from agentic_sdlc import __version__
from agentic_sdlc.commands.init import init
from agentic_sdlc.commands.spec import spec
from agentic_sdlc.commands.handoff import handoff
from agentic_sdlc.commands.check import check
from agentic_sdlc.commands.metrics import metrics


# Initialize colorama for Windows ANSI support
colorama_init(autoreset=True)


@click.group()
@click.version_option(version=__version__, prog_name="agentic-sdlc")
def cli() -> None:
    """Agentic SDLC Framework CLI.

    Governance, specs, and guardrails for AI-assisted development.
    Use this tool to initialize projects, create and validate specs,
    manage handoff packets, run guardrail checks, and view metrics.
    """


cli.add_command(init)
cli.add_command(spec)
cli.add_command(handoff)
cli.add_command(check)
cli.add_command(metrics)
