# Framework Delivery Strategy: CLI vs MCP vs IDE Integration

## Executive Summary

The Agentic SDLC Framework can be delivered through multiple interfaces. This document analyzes the options and recommends a phased approach starting with CLI, then expanding to IDE and MCP.

## Current Status

| Phase | Deliverable | Status |
|-------|------------|--------|
| Phase 1 — CLI | `agentic-sdlc` CLI (init, spec, handoff, check, metrics) | Complete |
| Phase 2 — MCP | MCP server (`tools/mcp-server/server.py`) | Complete |
| Phase 3 — IDE | VS Code / JetBrains extension | Planned |
| Phase 4 — Web | Web dashboard | Planned |

## Option Analysis

### Option 1: CLI Tool (Recommended Start)

**Concept:** `agentic-sdlc` command-line tool

**Example Usage:**
```bash
# Initialize new project
agentic-sdlc init my-project

# Create new spec
agentic-sdlc spec create --template api --title "User Service"

# Validate spec
agentic-sdlc spec validate

# Note: implemented commands are init, spec, handoff, check, metrics
# agentic-sdlc implement --milestone 1  # aspirational — not yet implemented

# Generate handoff packet
agentic-sdlc handoff create

# Validate handoff
agentic-sdlc handoff validate

# Run all guardrails
agentic-sdlc check --all

# Generate weekly scorecard
agentic-sdlc metrics --week

# Note: implemented commands are init, spec, handoff, check, metrics
# agentic-sdlc deploy --strategy canary  # aspirational — not yet implemented
```

**Pros:**
- ✅ Universal (works in any environment)
- ✅ Scriptable and automatable
- ✅ Easy CI/CD integration
- ✅ Low barrier to entry
- ✅ Fast to implement
- ✅ Works with any editor/IDE

**Cons:**
- ❌ Less discoverable than GUI
- ❌ Steeper learning curve for non-technical users
- ❌ No visual progress indication

**Best For:**
- Engineers comfortable with CLI
- CI/CD pipelines
- Automation scripts
- Initial framework adoption

---

### Option 2: MCP Server (Model Context Protocol)

**Concept:** MCP server that agents can call

**Example Usage:**
```json
// Agent calls MCP tools
{
  "tools": [
    {
      "name": "create_spec",
      "description": "Create agent-ready spec from template",
      "parameters": {
        "title": "User Service",
        "template": "api",
        "priority": "p1"
      }
    },
    {
      "name": "validate_spec",
      "description": "Validate spec completeness",
      "parameters": {
        "spec_path": "./specs/USER-001.md"
      }
    },
    {
      "name": "create_handoff",
      "description": "Create handoff packet",
      "parameters": {
        "milestone": 1,
        "agent": "claude-code"
      }
    },
    {
      "name": "check_guardrails",
      "description": "Run all guardrail checks",
      "parameters": {
        "strict": true
      }
    }
  ]
}
```

**Pros:**
- ✅ Native AI agent integration
- ✅ Agents can self-manage framework
- ✅ No human intervention for routine tasks
- ✅ Standardized interface
- ✅ Works with any MCP client

**Cons:**
- ❌ Requires MCP-compatible environment
- ❌ Less direct control for humans
- ❌ Debugging can be harder
- ❌ Newer standard (less mature)

**Best For:**
- Fully agentic workflows
- Organizations using Claude Desktop, Cursor, etc.
- Advanced users
- Future state

---

### Option 3: IDE Extension

**Concept:** VS Code / JetBrains extension

**Example Usage:**
```
Command Palette: "Agentic SDLC: Create New Spec"
→ Opens form for spec details
→ Generates spec file
→ Highlights sections to complete
→ Shows validation status inline
→ One-click handoff generation
→ Visual milestone tracker
```

**Features:**
- Sidebar with project status
- Spec templates with snippets
- Inline validation (squiggles)
- Handoff packet wizard
- Metrics dashboard
- One-click guardrail execution

**Pros:**
- ✅ Most discoverable
- ✅ Visual progress tracking
- ✅ Integrated into workflow
- ✅ Rich UI possible
- ✅ Beginner-friendly

**Cons:**
- ❌ IDE-specific (multiple implementations needed)
- ❌ Slower to develop
- ❌ Harder to automate
- ❌ Not universal

**Best For:**
- Beginners
- Visual learners
- Teams using specific IDEs
- Long-term adoption

---

### Option 4: Web Dashboard (Like GStack)

**Concept:** Web-based project management

**Example Usage:**
```
Web UI:
├── Projects List
│   └── Create New Project
├── Active Specs
│   ├── View/Edit
│   ├── Validate
│   └── Approve
├── Milestones
│   ├── Visual Progress
│   ├── Handoff Packets
│   └── Status
├── Metrics
│   ├── Weekly Scorecard
│   ├── Trends
│   └── Team Performance
└── Settings
    ├── Templates
    ├── Guardrails
    └── Integrations
```

**Pros:**
- ✅ Most accessible (any device)
- ✅ Rich visualizations
- ✅ Team collaboration
- ✅ Executive dashboards
- ✅ No installation

