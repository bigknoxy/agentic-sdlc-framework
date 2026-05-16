"""Load and manage .agentic-sdlc.yaml configuration.

The config file is searched upward from CWD through parent directories.
If no config file is found, sensible defaults are returned.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


CONFIG_FILENAME = ".agentic-sdlc.yaml"

DEFAULT_CONFIG_YAML = """\
project:
  name: "{project_name}"
  type: "api"

framework:
  version: "0.1.0"
  strict_mode: false

templates:
  specs_dir: "specs"
  handoffs_dir: "handoffs"
  adrs_dir: "adrs"

guardrails:
  min_coverage: 80
  security_scan: true

agents:
  planner: "claude-code"
  executor: "claude-code"
  reviewer: "claude-code"

compliance:
  data_classification: "internal"
  requires_audit: true
"""

_DEFAULT_CONFIG: dict[str, Any] = {
    "project": {
        "name": "",
        "type": "api",
    },
    "framework": {
        "version": "0.1.0",
        "strict_mode": False,
    },
    "templates": {
        "specs_dir": "specs",
        "handoffs_dir": "handoffs",
        "adrs_dir": "adrs",
    },
    "guardrails": {
        "min_coverage": 80,
        "security_scan": True,
    },
    "agents": {
        "planner": "claude-code",
        "executor": "claude-code",
        "reviewer": "claude-code",
    },
    "compliance": {
        "data_classification": "internal",
        "requires_audit": True,
    },
}


def find_config_file(start: Path | None = None) -> Path | None:
    """Walk up from start (default: CWD) to find .agentic-sdlc.yaml."""
    current = (start or Path.cwd()).resolve()
    while True:
        candidate = current / CONFIG_FILENAME
        if candidate.exists():
            return candidate
        parent = current.parent
        if parent == current:
            # Reached filesystem root without finding config
            return None
        current = parent


def load_config(start: Path | None = None) -> dict[str, Any]:
    """Load config from the nearest .agentic-sdlc.yaml, falling back to defaults."""
    config_path = find_config_file(start)
    if config_path is None:
        return _deep_copy(_DEFAULT_CONFIG)

    try:
        with config_path.open(encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh) or {}
    except (OSError, yaml.YAMLError):
        return _deep_copy(_DEFAULT_CONFIG)

    # Merge loaded config over defaults (shallow merge per top-level key)
    merged = _deep_copy(_DEFAULT_CONFIG)
    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value

    return merged


def save_config(config: dict[str, Any], path: Path) -> None:
    """Write config dict to a YAML file."""
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(config, fh, default_flow_style=False, sort_keys=False)


def _deep_copy(obj: Any) -> Any:
    """Recursively copy a dict/list structure (no external deps)."""
    if isinstance(obj, dict):
        return {k: _deep_copy(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_deep_copy(v) for v in obj]
    return obj
