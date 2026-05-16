# Agentic SDLC Framework

[![CI](https://github.com/bigknoxy/agentic-sdlc-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/bigknoxy/agentic-sdlc-framework/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg?style=flat-square)](https://python.org/)
[![Tests](https://img.shields.io/badge/tests-181%20passed-brightgreen.svg?style=flat-square)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

Governance, specs, and guardrails for AI-assisted software development — built around the **FRAME** methodology.

---

## Why This Exists

AI agents write code fast. That's not the problem.

The problem is that fast code without structure becomes technical debt at agent speed. Vague requirements produce verbose first drafts that fail review. No guardrails means secrets, broken deps, and compliance gaps slip through. Context lost between sessions causes agents to hallucinate past decisions. No evaluation means you never know if things are getting better.

This framework solves the **process problem**, not the model problem. It gives your team:

- A spec format agents can actually execute (not narrative tickets)
- Guardrails that run in CI so bad output doesn't reach production
- Handoff packets that preserve context across sessions and agents
- A 12-task golden task set to measure agent performance week over week

**Technique beats tools.** The best model with a vague spec produces worse outcomes than a mid-tier model with a precise one.

---

## Who Should Use This

**Engineering teams adopting AI agents** — You're adding Claude Code, GitHub Copilot, or Cursor to your workflow and need a process that keeps output trustworthy and reviewable.

**Individual engineers** — You use Claude Code daily and want a repeatable system: write the spec, let the agent implement, run the guardrails, ship.

**Engineering managers at regulated companies** — You need audit trails, data classification, and governance artifacts before AI agents touch production code.

**Platform / DevEx teams** — You're building internal AI tooling and want a framework others can adopt without reinventing the process layer.

---

## The FRAME Methodology

| Letter | Principle | What it means |
|--------|-----------|---------------|
| **F** | Focus | One workflow, one pilot. Spread thin = no signal. |
| **R** | Requirements | Executable specs, not narrative tickets. Agents implement constraints, not intentions. |
| **A** | Automation | Guardrails in CI — secrets scanning, SAST, coverage thresholds. Keeps speed useful. |
| **M** | Multi-agent | Planner → Executor → Reviewer. Each boundary produces a handoff packet. |
| **E** | Evaluation | Weekly metrics on a fixed 12-task set. You can't improve what you don't measure. |

---

## Actual Use Cases

### 1. Shipping a Feature with an AI Agent

**Before:** Engineer pastes a Jira ticket into Claude. Agent produces code that technically works but ignores edge cases, skips error handling, and has no tests. Review takes longer than writing it would have.

**After:**
```bash
# Create a spec before asking the agent to code
agentic-sdlc spec create --title "Add rate limiting to /api/payments"
# Fill in constraints, acceptance criteria, edge cases
# Then give the spec to the agent — not the ticket
```
Agent gets exact constraints, acceptance criteria, and rollback conditions. First-pass review rate improves because the spec sets the bar before a line is written.

---

### 2. Running an AI Pilot at a Regulated Company

**Before:** Legal says no AI on production code until you can show audit trails, data classification, and access controls. Pilot stalls.

**After:** Every spec has `data_classification: confidential | internal | public`. Every milestone produces a handoff packet with a Correlation ID and audit trail entry. Security scan runs on every push.

```bash
agentic-sdlc check --all   # secrets scan + spec completeness + handoff validation
```

Pilot unblocks because the governance artifacts already exist.

---

### 3. Measuring Agent Performance Over Time

**Before:** "The agents seem to be getting better" — or worse. Nobody actually knows.

**After:**
```bash
python tools/golden-task-set/evaluate.py --week
```

12 standardized tasks, scored weekly. You see pass rate, time-to-complete, and rework rate trend over time. When a model upgrade helps — or hurts — you have data.

---

### 4. Using the Framework from Claude Desktop

Add the MCP server to `claude_desktop_config.json`:
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

Then from Claude Desktop: "Create a spec for adding OAuth to the user service" — the `create_spec` tool scaffolds the full agent-ready template. "Validate handoffs/" — `validate_handoff` runs against every packet.

---

## Quick Start

```bash
# Install from source (PyPI publish in progress — tracked: specs/SPEC-2026-05-15-001.md)
git clone https://github.com/bigknoxy/agentic-sdlc-framework.git
cd agentic-sdlc-framework
pip install -e ".[dev]"   # Python 3.11+ required

# Initialize a project
agentic-sdlc init my-project
cd my-project

# Create your first spec
agentic-sdlc spec create --title "User Authentication API"
# Edit the generated spec file — fill in constraints, acceptance criteria, edge cases

# Validate the spec
agentic-sdlc spec validate specs/SPEC-*.md

# Run all guardrails (CI-safe, exits 1 on failure)
agentic-sdlc check --all
```

---

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
| `agentic-sdlc check --secrets` | Scan for exposed secrets |
| `agentic-sdlc check --specs` | Validate spec completeness |
| `agentic-sdlc check --handoffs` | Validate handoff packet completeness |
| `agentic-sdlc metrics --week` | Show weekly evaluation metrics |

---

## MCP Server

`tools/mcp-server/server.py` exposes five tools for Claude Desktop or any MCP-compatible client:

| Tool | Description |
|------|-------------|
| `create_spec` | Scaffold a new agent-ready spec |
| `validate_spec` | Validate a spec document |
| `create_handoff` | Create a handoff packet |
| `validate_handoff` | Validate a handoff packet |
| `check_guardrails` | Run all guardrail checks |

---

## Key Results (Framework Applied to Itself)

| Metric | Value |
|--------|-------|
| Tests | 181 passed, 0 failed |
| Coverage | 86.79% |
| CLI commands | 11 |
| MCP tools | 5 |
| Golden task set | 12 tasks |
| Guardrail scripts | 4 |
| Active specs | 3 |
| `check --all` | Clean |

---

## Repository Structure

```
.
├── src/agentic_sdlc/        # Python CLI source (11 commands)
├── tests/                   # 181 tests, 86.79% coverage
├── tools/
│   ├── guardrail-scripts/   # validate-spec.py, check-handoff-packet.py, generate-audit-trail.py, validate-intake.py
│   ├── mcp-server/          # MCP server (5 tools)
│   └── golden-task-set/     # 12 evaluation tasks + evaluate.py
├── templates/               # agent-ready-spec.md, handoff-packet.md, ADR, scorecard, pilot-proposal
├── docs/                    # framework-overview.md, how-to-use.md, implementation-guide.md, security-guardrails.md
├── specs/                   # Active specs (SPEC-2026-05-15-001 through 003)
├── handoffs/                # Handoff packets (HANDOFF-001.md)
├── examples/
│   ├── personal-project-example/
│   └── enterprise-pilot-example/
└── pyproject.toml
```

---

## Contributing

Branch from `main`, write an agent-ready spec for significant changes, pass all CI checks, then submit a PR. See [CONTRIBUTING.md](CONTRIBUTING.md).

The project is developed using the framework itself — new features start as specs in `specs/`.

## License

MIT — see [LICENSE](LICENSE).
