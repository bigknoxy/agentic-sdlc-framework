"""agentic-sdlc init <project-name> — Initialize a new project."""

import click
from pathlib import Path

from agentic_sdlc.core.config import DEFAULT_CONFIG_YAML
from agentic_sdlc.utils.output import success, info, error, warn, step


@click.command("init")
@click.argument("project_name")
@click.pass_context
def init(ctx: click.Context, project_name: str) -> None:
    """Initialize a new or existing project with the Agentic SDLC structure.

    Creates specs/, handoffs/, adrs/, and .agentic-sdlc.yaml. Safe to run
    on an existing directory — only missing pieces are added, nothing is
    overwritten.

    Pass "." to initialize the current directory in-place.

    \b
    Examples:
        agentic-sdlc init my-api
        agentic-sdlc init .
    """
    project_dir = Path(project_name).resolve()
    in_place = project_dir == Path.cwd()
    display_name = "." if in_place else project_name
    created: list[str] = []

    # Create directory structure (additive — skip existing)
    subdirs = ["specs", "handoffs", "adrs"]
    try:
        project_dir.mkdir(parents=True, exist_ok=True)
        for subdir in subdirs:
            subdir_path = project_dir / subdir
            if not subdir_path.exists():
                subdir_path.mkdir()
                gitkeep = subdir_path / ".gitkeep"
                gitkeep.write_text("", encoding="utf-8")
                created.append(f"  {display_name}/{subdir}/")
    except OSError as exc:
        error(f"Failed to create project directories: {exc}")
        ctx.exit(1)
        return

    # Write config only if absent
    config_path = project_dir / ".agentic-sdlc.yaml"
    if not config_path.exists():
        config_name = project_dir.name if in_place else project_name
        config_content = DEFAULT_CONFIG_YAML.format(project_name=config_name)
        try:
            config_path.write_text(config_content, encoding="utf-8")
            created.append(f"  {display_name}/.agentic-sdlc.yaml")
        except OSError as exc:
            error(f"Failed to write config file: {exc}")
            ctx.exit(1)
            return

    if created:
        success(f"Initialized project: {display_name}")
        click.echo("")
        info("Created:")
        for item in created:
            step(item)
    else:
        success(f"Project already initialized: {display_name} (nothing to add)")

    click.echo("")
    info("Next steps:")
    if not in_place:
        click.echo(f"  1. cd {project_name}")
    click.echo("  Edit .agentic-sdlc.yaml to configure your project")
    click.echo("  Create your first spec:")
    click.echo('    agentic-sdlc spec create --title "My First Feature"')
