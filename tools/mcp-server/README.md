# agentic-sdlc MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that exposes the agentic-sdlc-framework guardrails and spec/handoff management as tools for any MCP-compatible AI client (Claude Desktop, Claude Code, etc.).

## Tools

| Tool | Description |
|------|-------------|
| `create_spec` | Create a new agent-ready spec file; returns `spec_id` and `path` |
| `validate_spec` | Validate a spec file; returns `passed`, `errors`, `warnings` |
| `create_handoff` | Create a new handoff packet for a milestone; returns `packet_id` and `path` |
| `validate_handoff` | Validate a handoff packet; returns `passed`, `errors`, `warnings` |
| `check_guardrails` | Run all checks (secrets scan, spec validation, handoff validation); returns per-check results |

## Installation

Install the `mcp` extra from the project root:

```bash
pip install -e ".[mcp]"
```

Or install just the server's direct dependency:

```bash
pip install -r tools/mcp-server/requirements.txt
```

The server also depends on the `agentic-sdlc` package itself (installed editably from the project root).

## Running the server

```bash
python tools/mcp-server/server.py
```

The server communicates over stdio (standard MCP transport).

## Claude Desktop configuration

Add this block to your `claude_desktop_config.json` (usually `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "agentic-sdlc": {
      "command": "python",
      "args": ["/absolute/path/to/agentic-sdlc-framework/tools/mcp-server/server.py"],
      "env": {}
    }
  }
}
```

Replace `/absolute/path/to/agentic-sdlc-framework` with the actual path on your machine.

If you are using a virtual environment, point `command` at the Python interpreter inside it:

```json
{
  "mcpServers": {
    "agentic-sdlc": {
      "command": "/absolute/path/to/agentic-sdlc-framework/.venv/bin/python",
      "args": ["/absolute/path/to/agentic-sdlc-framework/tools/mcp-server/server.py"]
    }
  }
}
```

## Tool reference

### `create_spec`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `title` | string | yes | — | Human-readable title |
| `priority` | string | no | `p1` | `p0`, `p1`, or `p2` |
| `template` | string | no | `api` | `api`, `web`, `ml`, or `generic` |
| `specs_dir` | string | no | `specs/` | Directory for spec files (relative to CWD or absolute) |

Returns:
```json
{
  "spec_id": "SPEC-2025-01-15-001",
  "path": "/project/specs/SPEC-2025-01-15-001.md",
  "title": "My Feature",
  "priority": "P1",
  "template": "api"
}
```

### `validate_spec`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Path to the spec `.md` file |

Returns:
```json
{
  "passed": false,
  "errors": ["Missing required section: Edge Cases"],
  "warnings": [],
  "path": "/project/specs/SPEC-2025-01-15-001.md"
}
```

### `create_handoff`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `milestone` | string | yes | — | Milestone name or number |
| `agent` | string | no | `claude-code` | Agent ID |
| `supervisor` | string | no | `human` | Supervisor identifier |
| `handoffs_dir` | string | no | `handoffs/` | Directory for handoff files |

Returns:
```json
{
  "packet_id": "HANDOFF-executor-001",
  "path": "/project/handoffs/HANDOFF-001.md",
  "milestone": "M1",
  "agent": "claude-code",
  "supervisor": "human"
}
```

### `validate_handoff`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | yes | Path to the handoff `.md` file |

Returns:
```json
{
  "passed": true,
  "errors": [],
  "warnings": [],
  "path": "/project/handoffs/HANDOFF-001.md"
}
```

### `check_guardrails`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `root_dir` | string | no | CWD | Root directory to scan for secrets |
| `specs_dir` | string | no | `<root_dir>/specs` | Specs directory |
| `handoffs_dir` | string | no | `<root_dir>/handoffs` | Handoffs directory |

Returns:
```json
{
  "secrets": { "passed": true, "finding_count": 0, "findings": [] },
  "specs":   { "passed": true, "total": 2, "passed_count": 2, "failed_count": 0, "errors": [] },
  "handoffs":{ "passed": false, "total": 1, "passed_count": 0, "failed_count": 1, "errors": ["..."] },
  "overall_passed": false
}
```

## Path resolution

All `path`, `specs_dir`, `handoffs_dir`, and `root_dir` parameters accept either:
- **Relative paths** — resolved against the current working directory of the server process.
- **Absolute paths** — used as-is.

When running via Claude Desktop the CWD is typically your home directory, so prefer absolute paths or set `root_dir` explicitly.