**Cons:**
- ❌ Requires hosting
- ❌ Network dependency
- ❌ Harder to integrate with dev tools
- ❌ Most expensive to build/maintain

**Best For:**
- Executive visibility
- Team coordination
- Non-technical stakeholders
- Large organizations

---

## Recommended Phased Approach

### Phase 1: CLI Foundation — Complete

**Goal:** Get framework into hands of early adopters

**Deliverables (implemented):**
1. `agentic-sdlc` CLI tool
2. Core commands: init, spec (create/validate/list), handoff (create/validate/list), check, metrics
3. Configuration file support (.agentic-sdlc.yaml)
4. Integration with existing templates

**Why First:**
- Fastest to build
- Works for everyone
- Proves concept
- Gathers feedback
- Foundation for other interfaces

**Implementation:**
```python
# Python CLI with Click or Typer
import click

@click.group()
def cli():
    """Agentic SDLC Framework CLI"""
    pass

@cli.command()
@click.argument('project_name')
def init(project_name):
    """Initialize new project"""
    # Copy templates, create structure
    pass

@cli.command()
@click.option('--template', default='api')
@click.option('--title', prompt=True)
def spec(template, title):
    """Create new specification"""
    # Generate spec from template
    pass

@cli.command()
def validate():
    """Validate current spec"""
    # Run validation scripts
    pass
```

---

### Phase 2: MCP Server — Complete

**Goal:** Enable fully agentic workflows

**Deliverables (implemented — see `tools/mcp-server/server.py`):**
1. MCP server exposing framework tools
2. Integration with Claude Desktop
3. Self-managing agent workflows
4. Handoff packet automation

**Why Second:**
- Builds on CLI foundation
- Enables advanced use cases
- Proves framework works with agents
- Gathers agent-specific feedback

**Implementation:**
```python
# MCP server
from mcp.server import Server

server = Server("agentic-sdlc")

@server.tool()
def create_spec(title: str, template: str = "api") -> str:
    """Create agent-ready specification"""
    # Use CLI library
    pass

@server.tool()
def validate_spec(spec_path: str) -> dict:
    """Validate spec completeness"""
    # Return structured results
    pass
```

---

### Phase 3: IDE Extension (Month 3-4)

**Goal:** Make framework accessible to broader audience

**Deliverables:**
1. VS Code extension
2. JetBrains plugin (later)
3. Visual spec editor
4. Inline validation
5. Milestone tracker

**Why Third:**
- Requires stable CLI/API
- More complex development
- Needs user feedback from CLI
- Different audience

---

### Phase 4: Web Dashboard (Month 6+)

**Goal:** Enterprise adoption and executive visibility

**Deliverables:**
1. Web application
2. Project management features
3. Team collaboration
4. Executive dashboards
5. Integration with CLI

**Why Last:**
- Most expensive
- Requires product-market fit
- Needs hosting infrastructure
- Enterprise sales process

---

## CLI Design Detail

### Command Structure

```
agentic-sdlc
├── init                    # Initialize project
├── config                  # Manage configuration
├── spec
│   ├── create             # Create new spec
│   ├── validate           # Validate spec
│   ├── approve            # Mark as approved
│   └── list               # List specs
├── handoff
│   ├── create             # Create handoff packet
│   ├── validate           # Validate handoff
│   └── list               # List handoffs
├── implement              # Start implementation phase
├── check                  # Run guardrails
├── deploy                 # Deployment commands
├── metrics                # Generate reports
└── template
    ├── list               # List templates
    ├── create             # Create custom template
    └── edit               # Edit template
```

### Configuration

```yaml
# .agentic-sdlc.yaml
project:
  name: "My Project"
  type: "api"  # api, web, ml, etc.
  
framework:
  version: "1.0.0"
  strict_mode: true
  
templates:
  spec: "templates/agent-ready-spec.md"
  handoff: "templates/handoff-packet.md"
  adr: "templates/architecture-decision-record.md"
  
guardrails:
  min_coverage: 80
  max_complexity: 10
  security_scan: true
  
agents:
  planner: "claude-code"
  executor: "claude-code"
  reviewer: "claude-code"
  
integrations:
  github:
    repo: "owner/repo"
    actions: true
  slack:
    channel: "#project-updates"
  
compliance:
  data_classification: "internal"
  requires_audit: true
  retention_days: 2555  # 7 years
```

### Interactive Mode

```bash
# Guided project creation
$ agentic-sdlc init --interactive
? Project name: my-api
? Project type: API
? Data classification: Internal
? Compliance requirements: Audit trail
✓ Created project structure
✓ Generated initial spec template
✓ Configured guardrails
✓ Ready to start!

# Guided spec creation
$ agentic-sdlc spec create --interactive
? Title: User Authentication Service
? Priority: P1
? Estimated effort: 16 hours
? Business value: Reduce login friction
✓ Created spec at specs/AUTH-001.md
✓ Pre-filled template sections
? Open in editor? (Y/n)
```

---

