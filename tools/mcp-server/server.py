"""MCP server for the agentic-sdlc-framework.

Exposes five tools over the Model Context Protocol:
  - create_spec       Create a new agent-ready spec file
  - validate_spec     Validate a spec file, return structured results
  - create_handoff    Create a new handoff packet
  - validate_handoff  Validate a handoff packet, return structured results
  - check_guardrails  Run all guardrail checks and return per-check results
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Ensure the project src is importable when running the server directly
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).parent.parent.parent
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from agentic_sdlc.core.templates import get_spec_template, get_handoff_template
from agentic_sdlc.core.validation import (
    validate_spec as _validate_spec,
    validate_handoff as _validate_handoff,
    validate_spec_directory,
    validate_handoff_directory,
)
from agentic_sdlc.commands.check import _scan_secrets

# ---------------------------------------------------------------------------
# MCP server instance
# ---------------------------------------------------------------------------

server = Server("agentic-sdlc")

# ---------------------------------------------------------------------------
# Internal helpers (re-implementing thin create logic without Click/sys.exit)
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


def _next_handoff_num(handoffs_dir: Path) -> int:
    """Return the next available handoff sequence number."""
    existing = []
    if handoffs_dir.exists():
        for f in handoffs_dir.glob("HANDOFF-*.md"):
            m = re.search(r"HANDOFF-(\d+)", f.name)
            if m:
                existing.append(int(m.group(1)))
    return (max(existing) + 1) if existing else 1


def _resolve(path_str: str) -> Path:
    """Resolve a potentially relative path against CWD."""
    p = Path(path_str)
    if not p.is_absolute():
        p = Path.cwd() / p
    return p


def _ok(data: dict[str, Any]) -> list[TextContent]:
    """Return a successful MCP TextContent result."""
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def _err(message: str) -> list[TextContent]:
    """Return an error MCP TextContent result."""
    return [TextContent(type="text", text=json.dumps({"error": message}, indent=2))]


# ---------------------------------------------------------------------------
# Tool: list_tools
# ---------------------------------------------------------------------------

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="create_spec",
            description=(
                "Create a new agent-ready spec file in the specs directory. "
                "Returns the generated spec_id and the path to the file."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Human-readable title for the spec.",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["p0", "p1", "p2"],
                        "default": "p1",
                        "description": "Priority level: p0 (critical), p1 (high), p2 (normal).",
                    },
                    "template": {
                        "type": "string",
                        "enum": ["api", "web", "ml", "generic"],
                        "default": "api",
                        "description": "Spec template type.",
                    },
                    "specs_dir": {
                        "type": "string",
                        "description": "Directory for spec files (default: specs/).",
                    },
                },
                "required": ["title"],
            },
        ),
        Tool(
            name="validate_spec",
            description=(
                "Validate an existing spec file against the FRAME guardrails. "
                "Returns structured results: passed (bool), errors (list), warnings (list)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the spec .md file (relative to CWD or absolute).",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="create_handoff",
            description=(
                "Create a new handoff packet for a milestone. "
                "Returns the packet_id and the path to the file."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "milestone": {
                        "type": "string",
                        "description": "Milestone name or number (e.g. 'M1' or 'Milestone 2').",
                    },
                    "agent": {
                        "type": "string",
                        "description": "Agent ID that produced this handoff (default: claude-code).",
                    },
                    "supervisor": {
                        "type": "string",
                        "description": "Human supervisor overseeing this handoff (default: human).",
                    },
                    "handoffs_dir": {
                        "type": "string",
                        "description": "Directory for handoff files (default: handoffs/).",
                    },
                },
                "required": ["milestone"],
            },
        ),
        Tool(
            name="validate_handoff",
            description=(
                "Validate an existing handoff packet against all FRAME guardrails. "
                "Returns structured results: passed (bool), errors (list), warnings (list)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the handoff .md file (relative to CWD or absolute).",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="check_guardrails",
            description=(
                "Run all guardrail checks (secrets scan, spec validation, handoff validation). "
                "Returns a per-check results dict."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "root_dir": {
                        "type": "string",
                        "description": "Root directory to scan (default: CWD).",
                    },
                    "specs_dir": {
                        "type": "string",
                        "description": "Specs directory override (default: specs/ under root_dir).",
                    },
                    "handoffs_dir": {
                        "type": "string",
                        "description": "Handoffs directory override (default: handoffs/ under root_dir).",
                    },
                },
                "required": [],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tool: call_tool
# ---------------------------------------------------------------------------

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "create_spec":
        return await _tool_create_spec(arguments)
    if name == "validate_spec":
        return await _tool_validate_spec(arguments)
    if name == "create_handoff":
        return await _tool_create_handoff(arguments)
    if name == "validate_handoff":
        return await _tool_validate_handoff(arguments)
    if name == "check_guardrails":
        return await _tool_check_guardrails(arguments)
    return _err(f"Unknown tool: {name}")


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

async def _tool_create_spec(args: dict[str, Any]) -> list[TextContent]:
    title = args.get("title", "").strip()
    if not title:
        return _err("Missing required parameter: title")

    priority = args.get("priority", "p1").lower()
    if priority not in ("p0", "p1", "p2"):
        return _err(f"Invalid priority '{priority}'. Must be one of: p0, p1, p2")

    template = args.get("template", "api").lower()
    if template not in ("api", "web", "ml", "generic"):
        return _err(f"Invalid template '{template}'. Must be one of: api, web, ml, generic")

    specs_dir_str = args.get("specs_dir", "specs")
    specs_path = _resolve(specs_dir_str)

    today = date.today().strftime("%Y-%m-%d")
    spec_id = _next_spec_id(specs_path, today)
    filename = f"{spec_id}.md"
    output_path = specs_path / filename

    try:
        specs_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return _err(f"Cannot create specs directory '{specs_path}': {exc}")

    try:
        content = get_spec_template()
    except FileNotFoundError as exc:
        return _err(f"Spec template not found: {exc}")

    content = content.replace("SPEC-YYYY-MM-DD-001", spec_id)
    content = content.replace("[Feature/Workflow Name]", title)
    content = content.replace("priority: p1", f"priority: {priority}")
    content = content.replace(
        "template_version: 1.0.0",
        f"template_version: 1.0.0\nspec_template: {template}",
    )

    try:
        output_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        return _err(f"Failed to write spec file: {exc}")

    return _ok({
        "spec_id": spec_id,
        "path": str(output_path),
        "title": title,
        "priority": priority.upper(),
        "template": template,
    })


async def _tool_validate_spec(args: dict[str, Any]) -> list[TextContent]:
    path_str = args.get("path", "").strip()
    if not path_str:
        return _err("Missing required parameter: path")

    spec_path = _resolve(path_str)
    if not spec_path.exists():
        return _err(f"File not found: {spec_path}")

    passed, errors = _validate_spec(spec_path)

    return _ok({
        "passed": passed,
        "errors": errors,
        "warnings": [],
        "path": str(spec_path),
    })


async def _tool_create_handoff(args: dict[str, Any]) -> list[TextContent]:
    milestone = args.get("milestone", "").strip()
    if not milestone:
        return _err("Missing required parameter: milestone")

    agent = args.get("agent", "claude-code").strip() or "claude-code"
    supervisor = args.get("supervisor", "human").strip() or "human"

    handoffs_dir_str = args.get("handoffs_dir", "handoffs")
    handoffs_path = _resolve(handoffs_dir_str)

    # Determine agent role for packet_id
    agent_role = "planner" if "planner" in agent.lower() else "executor"

    packet_num = _next_handoff_num(handoffs_path)
    packet_id = f"HANDOFF-{agent_role}-{packet_num:03d}"
    filename = f"HANDOFF-{packet_num:03d}.md"
    output_path = handoffs_path / filename

    today = date.today().strftime("%Y-%m-%d")

    try:
        handoffs_path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return _err(f"Cannot create handoffs directory '{handoffs_path}': {exc}")

    try:
        content = get_handoff_template()
    except FileNotFoundError as exc:
        return _err(f"Handoff template not found: {exc}")

    content = content.replace("HANDOFF-[planner|executor]-###", packet_id)
    content = content.replace("[Number/Name]", milestone)
    content = content.replace("YYYY-MM-DD", today, 1)
    content = content.replace('[Agent ID - e.g., "claude-code-001"]', agent)
    content = content.replace('[Human owner - e.g., "josh@apexfinancial.example.com"]', supervisor)
    content = content.replace("[Milestone Name]", milestone)

    try:
        output_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        return _err(f"Failed to write handoff packet: {exc}")

    return _ok({
        "packet_id": packet_id,
        "path": str(output_path),
        "milestone": milestone,
        "agent": agent,
        "supervisor": supervisor,
    })


async def _tool_validate_handoff(args: dict[str, Any]) -> list[TextContent]:
    path_str = args.get("path", "").strip()
    if not path_str:
        return _err("Missing required parameter: path")

    packet_path = _resolve(path_str)
    if not packet_path.exists():
        return _err(f"File not found: {packet_path}")

    passed, errors = _validate_handoff(packet_path)

    return _ok({
        "passed": passed,
        "errors": errors,
        "warnings": [],
        "path": str(packet_path),
    })


async def _tool_check_guardrails(args: dict[str, Any]) -> list[TextContent]:
    root_str = args.get("root_dir", "")
    root = _resolve(root_str) if root_str else Path.cwd()

    specs_dir_str = args.get("specs_dir", "")
    specs_path = _resolve(specs_dir_str) if specs_dir_str else root / "specs"

    handoffs_dir_str = args.get("handoffs_dir", "")
    handoffs_path = _resolve(handoffs_dir_str) if handoffs_dir_str else root / "handoffs"

    results: dict[str, Any] = {}
    overall_passed = True

    # --- Secrets scan ---
    findings = _scan_secrets(root)
    secrets_passed = len(findings) == 0
    overall_passed = overall_passed and secrets_passed
    results["secrets"] = {
        "passed": secrets_passed,
        "finding_count": len(findings),
        "findings": [
            {
                "path": str(fpath),
                "line": lineno,
                "label": label,
                "snippet": snippet[:120],
            }
            for fpath, lineno, label, snippet in findings
        ],
    }

    # --- Spec validation ---
    if specs_path.exists():
        total, passed_count, errors = validate_spec_directory(specs_path)
        specs_passed = (total == 0 or passed_count == total)
        overall_passed = overall_passed and specs_passed
        results["specs"] = {
            "passed": specs_passed,
            "total": total,
            "passed_count": passed_count,
            "failed_count": total - passed_count,
            "errors": errors,
        }
    else:
        results["specs"] = {
            "passed": True,
            "total": 0,
            "passed_count": 0,
            "failed_count": 0,
            "errors": [],
            "skipped": f"Directory not found: {specs_path}",
        }

    # --- Handoff validation ---
    if handoffs_path.exists():
        total, passed_count, errors = validate_handoff_directory(handoffs_path)
        handoffs_passed = (total == 0 or passed_count == total)
        overall_passed = overall_passed and handoffs_passed
        results["handoffs"] = {
            "passed": handoffs_passed,
            "total": total,
            "passed_count": passed_count,
            "failed_count": total - passed_count,
            "errors": errors,
        }
    else:
        results["handoffs"] = {
            "passed": True,
            "total": 0,
            "passed_count": 0,
            "failed_count": 0,
            "errors": [],
            "skipped": f"Directory not found: {handoffs_path}",
        }

    results["overall_passed"] = overall_passed
    return _ok(results)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
