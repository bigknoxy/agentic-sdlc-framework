"""agentic-sdlc metrics — Report project metrics from specs and handoffs."""

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

import click
from tabulate import tabulate

from agentic_sdlc.core.config import load_config
from agentic_sdlc.core.validation import validate_spec, validate_handoff
from agentic_sdlc.utils.output import success, info, error, warn, header


@click.command("metrics")
@click.option("--week", is_flag=True, default=False, help="Scope to files created this week.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--specs-dir",
    default=None,
    help="Override the specs directory (default: specs/).",
)
@click.option(
    "--handoffs-dir",
    default=None,
    help="Override the handoffs directory (default: handoffs/).",
)
def metrics(
    week: bool,
    output_format: str,
    specs_dir: Optional[str],
    handoffs_dir: Optional[str],
) -> None:
    """Report project metrics: spec counts, handoff counts, validation pass rate.

    \b
    Examples:
        agentic-sdlc metrics
        agentic-sdlc metrics --week
        agentic-sdlc metrics --format json
        agentic-sdlc metrics --week --format json
    """
    cfg = load_config()
    specs_path = Path(specs_dir) if specs_dir else Path(
        cfg.get("templates", {}).get("specs_dir", "specs")
    )
    handoffs_path = Path(handoffs_dir) if handoffs_dir else Path(
        cfg.get("templates", {}).get("handoffs_dir", "handoffs")
    )

    week_start = date.today() - timedelta(days=date.today().weekday()) if week else None

    # Collect spec data
    spec_files = _collect_files(specs_path, week_start)
    handoff_files = _collect_files(handoffs_path, week_start)

    # Aggregate spec stats
    spec_by_status: dict = {}
    spec_pass = 0
    spec_fail = 0
    for sf in spec_files:
        meta = _parse_frontmatter(sf)
        status = meta.get("status", "unknown")
        spec_by_status[status] = spec_by_status.get(status, 0) + 1
        valid, _ = validate_spec(sf)
        if valid:
            spec_pass += 1
        else:
            spec_fail += 1

    total_specs = len(spec_files)
    spec_pass_rate = (spec_pass / total_specs * 100) if total_specs > 0 else 0.0

    # Aggregate handoff stats
    handoff_total = len(handoff_files)
    handoff_pass = 0
    for hf in handoff_files:
        valid, _ = validate_handoff(hf)
        if valid:
            handoff_pass += 1

    handoff_pass_rate = (handoff_pass / handoff_total * 100) if handoff_total > 0 else 0.0

    scope_label = "This Week" if week else "All Time"

    if output_format == "json":
        data = {
            "scope": scope_label,
            "specs": {
                "total": total_specs,
                "by_status": spec_by_status,
                "validation_pass": spec_pass,
                "validation_fail": spec_fail,
                "validation_pass_rate_pct": round(spec_pass_rate, 1),
            },
            "handoffs": {
                "total": handoff_total,
                "validation_pass": handoff_pass,
                "validation_fail": handoff_total - handoff_pass,
                "validation_pass_rate_pct": round(handoff_pass_rate, 1),
            },
        }
        click.echo(json.dumps(data, indent=2))
        return

    # Table format
    header(f"Agentic SDLC Metrics ({scope_label})")

    # Specs summary
    click.echo(click.style("\nSpecs", bold=True))
    spec_rows = [[status, count] for status, count in sorted(spec_by_status.items())]
    spec_rows.append(["TOTAL", total_specs])
    click.echo(tabulate(spec_rows, headers=["Status", "Count"], tablefmt="simple"))

    # Spec validation rate
    click.echo("")
    pass_color = "green" if spec_pass_rate >= 80 else "yellow" if spec_pass_rate >= 50 else "red"
    rate_str = click.style(f"{spec_pass_rate:.1f}%", fg=pass_color, bold=True)
    info(f"Spec validation pass rate: {rate_str} ({spec_pass}/{total_specs})")

    # Handoffs summary
    click.echo(click.style("\nHandoffs", bold=True))
    handoff_rows = [
        ["Total", handoff_total],
        ["Passed validation", handoff_pass],
        ["Failed validation", handoff_total - handoff_pass],
    ]
    click.echo(tabulate(handoff_rows, headers=["Metric", "Count"], tablefmt="simple"))

    if handoff_total > 0:
        click.echo("")
        hpass_color = "green" if handoff_pass_rate >= 80 else "yellow" if handoff_pass_rate >= 50 else "red"
        hrate_str = click.style(f"{handoff_pass_rate:.1f}%", fg=hpass_color, bold=True)
        info(f"Handoff validation pass rate: {hrate_str} ({handoff_pass}/{handoff_total})")

    click.echo("")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collect_files(directory: Path, week_start: Optional[date]) -> list:
    """Collect markdown files from directory, optionally filtered to this week."""
    if not directory.exists():
        return []

    files = []
    for fpath in sorted(directory.glob("*.md")):
        if fpath.name == ".gitkeep":
            continue
        if week_start:
            # Filter by date embedded in filename (YYYY-MM-DD) or file modification time
            mdate = date.fromtimestamp(fpath.stat().st_mtime)
            # Also try extracting date from filename
            m = re.search(r"(\d{4})-(\d{2})-(\d{2})", fpath.name)
            if m:
                try:
                    fdate = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                    mdate = fdate
                except ValueError:
                    pass
            if mdate < week_start:
                continue
        files.append(fpath)
    return files


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