## Integration with Existing Tools

### GitHub Integration

```yaml
# .github/workflows/agentic-sdlc.yml
name: Agentic SDLC

on:
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: agentic-sdlc/action@v1  # GitHub Action not yet published
        with:
          command: check --all
          fail-on-error: true
      
      - name: Validate spec changes
        run: |
          if git diff --name-only | grep -q "specs/"; then
            agentic-sdlc spec validate --changed
          fi
      
      - name: Check handoff packets
        run: |
          agentic-sdlc handoff validate --all
      
      - name: Generate metrics
        run: |
          agentic-sdlc metrics --pr ${{ github.event.number }}
```

### Slack Integration

```yaml
# Notification on milestone complete
notifications:
  slack:
    on:
      - spec.approved
      - milestone.completed
      - deployment.success
      - security.alert
    channels:
      - "#engineering"
      - "#compliance"
```

---

## Comparison: Our Approach vs. GStack

| Aspect | GStack (Gary Tan) | Agentic SDLC Framework |
|--------|-------------------|------------------------|
| **Primary Interface** | CLI + Web | CLI → MCP → IDE → Web |
| **Target User** | Startup founders | Engineers + Enterprises |
| **Focus** | Project scaffolding | Full SDLC with governance |
| **AI Integration** | Template generation | Multi-agent coordination |
| **Compliance** | Minimal | Built-in |
| **Customization** | Limited | Extensive templates |
| **Open Source** | Unknown | Yes (MIT) |

**Key Differentiator:**
- GStack: "Generate a project quickly"
- Agentic SDLC: "Guide the entire development lifecycle with governance"

---

## Implementation Priority

### Immediate (Week 1-2)

1. **CLI Core**
   - `init` command
   - `spec create` command
   - `validate` command
   - Basic configuration

2. **Package & Distribute**
   - PyPI package: `agentic-sdlc`
   - Homebrew formula
   - Docker image

### Short-term (Month 1)

3. **Complete CLI**
   - All commands implemented
   - Interactive mode
   - Configuration management
   - GitHub Actions integration

4. **Documentation**
   - CLI reference
   - Tutorial videos
   - Example projects

### Medium-term (Month 2-3)

5. **MCP Server**
   - Tool definitions
   - Claude Desktop integration
   - Self-managing workflows

6. **VS Code Extension**
   - Basic commands
   - Spec editor
   - Validation UI

### Long-term (Month 6+)

7. **Web Dashboard**
   - Project management
   - Team features
   - Executive dashboards

---

## Recommendation

**Start with CLI. Here's why:**

1. **Fastest path to value** — Users can start today
2. **Proves the framework** — Validates the concept
3. **Foundation for everything** — MCP, IDE, Web all use CLI
4. **Universal** — Works for everyone immediately
5. **Low maintenance** — Easier to support than GUI

**Then add MCP** for power users who want fully agentic workflows.

**Then IDE extensions** for broader adoption.

**Finally web dashboard** for enterprise sales.

---

## Next Steps

1. **Build CLI MVP** (This week)
   - Core commands: init, spec create, validate
   - Package for PyPI
   - Basic documentation

2. **Test with real project** (Next week)
   - Use on personal Task API
   - Gather feedback
   - Iterate

3. **Add remaining commands** (Week 3-4)
   - Complete command set
   - Interactive mode
   - Configuration

4. **Publish & Share** (Month 2)
   - Blog post
   - Hacker News
   - Reddit
   - Twitter

5. **Gather feedback** (Ongoing)
   - GitHub issues
   - Discord/Slack community
   - User interviews

6. **Plan MCP** (Month 2-3)
   - Based on CLI usage patterns
   - Agent workflow learnings

---

## File Structure for CLI

```
agentic-sdlc-cli/
├── pyproject.toml
├── README.md
├── src/
│   └── agentic_sdlc/
│       ├── __init__.py
│       ├── cli.py              # Main CLI entry
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── init.py
│       │   ├── spec.py
│       │   ├── handoff.py
│       │   ├── check.py
│       │   ├── deploy.py
│       │   └── metrics.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py     # Configuration management
│       │   ├── templates.py  # Template handling
│       │   └── validation.py # Validation logic
│       └── utils/
│           ├── __init__.py
│           ├── git.py
│           └── output.py
├── tests/
│   └── test_*.py
└── docs/
    └── cli-reference.md
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| CLI installs | 100 in Month 1 | PyPI downloads |
| Active users | 20 in Month 2 | GitHub stars + issues |
| Specs created | 50 in Month 2 | Telemetry (opt-in) |
| Validation runs | 200 in Month 2 | Telemetry |
| MCP adoption | 10 users in Month 3 | MCP server connections |
| IDE installs | 50 in Month 4 | Extension downloads |

---

## Conclusion

**The play:**
1. **Build CLI first** — Fastest to market, universal
2. **Add MCP second** — Enable agentic workflows
3. **IDE third** — Broaden adoption
4. **Web last** — Enterprise scale

This approach lets us prove the framework, gather feedback, and build incrementally toward the full vision.
