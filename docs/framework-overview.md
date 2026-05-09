# Agentic SDLC Framework Overview

## Executive Summary

The Agentic SDLC Framework enables organizations to incorporate AI coding agents into their software development lifecycle while maintaining governance, security, and compliance standards. It adapts the **FRAME** methodology (Focus, Requirements, Automation guardrails, Multi-agent coordination, Evaluation cadence) for enterprise environments.

**Key Insight:** Technique > Tools. Process discipline drives outcomes more than model choice.

---

## The FRAME Methodology

### 1. Focus: One Business-Critical Workflow

**Principle:** Don't spread pilots across too many use cases. Pick one workflow with obvious business value and run a deep implementation cycle.

**Why:** Creates a clean learning loop, faster signal, and faster executive confidence.

**Example:** A B2B SaaS company with 140 engineers narrowed rollout to API endpoint changes in a high-churn billing service. PR cycle time dropped 40% in six weeks.

**Executive Metric:** Cycle time — report to the board. A focused pilot produces measurable cycle time reduction within one quarter.

### 2. Requirements: Executable Specs

**Principle:** Vague tickets create verbose code and review fatigue. Precise specs produce clean first drafts.

**Approach:** Treat specs as executable guidance. Write constraints, acceptance criteria, edge cases, and test expectations before asking an agent to write implementation code.

**Template:** Use the [Agent-Ready Spec Template](../templates/agent-ready-spec.md)

**Example:** A fintech product squad moved from narrative tickets to a lightweight spec template. First-pass approval rate on agent-generated PRs more than doubled.

**Executive Metric:** Review rework rate — when specs improve, the ratio of PRs that pass review on first attempt climbs.

### 3. Automation: Guardrails in the Pipeline

**Principle:** Agentic systems move fast. Guardrails keep that speed useful.

**Approach:** When coding standards live in automation, agents and humans both align to the same definition of good.

**Components:**
- Pre-commit: Secrets scanning, linting
- Pre-build: SAST, SCA, dependency scanning
- Pre-deploy: Security validation, compliance checks
- Runtime: Anomaly detection, audit logging

**Example:** A 220-person marketplace team tightened linting, formatter rules, test coverage thresholds, and dependency policies. Reviewer comments on style dropped by nearly half.

**Executive Metric:** Defect escape rate — guardrails catch problems before production.

**Security Note:** For regulated industries (fintech, healthcare, government), security and compliance guardrails are "table stakes" — not optional polish.

### 4. Multi-Agent: Planner and Executor Coordination

**Principle:** Long-running agentic work breaks when context becomes muddy. Use defined roles and clean handoffs.

**Approach:** A planner agent breaks work into milestones; an executor agent implements one milestone at a time. Each milestone ends with an artifact packet.

**Handoff Packet:** Contains what changed, why, open risks, and next-step context.

**Example:** A growth-stage infrastructure team used this pattern for a two-week refactor across eight services. They stored handoff packets in a shared workspace and refreshed executor contexts at each milestone boundary.

**Executive Metric:** Deployment reliability — clean handoffs reduce the "works on my machine" problem at scale.

### 5. Evaluation: Weekly Cadence

**Principle:** Technique compounds only when teams measure outcomes consistently.

**Approach:** Maintain a small "golden task set" that reflects real work, then evaluate agent performance against that set every week.

**Investment:** Budget 2-3 days of senior time for initial build and a few hours per quarter for upkeep.

**Example:** A product engineering org built a 25-task golden set covering bug fixes, API extensions, and migration tasks. Weekly evaluation showed one model configuration improved draft speed but increased regression risk. The team kept the speed gain and added targeted validation checks.

**Executive Metric:** Task success rate on the golden set — your compound quality indicator.

---

