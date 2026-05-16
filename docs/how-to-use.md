# How to Use the Agentic SDLC Framework

## Quick Start Guide

This guide explains how to actually use the framework on a real project — what steps to take, what's automated, and what requires human judgment.

---

## Overview: Automated vs. Manual

| Activity | Automation Level | Human Role |
|----------|-----------------|------------|
| **Intake & Triage** | Semi-automated | Decision maker |
| **Spec Writing** | Template-guided | Author + Reviewer |
| **Design & ADRs** | Template-assisted | Architect + Reviewers |
| **Implementation** | Agent-driven | Supervisor/Reviewer |
| **Validation** | Fully automated | Gate approver |
| **Deployment** | Automated with gates | Approver + Monitor |
| **Operations** | Automated monitoring | Responder + Improver |

---

## Phase-by-Phase Usage

### Phase 0: Intake & Triage

**Time:** 30 minutes - 2 hours
**Automation:** Semi-automated

#### Step 1: Create Intake Ticket

**Manual:** Fill out intake template

```bash
# Copy template
cp templates/pilot-proposal.md my-project/intake.md

# Edit with your details
nano my-project/intake.md
```

**Key fields to complete:**
- Idea description
- Business value
- Scope
- Risk assessment
- Compliance notes

#### Step 2: Automated Feasibility Check

**Semi-automated:** Run guardrail scripts

```bash
# Validate intake completeness
python tools/guardrail-scripts/validate-intake.py my-project/intake.md

# Check for common issues (runs via CLI)
# agentic-sdlc check --all
```

**What it checks:**
- All required sections present
- Data classification specified
- Risk assessment complete
- Compliance requirements identified

#### Step 3: Human Decision

**Manual:** Go/No-Go decision

**Who decides:**
- Personal project: You
- Enterprise: Business sponsor + technical lead

**Criteria:**
- [ ] Business value articulated
- [ ] Technical feasibility confirmed
- [ ] Compliance concerns addressed
- [ ] Resources available

**Output:** Approved intake ticket

---

### Phase 1: Executable Spec Generation

**Time:** 2-4 hours
**Automation:** Template-guided

#### Step 1: Copy Spec Template

**Manual:**

```bash
# Copy template
cp templates/agent-ready-spec.md my-project/spec.md

# Fill in frontmatter
nano my-project/spec.md
```

**Required frontmatter:**
```yaml
---
spec_id: SPEC-2025-01-15-001
title: My Feature
status: draft
priority: p1
estimated_effort: 8 hours
---
```

#### Step 2: Write the Spec

**Manual with AI assistance:**

**Option A: Write yourself**
- Fill in each section
- Use examples for guidance
- Be specific and testable

**Option B: Use AI agent**
```
"I need to write an agent-ready spec for [feature]. 
Here's the business context: [context].
Please help me draft sections 1-3, then I'll review."
```

**Critical sections to get right:**
1. **Context** — Why are we building this?
2. **Acceptance Criteria** — Gherkin format tests
3. **Constraints** — Security, compliance, technical
4. **Edge Cases** — What could go wrong?

#### Step 3: Automated Validation

**Automated:** Run spec validator

```bash
# Validate spec completeness
python tools/guardrail-scripts/validate-spec.py my-project/spec.md

# Output example:
# ✅ Spec validation passed
# ✅ All required sections found
#   ✓ Context
#   ✓ Goal State
#   ✓ Acceptance Criteria
#   ✓ Edge Cases
#   ...
```

**What it validates:**
- YAML frontmatter complete
- All 10 required sections present
- Gherkin format in acceptance criteria
- Data classification selected
- Approval gates defined

#### Step 4: Human Review

**Manual:** Get approvals

**Required approvals:**
- [ ] Business stakeholder (value confirmed)
- [ ] Technical lead (approach validated)
- [ ] Security (if handling sensitive data)
- [ ] Compliance (if regulatory requirements)

