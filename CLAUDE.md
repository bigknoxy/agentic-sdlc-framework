# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A documentation-and-tooling framework (not a runnable application) for integrating AI agents into software development pipelines using the **FRAME** methodology. Primary artifacts are Markdown templates, Python guardrail scripts, and GitHub Actions workflows. There is no build step or compiled output.

## Commands

### CLI

```bash
# Install (dev mode)
pip install -e ".[dev]"

# Init project
agentic-sdlc init <project-name>

# Spec commands
agentic-sdlc spec create --title "Feature Name"
agentic-sdlc spec validate specs/SPEC-2026-01-15-001.md
agentic-sdlc spec list

# Handoff commands
agentic-sdlc handoff create --milestone 1 --agent claude-code
agentic-sdlc handoff validate handoffs/HANDOFF-001.md

# Guardrail check (CI-friendly, exits 1 on failure)
agentic-sdlc check --all

# Golden task evaluation
python tools/golden-task-set/evaluate.py --list
python tools/golden-task-set/evaluate.py --task GT-001
python tools/golden-task-set/evaluate.py --week
```

### Guardrail Scripts (Python 3.11+)

```bash
# Validate a spec document
python tools/guardrail-scripts/validate-spec.py path/to/spec.md

# Validate all specs in a directory
python tools/guardrail-scripts/validate-spec.py --dir ./specs

# Strict mode (warnings = errors)
python tools/guardrail-scripts/validate-spec.py --strict path/to/spec.md

# Validate a handoff packet
python tools/guardrail-scripts/check-handoff-packet.py path/to/handoff.md

# Validate all handoff packets in a directory (strict mode)
python tools/guardrail-scripts/check-handoff-packet.py --strict --dir ./handoffs

# Generate an audit trail entry
python tools/guardrail-scripts/generate-audit-trail.py \
    --action "spec.created" \
    --actor "claude-code" \
    --resource "SPEC-2025-01-15-001" \
    --result "success"

# Output formats: json (default), log, markdown
python tools/guardrail-scripts/generate-audit-trail.py \
    --action "spec.reviewed" --actor "human" --result "success" \
    --output markdown --output-file audit.md
```

### Lint Markdown

```bash
npm install -g markdownlint-cli
markdownlint '**/*.md' --ignore node_modules --ignore CHANGELOG.md
```

### Run Python script syntax check

```bash
python3 -m py_compile tools/guardrail-scripts/<script>.py
```

## Architecture

### Directory Map

| Path | Purpose |
|------|---------|
| `templates/` | Fill-in-the-blank source artifacts agents and humans complete |
| `docs/` | Framework methodology and usage guidance |
| `tools/guardrail-scripts/` | Python validators that enforce spec/packet completeness |
| `tools/mcp-server/` | MCP server exposing 5 framework tools for Claude Desktop / MCP clients |
| `tools/golden-task-set/` | 12 standardized evaluation tasks + evaluate.py for weekly metrics |
| `examples/` | Worked examples (personal and enterprise) showing completed artifacts |
| `.github/workflows/` | CI: markdown lint, spec validation, secret scanning, structure checks |

### Template Hierarchy

**agent-ready-spec.md** is the core artifact. All other templates reference or extend it:

1. `pilot-proposal.md` → approved → `agent-ready-spec.md`
2. `agent-ready-spec.md` → implemented → `handoff-packet.md` (one per milestone)
3. Significant decisions → `architecture-decision-record.md`
4. Outcomes tracked in → `weekly-scorecard.md`

### Guardrail Script Contract

Each script in `tools/guardrail-scripts/` follows the same pattern:
- Accepts a file path or `--dir` for batch
- Returns exit code 0 (pass), 1 (fail), 2 (usage error)
- `--strict` promotes warnings to errors
- Scripts validate YAML frontmatter + required Markdown section presence

### CI Pipeline Jobs

| Job | What it enforces |
|-----|-----------------|
| `lint` | markdownlint + lychee link check (both non-blocking) |
| `validate-specs` | Required sections in `templates/agent-ready-spec.md` |
| `security` | TruffleHog secret scan on diffs; sensitive file check |
| `structure` | `docs/`, `templates/`, `examples/`, `tools/` dirs + `README.md`, `LICENSE`, `CONTRIBUTING.md` exist |
| `test` | `py_compile` on every `.py` in `tools/guardrail-scripts/` |

## Key Concepts

**FRAME:** Focus → Requirements → Automation guardrails → Multi-agent coordination → Evaluation cadence.

**Multi-agent pattern:** Planner breaks work into milestones → Executor implements one milestone → Reviewer validates → each boundary produces a `handoff-packet.md`.

**Data classification** used in specs: `restricted` / `confidential` / `internal` / `public` — determines allowed endpoints and audit requirements.

**Spec frontmatter** must include: `spec_id`, `title`, `status`, `priority`. **Handoff packet frontmatter** must include: `packet_id`, `milestone`, `date`, `agent`, `supervisor`.

**Spec ID format:** `SPEC-YYYY-MM-DD-NNN` (e.g. `SPEC-2025-01-15-001`). Increment NNN per day.

## Contributing

Branch from `main`, write an agent-ready spec for significant changes, pass all CI checks, then submit a PR. The project is developed using the framework itself — new templates or scripts should have a corresponding spec.
