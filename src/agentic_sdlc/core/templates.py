"""Load bundled template files from package data.

Templates are stored in src/agentic_sdlc/data/templates/ and are bundled
with the package. At runtime we locate them via importlib.resources (3.9+)
with a fallback to __file__-relative path resolution for editable installs.
"""

from __future__ import annotations

import importlib.resources as pkg_resources
from pathlib import Path


_TEMPLATES_DIR = Path(__file__).parent.parent / "data" / "templates"


def _load_template(name: str) -> str:
    """Load a template by filename from the package data directory."""
    # Try importlib.resources first (works for installed wheels)
    try:
        ref = pkg_resources.files("agentic_sdlc") / "data" / "templates" / name
        return ref.read_text(encoding="utf-8")
    except (FileNotFoundError, TypeError, AttributeError):
        pass

    # Fallback: path relative to this file (works for editable installs)
    path = _TEMPLATES_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")

    raise FileNotFoundError(
        f"Template '{name}' not found in package data. "
        f"Expected location: {_TEMPLATES_DIR / name}"
    )


def get_spec_template() -> str:
    """Return the agent-ready spec template content."""
    return _load_template("agent-ready-spec.md")


def get_handoff_template() -> str:
    """Return the handoff packet template content."""
    return _load_template("handoff-packet.md")
