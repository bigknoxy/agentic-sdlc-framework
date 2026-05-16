"""agentic-sdlc init <project-name> — Initialize a new project."""

import click
from pathlib import Path

from agentic_sdlc.core.config import DEFAULT_CONFIG_YAML
from agentic_sdlc.utils.output import success, info, error, warn, step


@click.command("init")
@click.argument("project_name")
@click.pass_context
def init(ctx: click.Context, project_name: str) -> None:
    """Initialize a new Agentic SDLC project.

    Creates a project directory with the standard structure: specs/,
    handoffs/, adrs/, and a .agentic-sdlc.yaml config file.

    \b
    Example:
        agentic-sdlc init my-api
    """
    project_dir = Path(project_name)

    if project_dir.exists():
        error(f"Directory already exists: {project_dir}")
        ctx.exit(1)
        return

    # Create directory structure
    subdirs = ["specs", "handoffs", "adrs"]
    try:
        project_dir.mkdir(parents=True)
        for subdir in subdirs:
            (project_dir / subdir).mkdir()
    except OSError as exc:
        error(f"Failed to create project directory: {exc}")
        ctx.exit(1)
        return

    # Write config file
    config_path = project_dir / ".agentic-sdlc.yaml"
    config_content = DEFAULT_CONFIG_YAML.format(project_name=project_name)
    try:
        config_path.write_text(config_content, encoding="utf-8")
    except OSError as exc:
        error(f"Failed to write config file: {exc}")
        ctx.exit(1)
        return

    # Write a .gitkeep in each subdir so they show up in git
    for subdir in subdirs:
        gitkeep = project_dir / subdir / ".gitkeep"
        gitkeep.write_text("", encoding="utf-8")

    success(f"Initialized project: {project_name}/")
    click.echo("")
    info("Project structure created:")
    for subdir in subdirs:
        step(f"  {project_name}/{subdir}/")
    step(f"  {project_name}/.agentic-sdlc.yaml")

    click.echo("")
    info("Next steps:")
    click.echo(f"  1. cd {project_name}")
    click.echo("  2. Edit .agentic-sdlc.yaml to configure your project")
    click.echo("  3. Create your first spec:")
    click.echo('       agentic-sdlc spec create --title "My First Feature"')