## The 6-Phase SDLC

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Phase 0: Intake & Triage                                                   │
│  ────────────────────────                                                   │
│  Input: Idea / Business Process Need                                         │
│  Output: Go/No-Go decision                                                   │
│  Gates: Business value, technical feasibility, compliance check            │
├─────────────────────────────────────────────────────────────────────────────┤
│  Phase 1: Executable Spec Generation                                          │
│  ─────────────────────────────────                                          │
│  Input: Approved intake ticket                                               │
│  Output: Agent-ready specification                                           │
│  Gates: Stakeholder approval, executable acceptance criteria                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  Phase 2: Design & Architecture                                             │
│  ────────────────────────────                                               │
│  Input: Executable spec                                                      │
│  Output: Technical design, ADRs, threat model                                │
│  Gates: Architecture review, security review, compliance review              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Phase 3: Implementation (Multi-Agent)                                      │
│  ───────────────────────────────────                                        │
│  Input: Approved design + spec                                               │
│  Output: Production-ready code                                               │
│  Gates: Code review, security scan, test coverage, documentation             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Phase 4: Validation & Security Pass                                        │
│  ───────────────────────────────────                                        │
│  Input: Implementation + test suite                                          │
│  Output: Validated, documented package                                       │
│  Gates: Security approval, compliance sign-off, operations review              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Phase 5: Deployment & Release                                              │
│  ────────────────────────────                                               │
│  Input: Validated implementation                                             │
│  Output: Production deployment                                               │
│  Gates: Deployment approval, canary metrics, post-deployment validation      │
├─────────────────────────────────────────────────────────────────────────────┤
│  Phase 6: Operations & Monitoring                                           │
│  ─────────────────────────────────                                          │
│  Continuous: Performance monitoring, drift detection, compliance auditing     │
│  Output: Continuous improvement, weekly evaluation                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Artifacts

### 1. Agent-Ready Spec

The foundation of the framework. A comprehensive specification that agents can directly implement.

**Sections:**
1. Context (Business Problem)
2. Goal State (Definition of Done)
3. Non-Negotiable Constraints
4. Acceptance Criteria (Executable Tests)
5. Edge Cases & Error Handling
6. Rollback Conditions
7. Data Classification & Handling
8. Audit Trail Requirements
9. Implementation Notes
10. Approval Checklist

**Template:** [templates/agent-ready-spec.md](../templates/agent-ready-spec.md)

### 2. Handoff Packet

Captures the complete state of work at a milestone boundary, enabling seamless handoffs between agents.

**Sections:**
- Milestone Summary
- Work Completed (files created/modified/deleted)
- Test Results
- Security Scan Results
- Open Risks & Issues
- Next Steps
- Next Prompt Seed
- Audit Trail Entry

**Template:** [templates/handoff-packet.md](../templates/handoff-packet.md)

### 3. Architecture Decision Record (ADR)

Documents significant architectural decisions with context, rationale, and consequences.

**Sections:**
- Context
- Decision
- Consequences (positive and negative)
- Alternatives Considered
- Related Decisions

**Template:** [templates/architecture-decision-record.md](../templates/architecture-decision-record.md)

### 4. Weekly Scorecard

Tracks the four key metrics on a weekly cadence.

**Metrics:**
1. Task Success Rate (Golden Set)
2. Review Rework Rate
3. Escaped Defects
4. Median Time-to-Merge

**Template:** [templates/weekly-scorecard.md](../templates/weekly-scorecard.md)

### 5. Pilot Proposal

Structured proposal for starting a new agentic workflow pilot.

**Sections:**
- Business Case
- Scope
- Success Criteria
- Risk Assessment
- Compliance & Security
- Timeline
- Budget

**Template:** [templates/pilot-proposal.md](../templates/pilot-proposal.md)

---

## Security & Compliance

### Data Classification

```yaml
restricted:      # SSN, TIN, account numbers
  allowed_endpoints: []
  requires_approval: true

confidential:    # Member data, financials
  allowed_endpoints: ["internal-api"]
  audit_required: true

internal:        # Business data
  allowed_endpoints: ["internal-api", "approved-saas"]

public:          # Published reports
  allowed_endpoints: ["*"]
```

### Security Gates

| Layer | Checks |
|-------|--------|
| Pre-commit | Secrets scanning, linting |
| Pre-build | SAST, SCA, container scanning |
| Pre-deploy | Model vulnerability scan, compliance validation |
| Runtime | Input validation, rate limiting, anomaly detection |

### Audit Trail

Every agent action must log:
- **Who:** Agent ID + human supervisor
- **What:** Specific action taken
- **When:** Timestamp
- **Why:** Business justification
- **Where:** System/component affected
- **How:** Tool/approach used

---

## Multi-Agent Coordination

### Roles

**Planner Agent:**
- Breaks work into milestones (2-5 minute tasks)
- Defines success criteria for each milestone
- Creates handoff packets

**Executor Agent:**
- Implements one milestone at a time
- Runs tests and security scans
- Documents changes

**Reviewer Agent:**
- Reviews code against standards
- Validates test coverage
- Checks security compliance

**Security Agent:**
- Continuous security scanning
- Validates data handling
- Checks compliance requirements

### Handoff Process

```
Planner → Executor → Reviewer → Security → (Next Milestone)
   ↓          ↓          ↓          ↓
Handoff   Handoff   Handoff   Handoff
Packet    Packet    Packet    Packet
```

Each handoff packet includes:
- Objective
- Files touched
- Tests run
- Security scan results
- Open risks
- Next prompt seed
- Audit trail entry

---

## Implementation Roadmap

### Phase A: Foundation (Weeks 1-4)

**Goal:** Prove the framework on personal projects

**Activities:**
- Set up version control with PR templates
- Implement basic CI/CD
- Create agent-ready spec template
- Define handoff packet format
- Establish golden task set

**Deliverables:**
- Working framework on personal project
- Refined templates based on usage
- Initial metrics baseline

### Phase B: Pilot (Weeks 5-12)

**Goal:** Demonstrate value on one business-critical workflow

**Activities:**
- Get executive sponsor
- Define 30-day success targets
- Set up isolated environment
- Configure security guardrails
- Train 2-3 engineers

**Deliverables:**
- Working pilot
- Measurable improvements
- Lessons learned

### Phase C: Scale (Weeks 13-24)

**Goal:** Expand to 3-5 workflows, refine governance

**Activities:**
- Add second workflow
- Refine guardrails
- Build training materials
- Create compliance documentation
- Establish weekly evaluation

**Deliverables:**
- Multiple successful pilots
- Refined processes
- Internal training materials

### Phase D: Production (Weeks 25+)

**Goal:** Standard operating procedure

**Activities:**
- Integrate with formal change management
- Train broader engineering team
- Establish center of excellence
- Continuous improvement

**Deliverables:**
- Standard process
- Trained teams
- Measured ROI

---

## Tool Stack

### Personal Projects (Free/Open Source)

| Layer | Tool |
|-------|------|
| Agent Platform | Claude Code, GitHub Copilot |
| CI/CD | GitHub Actions |
| Security | GitHub Advanced Security, Bandit, Semgrep |
| Testing | pytest, jest |
| Linting | ruff, black, eslint |
| Documentation | MkDocs |

### Enterprise (Regulated)

| Layer | Options |
|-------|---------|
| Agent Platform | GitHub Copilot Enterprise, Amazon CodeWhisperer |
| CI/CD | GitHub Enterprise, Azure DevOps, GitLab Enterprise |
| Security | SonarQube Enterprise, Snyk, Checkmarx |
| Secrets | HashiCorp Vault, Azure Key Vault |
| Documentation | Confluence + auto-gen |
| Monitoring | Splunk, Datadog |
| Audit | Splunk, ELK Stack |

---

## Getting Started

### Week 1: Quick Start

1. **Choose one workflow** with direct KPI impact
2. **Write one executable spec** using the template
3. **Automate one quality gate** in CI
4. **Test one planner-executor handoff**
5. **Track one weekly scorecard**

That is enough to create momentum. From there, your framework evolves from opinion into operating system.

### Resources

- [Personal Project Example](../examples/personal-project-example/)
- [Enterprise Pilot Example](../examples/enterprise-pilot-example/)
- [Implementation Plan](../docs/implementation-plan.md)
- [Guardrail Scripts](../tools/guardrail-scripts/)

---

## Success Stories

### B2B SaaS Company (140 engineers)

**Workflow:** API endpoint changes in billing service

**Results:**
- PR cycle time: -40%
- First-pass approval: +35 points
- Defect escape rate: -60%

### Fintech Product Squad

**Workflow:** Backend feature development

**Results:**
- First-pass PR approval: >70%
- Review rework: -50%
- Spec quality: +40%

### Marketplace Team (220 engineers)

**Workflow:** General development

**Results:**
- Review comments on style: -50%
- Shift to product logic: +30%
- Defect escape rate: -40%

---

## Contributing

This framework is developed using itself. See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](../LICENSE)

---

## References

- [NeuEon FRAME Framework](https://www.neueon.com/insights/agentic-coding-works-when-technique-leads-a-practical-framework-for-teams/)
- [DORA Metrics](https://dora.dev/)
- [McKinsey 2025 State of AI](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
