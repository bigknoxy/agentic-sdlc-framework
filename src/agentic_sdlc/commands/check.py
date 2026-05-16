"""agentic-sdlc check — Run guardrail checks (CI-friendly, exits 1 on failure)."""

import re
import sys
from pathlib import Path
from typing import List, Tuple

import click

from agentic_sdlc.core.config import load_config
from agentic_sdlc.core.validation import validate_spec_directory, validate_handoff_directory
from agentic_sdlc.utils.output import success, info, error, warn, header, step


# Common secret patterns to scan for
SECRET_PATTERNS = [
    (r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?[A-Za-z0-9+/]{20,}['\"]?", "API key"),
    (r"(?i)(secret[_-]?key|secret)\s*[=:]\s*['\"]?[A-Za-z0-9+/]{20,}['\"]?", "Secret key"),
    (r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?.{8,}['\"]?", "Password"),
    (r"(?i)(token|auth[_-]?token|access[_-]?token)\s*[=:]\s*['\"]?[A-Za-z0-9+/._-]{20,}['\"]?", "Auth token"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*['\"]?[A-Za-z0-9+/]{40}['\"]?", "AWS Secret Key"),
    (r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----", "Private key"),
    (r"(?i)(database[_-]?url|db[_-]?url)\s*[=:]\s*['\"]?[A-Za-z]+://[^\s'\"]{10,}['\"]?", "Database URL"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub Personal Access Token"),
    (r"xoxb-[0-9]+-[A-Za-z0-9]+", "Slack Bot Token"),
]

# File extensions to scan for secrets
SCAN_EXTENSIONS = {".py", ".js", ".ts", ".yaml", ".yml", ".json", ".env", ".sh", ".bash", ".toml", ".cfg", ".ini"}

# Directories/files to always skip
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".mypy_cache", ".pytest_cache", "tests"}


@click.command("check")
@click.option("--all", "run_all", is_flag=True, default=False, help="Run all available checks.")
@click.option("--secrets", is_flag=True, default=False, help="Scan for hardcoded secrets.")
@click.option("--specs", is_flag=True, default=False, help="Validate all specs in specs/.")
@click.option("--handoffs", is_flag=True, default=False, help="Validate all handoffs in handoffs/.")
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
def check(
    run_all: bool,
    secrets: bool,
    specs: bool,
    handoffs: bool,
    specs_dir: str,
    handoffs_dir: str,
) -> None:
    """Run guardrail checks against the project.

    Returns exit code 1 if any check fails (CI-friendly).

    \b
    Examples:
        agentic-sdlc check --all
        agentic-sdlc check --secrets
        agentic-sdlc check --specs --handoffs
    """
    if not any([run_all, secrets, specs, handoffs]):
        click.echo(click.get_current_context().get_help())
        sys.exit(0)

    cfg = load_config()
    overall_pass = True
    cwd = Path.cwd()

    # --all enables everything
    run_secrets = run_all or secrets
    run_specs = run_all or specs
    run_handoffs = run_all or handoffs

    # Secrets check
    if run_secrets:
        header("Secrets Scan")
        findings = _scan_secrets(cwd)
        if findings:
            overall_pass = False
            error(f"Found {len(findings)} potential secret(s):")
            for fpath, lineno, label, snippet in findings:
                click.echo(
                    f"  {click.style('x', fg='red')} [{label}] {fpath}:{lineno}  {snippet[:80]}"
                )
        else:
            success("No secrets detected.")
        click.echo("")

    # Specs validation
    if run_specs:
        header("Spec Validation")
        specs_path = Path(specs_dir) if specs_dir else Path(
            cfg.get("templates", {}).get("specs_dir", "specs")
        )
        if not specs_path.exists():
            warn(f"Specs directory not found: {specs_path} — skipping.")
        else:
            total, passed, all_errors = validate_spec_directory(specs_path)
            if total == 0:
                warn("No spec files found.")
            elif passed == total:
                success(f"All {total} spec(s) passed.")
            else:
                overall_pass = False
                failed = total - passed
                error(f"{failed}/{total} spec(s) failed:")
                for msg in all_errors:
                    click.echo(f"  {click.style('x', fg='red')} {msg}")
        click.echo("")

    # Handoffs validation
    if run_handoffs:
        header("Handoff Validation")
        handoffs_path = Path(handoffs_dir) if handoffs_dir else Path(
            cfg.get("templates", {}).get("handoffs_dir", "handoffs")
        )
        if not handoffs_path.exists():
            warn(f"Handoffs directory not found: {handoffs_path} — skipping.")
        else:
            total, passed, all_errors = validate_handoff_directory(handoffs_path)
            if total == 0:
                warn("No handoff packets found.")
            elif passed == total:
                success(f"All {total} handoff packet(s) passed.")
            else:
                overall_pass = False
                failed = total - passed
                error(f"{failed}/{total} handoff packet(s) failed:")
                for msg in all_errors:
                    click.echo(f"  {click.style('x', fg='red')} {msg}")
        click.echo("")

    # Summary
    if overall_pass:
        success("All checks passed.")
    else:
        error("One or more checks failed.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Secret scanning helpers
# ---------------------------------------------------------------------------

def _scan_secrets(root: Path) -> List[Tuple[Path, int, str, str]]:
    """Scan files under root for secret patterns.

    Returns list of (path, line_number, label, snippet) tuples.
    """
    findings: List[Tuple[Path, int, str, str]] = []
    compiled = [(re.compile(pat), label) for pat, label in SECRET_PATTERNS]

    for fpath in _iter_files(root):
        try:
            lines = fpath.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        for lineno, line in enumerate(lines, start=1):
            for pattern, label in compiled:
                if pattern.search(line):
                    # Skip commented-out lines
                    stripped = line.lstrip()
                    if stripped.startswith("#") or stripped.startswith("//"):
                        continue
                    # Skip lines that look like examples/tests
                    if any(tok in line.lower() for tok in ["example", "placeholder", "your_", "<", "xxx"]):
                        continue
                    findings.append((fpath.relative_to(root), lineno, label, line.strip()))
                    break  # one hit per line is enough

    return findings


def _iter_files(root: Path):
    """Yield non-skipped files with scannable extensions."""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        # Skip hidden dirs and known noise dirs
        if any(part in SKIP_DIRS or part.startswith(".") for part in path.parts[len(root.parts):]):
            continue
        if path.suffix.lower() in SCAN_EXTENSIONS or path.name in {".env", ".envrc"}:
            yield path