**Update spec:**
```yaml
status: approved
```

---

### Phase 2: Design & Architecture

**Time:** 2-4 hours
**Automation:** Template-assisted

#### Step 1: Create ADR (if needed)

**Manual:** Document significant decisions

```bash
# Copy template
cp templates/architecture-decision-record.md my-project/adr-001.md

# Document decision
nano my-project/adr-001.md
```

**When to create ADR:**
- New framework/library choice
- Architecture pattern decision
- Data storage choice
- Security approach

#### Step 2: Threat Model (if needed)

**Manual:** Security review

**For regulated/financial projects:**
- Create threat model
- Identify attack vectors
- Define mitigations

#### Step 3: Automated Checks

**Automated:** Security validation

```bash
# Check for security considerations (runs via CLI)
# agentic-sdlc check --all
```

#### Step 4: Human Review

**Manual:** Design review

**Reviewers:**
- Technical lead
- Security (if applicable)
- Architecture board (if applicable)

---

### Phase 3: Implementation (Multi-Agent)

**Time:** Variable (spec-dependent)
**Automation:** Agent-driven with supervision

This is where the magic happens — but it's **supervised automation**, not full auto-pilot.

#### Step 1: Planner Agent Creates Milestones

**Automated with human review:**

**Input:** Approved spec
**Process:**
```
Planner Agent reads spec → Breaks into milestones → Creates handoff packets
```

**Example output:**
```markdown
## Milestone 1: Project Setup
- Create directory structure
- Set up dependencies
- Configure database
- Write initial tests

## Milestone 2: Core Models
- Define SQLAlchemy models
- Create Pydantic schemas
- Write model tests

## Milestone 3: CRUD Operations
- Implement create endpoint
- Implement read endpoint
- ...
```

**Human action:** Review and approve milestones

#### Step 2: Executor Agent Implements

**Automated with supervision:**

**For each milestone:**
```
Executor Agent receives handoff packet → Implements code → Runs tests → Creates handoff packet
```

**Your role as supervisor:**
1. **Watch** — Monitor agent progress
2. **Guide** — Clarify when stuck
3. **Review** — Check handoff packet
4. **Approve** — Accept or request changes

**Example interaction:**
```
Agent: "I've implemented Milestone 1. Here's the handoff packet."
You: Review handoff-packet-001.md
You: "Looks good, proceed to Milestone 2."
```

#### Step 3: Automated Guardrails Run

**Fully automated:**

```bash
# These run automatically in CI/CD
git commit -m "feat: milestone 1"

# CI automatically runs:
- Linting (ruff, black)
- Type checking (mypy)
- Security scanning (bandit, semgrep)
- Test execution (pytest)
- Coverage check (>80%)
```

**If any check fails:**
- Pipeline blocks
- Agent must fix
- Re-runs automatically

#### Step 4: Reviewer Agent Checks Quality

**Automated:**

```
Reviewer Agent → Reads code → Checks against spec → Validates tests → Approves or flags issues
```

**What reviewer checks:**
- Matches spec requirements
- Follows coding standards
- Has adequate tests
- No security issues
- Documentation complete

#### Step 5: Human Code Review

**Manual:**

**Required before merge:**
- [ ] Senior engineer review
- [ ] Security scan clean
- [ ] All tests passing
- [ ] Documentation complete

**Review focus:**
- Business logic correctness
- Architecture alignment
- Security considerations
- Edge case handling

---

### Phase 4: Validation & Security Pass

**Time:** 1-2 hours
**Automation:** Fully automated with human gates

#### Step 1: Security Scanning

**Fully automated:**

```bash
# SAST (Static Application Security Testing)
bandit -r src/
semgrep --config=auto src/

# SCA (Software Composition Analysis)
safety check
snyk test

# Secrets scanning
trufflehog filesystem .
gitleaks detect

# Container scanning (if applicable)
trivy image myapp:latest
```

**Results:**
- Critical/High vulnerabilities → Block deployment
- Medium/Low → Review and decide
- Clean → Proceed

#### Step 2: Compliance Validation

**Automated:**

```bash
# Check audit trail completeness and validate data handling (runs via CLI)
agentic-sdlc check --all
```

#### Step 3: Human Approval Gates

**Manual:** Final sign-offs

**Required approvals:**
- [ ] Security team (if required)
- [ ] Compliance officer (if required)
- [ ] Operations team (runbook review)

---

### Phase 5: Deployment

**Time:** 30 minutes - 2 hours
**Automation:** Automated with approval gates

#### Step 1: Deployment Preparation

**Semi-automated:**

```bash
# Build and package
make build

# Run pre-deployment checks
make pre-deploy-checks
```

#### Step 2: Canary Deployment

**Fully automated:**

```yaml
# GitHub Actions or similar
deployment:
  strategy:
    canary:
      steps:
        - 5% traffic for 10 minutes
        - 25% traffic for 30 minutes
        - 50% traffic for 1 hour
        - 100% traffic
      rollback:
        error_rate > 1%
        latency_p95 > 2x baseline
```

**Monitoring:**
- Error rates
- Response times
- Business metrics
- Security alerts

#### Step 3: Automatic Rollback (if needed)

**Fully automated:**

```
If error_rate > threshold:
  - Alert on-call
  - Automatically rollback
  - Preserve logs
  - Create incident ticket
```

#### Step 4: Human Approval for Full Rollout

**Manual:**

**After canary succeeds:**
- [ ] Manager approval for 100%
- [ ] Post-deployment validation
- [ ] Stakeholder notification

---

### Phase 6: Operations & Monitoring

**Time:** Ongoing
**Automation:** Continuous

#### Step 1: Automated Monitoring

**Fully automated:**

| Metric | Tool | Alert When |
|--------|------|-----------|
| Error rate | Datadog/Splunk | > 0.1% |
| Response time | APM | > 2x baseline |
| Security events | SIEM | Any critical |
| Data drift | Custom | Detected |

#### Step 2: Weekly Evaluation

**Semi-automated:**

```bash
# Generate weekly scorecard
python tools/golden-task-set/evaluate.py --week 2025-01-15
```

**Manual:** Review and action

**30-minute weekly review:**
1. Review 4 key metrics
2. Identify trends
3. Update golden task set
4. Plan improvements

#### Step 3: Continuous Improvement

**Manual:**

- Monthly: Refine templates
- Quarterly: Review framework
- Annually: Major updates

---

## Daily Workflow Example

### Day 1: Start New Feature

```bash
# 9:00 AM - Create spec from template
cp templates/agent-ready-spec.md specs/FEATURE-001.md

# 9:30 AM - Fill in details (with AI assistance)
# "Help me write the Context section for [feature]"

# 11:00 AM - Validate spec
python tools/guardrail-scripts/validate-spec.py specs/FEATURE-001.md
# ✅ Validation passed

# 11:30 AM - Get approval
# Send to tech lead for review

# 2:00 PM - Approved, start implementation
# Planner agent creates milestones
```

### Day 2-3: Implementation

```bash
# Morning - Review handoff packet from yesterday
# "Milestone 1 complete, here's what was done..."

# Approve and continue
# Executor agent works on Milestone 2

# Throughout day - CI runs automatically
# - Tests pass ✅
# - Security scan clean ✅
# - Linting passes ✅

# End of day - Review handoff packet
# Plan tomorrow
```

### Day 4: Validation & Deploy

```bash
# Morning - Security scan
# All checks automated

# Noon - Human approval
# Tech lead reviews PR

# 2:00 PM - Deploy to canary
# Automated, monitored

# 4:00 PM - Canary successful
# Approve full rollout
```

---

## What's Automated vs. Manual Summary

