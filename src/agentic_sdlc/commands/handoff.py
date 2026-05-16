"""agentic-sdlc handoff — Create, validate, and list handoff packets."""

import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import click
from tabulate import tabulate

from agentic_sdlc.core.config import load_config
from agentic_sdlc.core.templates import get_handoff_template
from agentic_sdlc.core.validation import validate_handoff, validate_handoff_directory
from agentic_sdlc.utils.output import success, info, error, warn, step, header


@click.group("handoff")
def handoff() -> None:
    """Manage agent handoff packets.

    \b
    Commands:
        create    Create a new handoff packet from template
        validate  Validate one or all handoff packets
        list      List all handoff packets in a table
    """


# ---------------------------------------------------------------------------
# handoff create
# ---------------------------------------------------------------------------

@handoff.command("create")
@click.option("--milestone", required=True, help="Milestone name or number (e.g. 'M1' or '1').")
@click.option(
    "--agent",
    default="claude-code",
    show_default=True,
    help="Agent ID that produced this handoff.",
)
@click.option(
    "--supervisor",
    default="human",
    show_default=True,
    help="Human supervisor overseeing this handoff.",
)
@click.option(
    "--handoffs-dir",
    default=None,
    help="Override the handoffs directory (default: handoffs/).",
)
def handoff_create(
    milestone: str,
    agent: str,
    supervisor: str,
    handoffs_dir: Optional[str],
) -> None:
    """Create a new handoff packet from template.

    \b
    Example:
        agentic-sdlc handoff create --milestone "M1" --agent "claude-code"
        agentic-sdlc handoff create --milestone "Milestone 2" --supervisor "josh@example.com"
    """
    cfg = load_config()
    handoffs_path = Path(handoffs_dir) if handoffs_dir else Path(
        cfg.get("templates", {}).get("handoffs_dir", "handoffs")
    )

    # Determine agent role for packet_id
    agent_role = "executor"
    if "planner" in agent.lower():
        agent_role = "planner"

    # Auto-increment packet number
    packet_num = _next_handoff_num(handoffs_path, agent_role)
    packet_id = f"HANDOFF-{agent_role}-{packet_num:03d}"
    filename = f"HANDOFF-{packet_num:03d}.md"
    output_path = handoffs_path / filename

    today = date.today().strftime("%Y-%m-%d")

    try:
        handoffs_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        error(f"Cannot create handoffs directory: {exc}")
        sys.exit(1)

    content = get_handoff_template()
    content = content.replace("HANDOFF-[planner|executor]-###", packet_id)
    content = content.replace("[Number/Name]", milestone)
    content = content.replace("YYYY-MM-DD", today, 1)  # only first occurrence (frontmatter date)
    content = content.replace('[Agent ID - e.g., "claude-code-001"]', agent)
    content = content.replace('[Human owner - e.g., "josh@apexfinancial.example.com"]', supervisor)
    content = content.replace("[Milestone Name]", milestone)

    try:
        output_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        error(f"Failed to write handoff packet: {exc}")
        sys.exit(1)

    success(f"Handoff packet created: {output_path}")
    info(f"  Packet ID:  {packet_id}")
    info(f"  Milestone:  {milestone}")
    info(f"  Agent:      {agent}")
    info(f"  Supervisor: {supervisor}")
    click.echo("")
    step("Fill in the template sections and run:")
    click.echo(f"  agentic-sdlc handoff validate {output_path}")


# ---------------------------------------------------------------------------
# handoff validate
# ---------------------------------------------------------------------------

@handoff.command("validate")
@click.argument("path", required=False, default=None)
@click.option("--strict", is_flag=True, default=False, help="Treat warnings as errors.")
@click.option(
    "--handoffs-dir",
    default=None,
    help="Override the handoffs directory (default: handoffs/).",
)
def handoff_validate(path: Optional[str], strict: bool, handoffs_dir: Optional[str]) -> None:
    """Validate one handoff packet or all packets in handoffs/.

    If PATH is omitted, all *.md files in handoffs/ are validated.

    \b
    Examples:
        agentic-sdlc handoff validate
        agentic-sdlc handoff validate handoffs/HANDOFF-001.md
        agentic-sdlc handoff validate handoffs/HANDOFF-001.md --strict
    """
    cfg = load_config()

    if path:
        packet_path = Path(path)
        if not packet_path.exists():
            error(f"File not found: {packet_path}")
            sys.exit(1)

        header(f"Validating {packet_path}")
        valid, errors = validate_handoff(packet_path)
        if valid:
            success("Handoff validation passed")
        else:
            error("Handoff validation failed")
            for e in errors:
                click.echo(f"  {click.style('x', fg='red')} {e}")
            sys.exit(1)
    else:
        handoffs_dir_path = Path(handoffs_dir) if handoffs_dir else Path(
            cfg.get("templates", {}).get("handoffs_dir", "handoffs")
        )
        if not handoffs_dir_path.exists():
            warn(f"Handoffs directory not found: {handoffs_dir_path}")
            sys.exit(0)

        header(f"Validating all handoffs in {handoffs_dir_path}/")
        total, passed, all_errors = validate_handoff_directory(handoffs_dir_path)

        click.echo("")
        if total == 0:
            warn("No handoff packets found.")
        elif passed == total:
            success(f"All {total} handoff packet(s) passed validation.")
        else:
            failed = total - passed
            error(f"{failed}/{total} handoff packet(s) failed validation.")
            for msg in all_errors:
                click.echo(f"  {click.style('x', fg='red')} {msg}")
            sys.exit(1)


# ---------------------------------------------------------------------------
# handoff list
# ---------------------------------------------------------------------------

@handoff.command("list")
@click.option(
    "--handoffs-dir",
    default=None,
    help="Override the handoffs directory (default: handoffs/).",
)
def handoff_list(handoffs_dir: Optional[str]) -> None:
    """List all handoff packets with ID, milestone, date, and agent.

    \b
    Example:
        agentic-sdlc handoff list
    """
    cfg = load_config()
    handoffs_dir_path = Path(handoffs_dir) if handoffs_dir else Path(
        cfg.get("templates", {}).get("handoffs_dir", "handoffs")
    )

    if not handoffs_dir_path.exists():
        warn(f"Handoffs directory not found: {handoffs_dir_path}")
        return

    rows = []
    for packet_file in sorted(handoffs_dir_path.glob("*.md")):
        meta = _parse_frontmatter(packet_file)
        if meta:
            rows.append([
                meta.get("packet_id", packet_file.stem),
                meta.get("milestone", "-"),
                meta.get("date", "-"),
                meta.get("agent", "-"),
            ])

    if not rows:
        warn("No handoff packets found.")
        return

    header("Handoff Packets")
    click.echo(tabulate(
        rows,
        headers=["Packet ID", "Milestone", "Date", "Agent"],
        tablefmt="simple",
    ))
    click.echo(f"\n{len(rows)} handoff packet(s) total.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _next_handoff_num(handoffs_dir: Path, agent_role: str) -> int:
    """Return the next available handoff sequence number."""
    existing = []
    if handoffs_dir.exists():
        # Look at all handoff files, regardless of role
        for f in handoffs_dir.glob("HANDOFF-*.md"):
            m = re.search(r"HANDOFF-(\d+)", f.name)
            if m:
                existing.append(int(m.group(1)))
    return (max(existing) + 1) if existing else 1


def _parse_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith("#"):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta
