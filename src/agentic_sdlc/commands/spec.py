"""agentic-sdlc spec — Create, validate, and list spec files."""

import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import click
from tabulate import tabulate

from agentic_sdlc.core.config import load_config
from agentic_sdlc.core.templates import get_spec_template
from agentic_sdlc.core.validation import validate_spec, validate_spec_directory
from agentic_sdlc.utils.output import success, info, error, warn, step, header


@click.group("spec")
def spec() -> None:
    """Manage agent-ready specification files.

    \b
    Commands:
        create    Create a new spec from template
        validate  Validate one or all specs
        list      List all specs in a table
    """


# ---------------------------------------------------------------------------
# spec create
# ---------------------------------------------------------------------------

@spec.command("create")
@click.option("--title", required=True, help="Human-readable title for the spec.")
@click.option(
    "--priority",
    default="p1",
    type=click.Choice(["p0", "p1", "p2"], case_sensitive=False),
    show_default=True,
    help="Priority level: p0 (critical), p1 (high), p2 (normal).",
)
@click.option(
    "--template",
    default="api",
    type=click.Choice(["api", "web", "ml", "generic"], case_sensitive=False),
    show_default=True,
    help="Spec template type.",
)
@click.option(
    "--specs-dir",
    default=None,
    help="Override the specs directory (default: specs/ relative to config or CWD).",
)
def spec_create(title: str, priority: str, template: str, specs_dir: Optional[str]) -> None:
    """Create a new agent-ready spec from template.

    \b
    Example:
        agentic-sdlc spec create --title "User Auth Service" --priority p1
        agentic-sdlc spec create --title "ML Pipeline" --template ml --priority p0
    """
    cfg = load_config()
    specs_path = Path(specs_dir) if specs_dir else Path(cfg.get("templates", {}).get("specs_dir", "specs"))

    # Auto-increment spec ID
    today = date.today().strftime("%Y-%m-%d")
    spec_id = _next_spec_id(specs_path, today)

    filename = f"{spec_id}.md"
    output_path = specs_path / filename

    # Ensure specs directory exists
    try:
        specs_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        error(f"Cannot create specs directory: {exc}")
        sys.exit(1)

    # Render template
    content = get_spec_template()
    content = content.replace("SPEC-YYYY-MM-DD-001", spec_id)
    content = content.replace("[Feature/Workflow Name]", title)
    content = content.replace("priority: p1", f"priority: {priority.lower()}")
    content = content.replace(
        "template_version: 1.0.0",
        f"template_version: 1.0.0\nspec_template: {template}",
    )

    try:
        output_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        error(f"Failed to write spec file: {exc}")
        sys.exit(1)

    success(f"Spec created: {output_path}")
    info(f"  Spec ID:  {spec_id}")
    info(f"  Title:    {title}")
    info(f"  Priority: {priority.upper()}")
    click.echo("")
    step("Fill in the template sections and run:")
    click.echo(f"  agentic-sdlc spec validate {output_path}")


# ---------------------------------------------------------------------------
# spec validate
# ---------------------------------------------------------------------------

@spec.command("validate")
@click.argument("path", required=False, default=None)
@click.option("--strict", is_flag=True, default=False, help="Treat warnings as errors.")
@click.option(
    "--specs-dir",
    default=None,
    help="Override the specs directory (default: specs/).",
)
def spec_validate(path: Optional[str], strict: bool, specs_dir: Optional[str]) -> None:
    """Validate one spec or all specs in the specs/ directory.

    If PATH is omitted, all *.md files in specs/ are validated.

    \b
    Examples:
        agentic-sdlc spec validate
        agentic-sdlc spec validate specs/SPEC-2025-01-15-001.md
        agentic-sdlc spec validate specs/SPEC-2025-01-15-001.md --strict
    """
    cfg = load_config()

    if path:
        spec_path = Path(path)
        if not spec_path.exists():
            error(f"File not found: {spec_path}")
            sys.exit(1)

        header(f"Validating {spec_path}")
        valid, errors = validate_spec(spec_path)
        if valid:
            success("Spec validation passed")
        else:
            error("Spec validation failed")
            for e in errors:
                click.echo(f"  {click.style('x', fg='red')} {e}")
            sys.exit(1)
    else:
        specs_dir_path = Path(specs_dir) if specs_dir else Path(
            cfg.get("templates", {}).get("specs_dir", "specs")
        )
        if not specs_dir_path.exists():
            warn(f"Specs directory not found: {specs_dir_path}")
            sys.exit(0)

        header(f"Validating all specs in {specs_dir_path}/")
        total, passed, all_errors = validate_spec_directory(specs_dir_path)

        click.echo("")
        if total == 0:
            warn("No spec files found.")
        elif passed == total:
            success(f"All {total} spec(s) passed validation.")
        else:
            failed = total - passed
            error(f"{failed}/{total} spec(s) failed validation.")
            for msg in all_errors:
                click.echo(f"  {click.style('x', fg='red')} {msg}")
            sys.exit(1)


# ---------------------------------------------------------------------------
# spec list
# ---------------------------------------------------------------------------

@spec.command("list")
@click.option(
    "--specs-dir",
    default=None,
    help="Override the specs directory (default: specs/).",
)
def spec_list(specs_dir: Optional[str]) -> None:
    """List all specs with ID, title, status, and priority.

    \b
    Example:
        agentic-sdlc spec list
    """
    cfg = load_config()
    specs_dir_path = Path(specs_dir) if specs_dir else Path(
        cfg.get("templates", {}).get("specs_dir", "specs")
    )

    if not specs_dir_path.exists():
        warn(f"Specs directory not found: {specs_dir_path}")
        return

    rows = []
    for spec_file in sorted(specs_dir_path.glob("*.md")):
        meta = _parse_frontmatter(spec_file)
        if meta:
            rows.append([
                meta.get("spec_id", spec_file.stem),
                meta.get("title", "(no title)"),
                meta.get("status", "unknown"),
                meta.get("priority", "-"),
            ])

    if not rows:
        warn("No specs found.")
        return

    header("Specs")
    click.echo(tabulate(
        rows,
        headers=["Spec ID", "Title", "Status", "Priority"],
        tablefmt="simple",
    ))
    click.echo(f"\n{len(rows)} spec(s) total.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _next_spec_id(specs_dir: Path, today: str) -> str:
    """Generate the next SPEC-YYYY-MM-DD-NNN ID."""
    prefix = f"SPEC-{today}-"
    existing = []
    if specs_dir.exists():
        for f in specs_dir.glob(f"SPEC-{today}-*.md"):
            m = re.search(r"SPEC-\d{4}-\d{2}-\d{2}-(\d+)", f.name)
            if m:
                existing.append(int(m.group(1)))
    next_num = (max(existing) + 1) if existing else 1
    return f"{prefix}{next_num:03d}"


def _parse_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    import re as _re
    match = _re.match(r"^---\n(.*?)\n---", content, _re.DOTALL)
    if not match:
        return {}

    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith("#"):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta
