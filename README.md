# Agentic SDLC Framework

A production-ready framework for incorporating AI agents into the software development lifecycle, with built-in governance, security, auditing, and self-documentation.

## Overview

This framework adapts the **FRAME** methodology (Focus, Requirements, Automation guardrails, Multi-agent coordination, Evaluation cadence) for enterprise environments, particularly regulated industries like banking and financial services.

## The FRAME-Enhanced SDLC

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 0: Intake & Triage                                       │
│  Phase 1: Executable Spec Generation                            │
│  Phase 2: Design & Architecture                                 │
│  Phase 3: Implementation (Multi-Agent)                          │
│  Phase 4: Validation & Security Pass                            │
│  Phase 5: Deployment & Release                                    │
│  Phase 6: Operations & Monitoring                               │
└─────────────────────────────────────────────────────────────────┘
```

## Key Principles

1. **Technique > Tools** — Process discipline drives outcomes more than model choice
2. **Executable Specs** — Requirements that agents can directly implement
3. **Automated Guardrails** — Security and compliance built into the pipeline
4. **Multi-Agent Coordination** — Planner → Executor → Reviewer with handoff packets
5. **Continuous Evaluation** — Weekly metrics on golden task set

## Quick Start

1. Review the [Framework Documentation](docs/framework-overview.md)
2. Use the [Agent-Ready Spec Template](templates/agent-ready-spec.md)
3. Follow the [Implementation Guide](docs/implementation-guide.md)
4. Track progress with [Weekly Scorecard](templates/weekly-scorecard.md)

## Repository Structure

```
.
├── README.md
├── docs/
│   ├── framework-overview.md
│   ├── implementation-guide.md
│   ├── security-guardrails.md
│   └── compliance-requirements.md
├── templates/
│   ├── agent-ready-spec.md
│   ├── architecture-decision-record.md
│   ├── handoff-packet.md
│   ├── weekly-scorecard.md
│   └── pilot-proposal.md
├── examples/
│   ├── personal-project-example/
│   └── enterprise-pilot-example/
├── tools/
│   ├── ci-cd-configs/
│   └── guardrail-scripts/
└── LICENSE
```

## Contributing

This framework is being developed iteratively. See [Implementation Plan](docs/implementation-plan.md) for current phase.

## License

MIT License - See LICENSE file