### Fully Automated (No Human Intervention)

| Process | Tool | When It Runs |
|---------|------|--------------|
| Linting | ruff, black | Every commit |
| Type checking | mypy | Every commit |
| Unit tests | pytest | Every commit |
| Security scanning | bandit, semgrep | Every commit + nightly |
| Dependency scanning | safety, snyk | Every commit + daily |
| Secret detection | trufflehog, gitleaks | Every commit |
| Spec validation | validate-spec.py | On demand + CI |
| Handoff validation | check-handoff-packet.py | On demand + CI |
| Canary progression | GitHub Actions | During deployment |
| Automatic rollback | GitHub Actions | On failure detection |
| Metrics collection | Datadog/Splunk | Continuous |
| Audit logging | Custom | Every action |

### Semi-Automated (Human-Guided)

| Process | Human Role | Automation |
|---------|-----------|------------|
| Spec writing | Author/reviewer | AI assistance, template validation |
| Code generation | Supervisor | Agent writes, human reviews |
| Test generation | Reviewer | Agent generates, human validates |
| Documentation | Reviewer | Auto-generates, human edits |
| Milestone planning | Approver | Agent breaks down, human confirms |
| Deployment approval | Decision maker | Automated checks, human gate |

### Fully Manual (Human-Only)

| Process | Why Manual |
|---------|-----------|
| Business decisions | Requires judgment |
| Architecture decisions | Strategic thinking |
| Security approvals | Compliance requirement |
| Final code review | Quality assurance |
| Incident response | Context-dependent |
| Stakeholder communication | Human relationship |
| Framework evolution | Strategic direction |

---

## Tool Commands Quick Reference

### Validation

```bash
# Validate spec
python tools/guardrail-scripts/validate-spec.py path/to/spec.md

# Validate handoff packet
python tools/guardrail-scripts/check-handoff-packet.py path/to/handoff.md

# Generate audit entry
python tools/guardrail-scripts/generate-audit-trail.py \
  --action "spec.approved" \
  --actor "josh" \
  --resource "SPEC-001"
```

### CI/CD

```bash
# Run all checks locally
make check

# Run tests
make test

# Run security scan
make security

# Build and deploy
make deploy
```

### Metrics

```bash
# Generate weekly scorecard
python tools/golden-task-set/evaluate.py --week 2025-01-15

# View metrics dashboard
open https://datadog.mycompany.com/dashboard
```

---

## Getting Started Checklist

- [ ] Clone framework repository
- [ ] Install dependencies (`pip install -e ".[dev]"`)
- [ ] Set up CI/CD (GitHub Actions configured)
- [ ] Choose first project (personal or pilot)
- [ ] Copy spec template
- [ ] Fill in spec (with AI help)
- [ ] Run validation scripts
- [ ] Get approval
- [ ] Start implementation
- [ ] Set up weekly evaluation

---

## Common Questions

### Q: Do I need to use AI agents?
**A:** No. The framework works with or without AI. The templates and process improve any development workflow. AI agents just accelerate implementation.

### Q: Can I skip phases?
**A:** Not recommended. Each phase catches different types of issues. Skipping early phases creates more work later.

### Q: How long does a typical project take?
**A:** Depends on scope. Personal projects: 1-2 days. Enterprise features: 1-2 weeks. The framework reduces time by 40-60%.

### Q: What if the AI generates bad code?
**A:** Guardrails catch most issues. Human code review catches the rest. The framework assumes AI assistance, not replacement.

### Q: Is this suitable for regulated industries?
**A:** Yes. The framework includes compliance gates, audit trails, and security checks specifically for regulated environments.

---

## Next Steps

1. **Try the personal project example** — Build the Task API
2. **Prepare AFC pilot** — Use the enterprise example
3. **Customize templates** — Adapt to your environment
4. **Measure results** — Track the 4 key metrics
5. **Iterate** — Improve the framework as you use it
