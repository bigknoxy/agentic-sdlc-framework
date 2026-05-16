# Agentic SDLC Framework

[![CI](https://github.com/bigknoxy/agentic-sdlc-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/bigknoxy/agentic-sdlc-framework/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg?style=flat-square)](https://python.org/)
[![Tests](https://img.shields.io/badge/tests-181%20passed-brightgreen.svg?style=flat-square)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

A framework for integrating AI agents into the software development lifecycle with built-in governance, security, auditing, and evaluation — built around the **FRAME** methodology.

## The FRAME-Enhanced SDLC

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 0: Intake & Triage                                       │
│  Phase 1: Executable Spec Generation                            │
│  Phase 2: Design & Architecture                                 │
│  Phase 3: Implementation (Multi-Agent)                          │
│  Phase 4: Validation & Security Pass                            │
│  Phase 5: Deployment & Release                                  │
│  Phase 6: Operations & Monitoring                               │
└─────────────────────────────────────────────────────────────────┘
```

**FRAME:** Focus → Requirements → Automation guardrails → Multi-agent coordination → Evaluation cadence.

## Key Principles

1. **Technique > Tools** — Process discipline drives outcomes more than model choice
2. **Executable Specs** — Requirements that agents can directly implement
3. **Automated Guardrails** — Security and compliance built into the pipeline
4. **Multi-Agent Coordination** — Planner → Executor → Reviewer with handoff packets
5. **Continuous Evaluation** — Weekly metrics on a 12-task golden task set

## Quick Start

```bash
git clone https://github.com/bigknoxy/agentic-sdlc-framework.git
cd agentic-sdlc-framework
pip install -e ".[dev]"

# Initialize a project
agentic-sdlc init my-project
cd my-project

# Create a spec
agentic-sdlc spec create --title "User Authentication API"

# Validate
agentic-sdlc spec validate specs/SPEC-2026-05-15-001.md

# Run all guardrails
agentic-sdlc check --all
```

> Python 3.11+ required. The package is not yet on PyPI — install from source.

## CLI Reference

| Command | Description |
|---------|-------------|
| `agentic-sdlc init <name>` | Initialize a new project directory |
| `agentic-sdlc spec create --title "..."` | Create a new agent-ready spec |
| `agentic-sdlc spec validate <path>` | Validate a spec document |
| `agentic-sdlc spec list` | List all specs in the project |
| `agentic-sdlc handoff create --milestone N --agent claude-code` | Create a handoff packet |
| `agentic-sdlc handoff validate <path>` | Validate a handoff packet |
| `agentic-sdlc handoff list` | List all handoff packets |
| `agentic-sdlc check --all` | Run all guardrail checks (exits 1 on failure) |
| `agentic-sdlc check --secrets` | Check for exposed secrets |
| `agentic-sdlc check --specs` | Check spec completeness |
| `agentic-sdlc check --handoffs` | Check handoff packet completeness |
| `agentic-sdlc metrics --week` | Show weekly evaluation metrics |

## MCP Server

`tools/mcp-server/server.py` exposes five tools for use with Claude Desktop or any MCP-compatible client:

| Tool | Description |
|------|-------------|
| `create_spec` | Create a new agent-ready spec |
| `validate_spec` | Validate a spec document |
| `create_handoff` | Create a handoff packet |
| `validate_handoff` | Validate a handoff packet |
| `check_guardrails` | Run all guardrail checks |

To configure for Claude Desktop, add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agentic-sdlc": {
      "command": "python",
      "args": ["/path/to/agentic-sdlc-framework/tools/mcp-server/server.py"]
    }
  }
}
```

## Golden Task Set

`tools/golden-task-set/evaluate.py` provides 12 standardized evaluation tasks for measuring agent performance over time.

```bash
python tools/golden-task-set/evaluate.py --list
python tools/golden-task-set/evaluate.py --task GT-001
python tools/golden-task-set/evaluate.py --record GT-001 --result pass
python tools/golden-task-set/evaluate.py --week
```

## Repository Structure

```
.
├── src/agentic_sdlc/        # Python CLI source
├── tests/                   # 181 tests, 86.79% coverage
├── tools/
│   ├── guardrail-scripts/   # validate-spec.py, check-handoff-packet.py, generate-audit-trail.py, validate-intake.py
│   ├── mcp-server/          # MCP server (5 tools)
│   └── golden-task-set/     # 12 evaluation tasks + evaluate.py
├── templates/               # agent-ready-spec.md, handoff-packet.md, ADR, scorecard, pilot-proposal
├── docs/                    # framework-overview.md, how-to-use.md, implementation-guide.md, security-guardrails.md
├── examples/
│   ├── personal-project-example/
│   ├── enterprise-pilot-example/
│   └── regulated-financial-pilot/
└── pyproject.toml
```

## Contributing

Branch from `main`, write an agent-ready spec for significant changes, pass all CI checks, then submit a PR. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
