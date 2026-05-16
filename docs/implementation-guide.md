# Implementation Guide

## Overview

This guide walks through setting up and operating the Agentic SDLC Framework from first commit to production cadence. Two tracks are covered: personal projects (you can be running in a day) and enterprise deployments (four-week structured rollout). Both tracks use the same FRAME methodology and the same tooling — the difference is governance overhead and stakeholder coordination.

---

## Track 1: Personal Project Quick Start (Week 1)

This track assumes a single developer, a GitHub repository, and no compliance requirements. The goal is to establish the full feedback loop — spec, implement, guardrails, measure — on something real before the process becomes habit.

### Day 1: Repository Setup

**Prerequisites:**
- Git installed
- Python 3.11+
- GitHub account (free tier is sufficient)

```bash
# Clone the framework
git clone https://github.com/bigknoxy/agentic-sdlc-framework.git
cd agentic-sdlc-framework

# Install Python dependencies and CLI from repo root
pip install -e ".[dev]"
# This installs the `agentic-sdlc` CLI (commands: init, spec, handoff, check, metrics)

# Initialize your project directory
mkdir -p my-project/{specs,handoffs,adrs,docs}
```

**Set up pre-commit hooks:**

```bash
pip install pre-commit
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/trufflesecurity/trufflehog
    rev: v3.63.11
    hooks:
      - id: trufflehog
        name: TruffleHog Secret Scan
        entry: trufflehog filesystem --no-update .
        language: system
        pass_filenames: false

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF

pre-commit install
```

**Enable GitHub Actions:**

The framework ships with `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml`. Push to GitHub and confirm both workflows appear in the Actions tab.

```bash
git add .
git commit -m "chore: initialize agentic SDLC framework"
git push origin main
```

### Day 2: Write Your First Executable Spec

Pick one concrete feature — something you would have implemented ad hoc before. Write the spec instead of writing code first.

```bash
# Copy the spec template
cp templates/agent-ready-spec.md my-project/specs/SPEC-$(date +%Y-%m-%d)-001.md

# Open and fill in these required sections:
# 1. Context (Why are we building this?)
# 2. Goal State (Gherkin acceptance criteria)
# 3. Non-Negotiable Constraints (language, dependencies)
# 4. Edge Cases & Error Handling
# 5. Data Classification
nano my-project/specs/SPEC-$(date +%Y-%m-%d)-001.md
```

**Validate the spec before touching implementation:**

```bash
python tools/guardrail-scripts/validate-spec.py my-project/specs/SPEC-$(date +%Y-%m-%d)-001.md
```

A passing validation looks like:

```
✅ Spec validation passed
✅ All required sections found
  ✓ Context
  ✓ Goal State
  ✓ Acceptance Criteria (Gherkin format detected)
  ✓ Edge Cases
  ✓ Data Classification
  ✓ Audit Trail Requirements
```

If sections are missing, fix them before proceeding. Skipping validation defeats the spec discipline.

### Day 3: Run Your First Planner-Executor Handoff

Open Claude Code (or your AI agent of choice) and use the spec as the anchor for the entire conversation.

**Planner prompt:**

```
Read this spec: [paste spec content or attach file]

Break this into milestones. Each milestone should be completable in 30-60 minutes 
and produce a testable artifact. For each milestone, identify:
- What files will be created or modified
- What tests will be written
- What the handoff packet should contain

Do not write any implementation code yet. Output only the milestone plan.
```

**Review and approve the milestone plan.** If the plan looks wrong, correct it now — it is far cheaper to fix a plan than to fix code.

**Executor prompt (one milestone at a time):**

```
Read this handoff packet: [paste previous handoff or starting context]

Implement Milestone 1 only. When complete:
1. Run the tests and include results in your handoff packet
2. Run ruff and confirm linting passes
3. Create a handoff packet for Milestone 2 following the template at 
   templates/handoff-packet.md

Do not proceed to Milestone 2.
```

Copy the handoff packet to `my-project/handoffs/handoff-M1.md` after each milestone:

```bash
python tools/guardrail-scripts/check-handoff-packet.py my-project/handoffs/handoff-M1.md
```

### Day 4: Establish the Golden Task Set

The golden task set is your compound quality indicator. Start small — five tasks is enough.

```bash
mkdir -p my-project/golden-tasks
```

Each task in the set is a real problem representative of your work:
- One bug fix (regression scenario)
- One API extension (new endpoint)
- One data migration (schema change)
- One refactor (extract a module)
- One documentation task (update runbook)

Store each task as a mini-spec:

```
golden-tasks/
├── GT-001-add-pagination.md
├── GT-002-fix-rate-limit-bug.md
├── GT-003-migrate-user-schema.md
├── GT-004-extract-auth-module.md
└── GT-005-update-api-runbook.md
```

Run the set against an agent every Friday and record results in the weekly scorecard template.

### Day 5: Weekly Scorecard Baseline

Generate your first scorecard to establish a baseline:

```bash
python tools/golden-task-set/evaluate.py --week $(date +%Y-%m-%d)
```

Record baseline values manually for the four FRAME metrics:

| Metric | Where to Find It | Baseline Source |
|--------|-----------------|-----------------|
| Task Success Rate | Golden task set results | Count: tasks passed / tasks run |
| Review Rework Rate | PR history | PRs merged with zero re-review / total PRs |
| Escaped Defects | Bug tracker | Bugs opened for issues in the most recent release |
| Median Time-to-Merge | GitHub PR analytics | Median hours from PR open to merge |

Record these in `my-project/metrics/baseline-$(date +%Y-%m-%d).md`. Every subsequent scorecard measures against this baseline.

---

## Track 2: Enterprise Setup (Weeks 1-4)

Enterprise deployment adds three layers the personal track omits: stakeholder alignment, isolated environments, and compliance gates. The four-week plan is structured to produce a working pilot by the end of Week 4 — not a proof of concept, but an actual production-adjacent workflow.

### Week 1: Foundation

**Goals:**
- Executive sponsor identified and briefed
- Environment provisioned
- Team of 2-3 engineers trained on spec format
- Baseline metrics recorded

**Step 1: Executive alignment**

Before any engineering work begins, secure a sponsor who owns the business KPI you are targeting. Without this, the pilot stalls at the first governance checkpoint.

Prepare a one-page brief covering:
- One workflow (not "AI for development" — one specific workflow)
- Current cycle time for that workflow
- 30-day target
- What you are asking from the sponsor (access, a named compliance contact, escalation path)

**Step 2: Provision an isolated environment**

```bash
# Create a dedicated repository for the pilot workflow
# Use GitHub Enterprise or your approved SCM platform

# Repository structure
pilot-workflow/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml           # Copy from framework
│   │   └── security-scan.yml
│   └── CODEOWNERS
├── specs/
├── handoffs/
├── docs/
└── tools/
    └── guardrail-scripts/   # Copy from framework
```

Configure branch protection before any agent work begins:

```bash
# Via GitHub CLI
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["CI / Lint","CI / Security Scan","CI / Test Scripts"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}'
```

**Step 3: Train the pilot team**

Two sessions, each 90 minutes:

*Session 1: Spec writing workshop*
- Walk through the agent-ready-spec template section by section
- Write one real spec together as a group
- Run validation script live

*Session 2: Planner-executor hands-on*
- Run a complete milestone cycle in the room
- Practice reading and approving handoff packets
- Walk through CI failures and how to respond

**Step 4: Record baselines**

Pull metrics from your existing ticketing and SCM systems for the pilot workflow only. Do not average across the whole engineering org — you need workflow-specific numbers.

```bash
# Suggested data sources:
# - Time-to-merge: GitHub PR analytics or Jira cycle time report
# - Review rework rate: PRs with "re-review requested" label / total PRs
# - Escaped defects: Bug reports opened within 14 days of a release
# - Task success rate: Not yet applicable — set a target, measure in Week 4
```

Store in `docs/metrics/week-1-baseline.md`.

### Week 2: Pipeline Hardening

**Goals:**
- All CI/CD checks enforced and blocking
- Security scan clean on pilot repository
- Pre-commit hooks installed on all engineer workstations
- First real spec approved

**Step 1: Configure CI/CD**

The framework CI workflow covers linting, spec validation, secret detection, and structure checks. For enterprise, add these jobs:

```yaml
# .github/workflows/ci.yml additions

  sast:
    name: SAST Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r src/ -ll -f json -o bandit-report.json || true
          bandit -r src/ -ll

      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/owasp-top-ten
            p/cwe-top-25

  dependency-audit:
    name: Dependency Audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Python dependency audit
        run: |
          pip install safety pip-audit
          pip-audit --format json

      - name: License compliance check
        run: |
          pip install pip-licenses
          pip-licenses --allow-only="MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC" \
            --fail-on-violation
```

**Step 2: Configure pre-commit for all engineers**

Distribute this to the team and verify installation:

```bash
# On each engineer's workstation
cd pilot-workflow/
pip install pre-commit
pre-commit install

# Verify
pre-commit run --all-files
```

**Step 3: Write and approve the first real spec**

The first spec should be modest — something 1-2 days of work, not a multi-week project. Write it using the template, validate it, and get explicit approval from:
- Business stakeholder (value confirmed)
- Technical lead (approach validated)
- Security (if handling data classified above Internal)

```bash
python tools/guardrail-scripts/validate-spec.py specs/SPEC-2025-W2-001.md
# agentic-sdlc check --all  # runs compliance checks via CLI
```

### Week 3: First Pilot Implementation

**Goals:**
- Complete implementation of the Week 2 spec using the multi-agent pattern
- All CI checks green
- PR merged through the standard review process
- Handoff packets stored and validated

Run the full planner-executor-reviewer cycle:

```bash
# 1. Planner creates milestones (human approves)
# 2. Executor implements one milestone at a time
# 3. After each milestone, validate the handoff packet
python tools/guardrail-scripts/check-handoff-packet.py handoffs/handoff-M1.md

# 4. Generate audit trail entries for each milestone
python tools/guardrail-scripts/generate-audit-trail.py \
  --action "milestone.completed" \
  --actor "claude-code" \
  --actor-type "agent" \
  --resource "SPEC-2025-W2-001-M1" \
  --resource-type "milestone" \
  --result "success" \
  --supervisor "your-name" \
  --log-file audit/audit.jsonl

# 5. Reviewer agent checks against spec before PR
# 6. Human engineer does final review
# 7. Merge with all checks green
```

Do not skip the reviewer agent step. The reviewer is a separate agent pass that reads the spec and the implemented code together and flags any divergence. Treat its output as a pre-review checklist, not a replacement for human review.

### Week 4: Measure and Iterate

**Goals:**
- Collect post-pilot metrics
- Compare against baseline
- Document lessons learned
- Decide: expand, refine, or pause

**Collect metrics:**

```bash
python tools/golden-task-set/evaluate.py --week $(date +%Y-%m-%d)
```

Fill in the four FRAME metrics manually where automation does not yet reach:

| Metric | Formula | Where to Find |
|--------|---------|--------------|
| Task Success Rate | (Tasks passing review on first agent attempt) / (Total tasks attempted) | Track per handoff |
| Review Rework Rate | (PRs merged with zero re-review requests) / (Total PRs merged) | GitHub PR history |
| Escaped Defects | (Bugs reported in production for Week 3 release) | Bug tracker |
| Median Time-to-Merge | Median hours from PR open to merge | GitHub Analytics |

Compare Week 4 numbers against the Week 1 baseline. Present the delta — not the absolute numbers — to your executive sponsor.

---

## Running Your First Pilot

Whether personal or enterprise, the first pilot follows the same execution pattern.

### Pilot Scoping Rules

A good first pilot has all of these properties:

1. **One workflow** — not a category of work, a specific repeating workflow (e.g., "adding a new REST endpoint to the billing service")
2. **Measurable baseline** — you have current cycle time data before you start
3. **Short cycle** — a complete cycle (intake through deployment) takes less than two weeks
4. **Low blast radius** — failure is recoverable; no customer-facing or compliance-critical system as the first target
5. **Willing participants** — the 2-3 engineers on this workflow want to try it, not have it imposed

Use the pilot proposal template to formalize scoping before starting:

```bash
cp templates/pilot-proposal.md pilots/pilot-001-$(date +%Y-%m-%d).md
```

### Pilot Execution Checklist

Before the pilot begins:
- [ ] Spec written and approved
- [ ] Environment provisioned with branch protection
- [ ] Pre-commit hooks installed on all workstations
- [ ] CI pipeline passing on empty commit
- [ ] Baseline metrics recorded
- [ ] Executive sponsor briefed on what "success" means in 30 days

During the pilot:
- [ ] Every task starts from an approved spec (no ad hoc implementation)
- [ ] Every milestone produces a handoff packet
- [ ] Every handoff packet is validated before the next milestone starts
- [ ] Audit trail entries generated for each agent action
- [ ] Weekly scorecard updated every Friday

After the pilot:
- [ ] Metrics compared against baseline
- [ ] Lessons learned documented
- [ ] Decision made: expand, refine, or pause

---

## Configuring CI/CD Guardrails

This section covers the complete CI/CD configuration, building on what ships in the framework.

### Layer 1: Pre-Commit (Local, Runs Before Every Commit)

The pre-commit configuration blocks commits that contain secrets, fail linting, or violate formatting rules. This catches the cheapest-to-fix problems at the cheapest moment.

```yaml
# .pre-commit-config.yaml
repos:
  # Secret scanning
  - repo: https://github.com/trufflesecurity/trufflehog
    rev: v3.63.11
    hooks:
      - id: trufflehog
        name: TruffleHog (secrets)
        entry: trufflehog filesystem --no-update .
        language: system
        pass_filenames: false

  # Python linting and formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy

  # General file hygiene
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key
```

### Layer 2: Pre-Build (CI, Runs on Every PR and Push to Main)

The CI workflow runs checks that are too slow for pre-commit or require a full environment.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ruff mypy
      - run: ruff check src/
      - run: ruff format --check src/
      - run: mypy src/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest tests/ --cov=src --cov-report=xml --cov-fail-under=80

  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install bandit
      - run: bandit -r src/ -ll
      - uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/owasp-top-ten

  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: TruffleHog (PR)
        if: github.event_name == 'pull_request'
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.pull_request.base.sha }}
          head: ${{ github.event.pull_request.head.sha }}
          extra_args: --only-verified
      - name: TruffleHog (Push)
        if: github.event_name == 'push'
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.before }}
          head: ${{ github.event.after }}
          extra_args: --only-verified

  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pip-audit
      - run: pip-audit
```

**All CI jobs must be required status checks in branch protection.** If a job is optional, it will be ignored.

### Layer 3: Pre-Deploy (Runs Before Each Deployment)

Pre-deploy checks run after a PR merges and before the artifact reaches any environment.

```yaml
# .github/workflows/pre-deploy.yml
name: Pre-Deploy Validation

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string

jobs:
  compliance-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Validate audit trail completeness and data classification
        run: |
          # Compliance checks run via CLI
          agentic-sdlc check --all

      - name: Model vulnerability scan
        run: |
          # Check for known prompt injection patterns in agent prompts
          grep -r "system_prompt\|SYSTEM_PROMPT" src/ | \
            grep -v "test\|example\|mock" > /tmp/prompts.txt || true
          if [ -s /tmp/prompts.txt ]; then
            echo "Agent prompts found - manual security review required"
            cat /tmp/prompts.txt
          fi

  container-scan:
    if: hashFiles('Dockerfile') != ''
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t pilot-app:${{ github.sha }} .
      - name: Trivy container scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: pilot-app:${{ github.sha }}
          exit-code: 1
          severity: CRITICAL,HIGH
```

### Layer 4: Runtime Monitoring

For regulated environments, runtime monitoring must be in place before go-live. At minimum:

```yaml
# Runtime monitoring targets (configure in your APM/SIEM)
alerts:
  error_rate:
    threshold: 0.1%        # Alert at 0.1% error rate
    window: 5m
    action: page_on_call

  response_time_p95:
    threshold: 2x_baseline  # Alert at 2x normal p95
    window: 10m
    action: alert_team

  security_event:
    severity: critical
    action: page_security_team

  audit_log_gap:
    description: "Gap in audit log sequence"
    action: alert_compliance
```

---

## Setting Up the Multi-Agent Pattern

The multi-agent pattern has three defined roles: Planner, Executor, and Reviewer. Each role operates on a distinct input and produces a distinct output. Never collapse these into a single agent conversation — context contamination between roles produces worse results than running them separately.

### Role Definitions

**Planner Agent**

Input: Approved spec
Output: Milestone plan with handoff packet templates

The Planner's only job is decomposition. It does not write code. It reads the spec and breaks the work into milestones of 30-90 minutes each, sequenced so each milestone builds cleanly on the previous one.

Planner system prompt:

```
You are a software project planner. Your job is to read an agent-ready spec 
and decompose it into implementation milestones. 

Rules:
- Each milestone must be independently testable
- No milestone touches more than 3-5 files
- Each milestone includes: objective, files to create/modify, tests to write, 
  definition of done, and seed for the next handoff packet
- Do not write any implementation code
- Flag any ambiguities in the spec before producing the plan

Output format: Numbered milestone list, then a handoff packet template 
for Milestone 1.
```

**Executor Agent**

Input: Handoff packet from previous milestone (or Planner output for Milestone 1)
Output: Implemented code + handoff packet for next milestone

The Executor implements exactly one milestone and stops. It runs its own tests and records the results in the handoff packet.

Executor system prompt:

```
You are a software implementation agent. You will receive a handoff packet 
describing one milestone. Implement only that milestone.

Rules:
- Read the handoff packet completely before writing any code
- Implement only what the milestone specifies — no scope creep
- Write tests before or alongside implementation (not after)
- Run all tests before declaring the milestone complete
- If you encounter an ambiguity not resolved in the spec, stop and ask — 
  do not guess
- Produce a complete handoff packet when finished

When done, output: summary of changes, test results, any open risks, 
and the handoff packet for the next milestone.
```

**Reviewer Agent**

Input: Spec + implemented code (for one milestone or full implementation)
Output: Review report flagging divergences from spec

The Reviewer is not a code quality reviewer in the traditional sense. Its job is spec compliance: does the implementation match what the spec required?

Reviewer system prompt:

```
You are a software review agent. You will receive an agent-ready spec and 
the implementation produced for it. Your job is to identify divergences.

Check:
1. Each acceptance criterion — is there test coverage?
2. Each non-negotiable constraint — is it respected?
3. Each edge case — is it handled?
4. Data classification — is data handled at the correct level?
5. Audit trail — are required events logged?

Output format: 
- PASS: criteria met
- FAIL [criterion reference]: specific divergence found
- WARN: potential issue, human judgment needed
```

### Handoff Protocol

Every handoff between agents uses the handoff packet template. Validate each packet before passing it to the next agent:

```bash
# After Planner produces milestone plan
python tools/guardrail-scripts/check-handoff-packet.py handoffs/planner-output.md

# After each Executor milestone
python tools/guardrail-scripts/check-handoff-packet.py handoffs/handoff-M1.md

# Generate audit entry for each milestone completion
python tools/guardrail-scripts/generate-audit-trail.py \
  --file handoffs/handoff-M1.md \
  --log-file audit/audit.jsonl
```

**Do not feed a handoff packet that fails validation to the next agent.** Fix the packet first. An incomplete handoff packet is an information loss event — the Executor will fill gaps with assumptions, and those assumptions will not match the spec.

### Context Refresh at Milestone Boundaries

Long-running agent conversations accumulate context that degrades quality. At each milestone boundary:

1. Do not continue the existing conversation
2. Start a fresh conversation with the Executor
3. The handoff packet is the complete context — it should be self-contained
4. The Executor should not need to ask "what was decided in Milestone 1?" — the handoff packet answers that

This is the entire point of the handoff packet format. A well-written handoff packet is a context checkpoint.

---

## Weekly Evaluation Cadence

The weekly evaluation is 30 minutes on Friday. It is not optional — skipping two weeks in a row means your metrics are no longer tracking reality.

### What to Measure

**Metric 1: Task Success Rate (Golden Set)**

Run the golden task set against your agent configuration every week. Record the number of tasks that pass review on first attempt without human correction.

```
Task Success Rate = (Tasks passing first-attempt review) / (Total tasks run)
```

Target trajectory: Start at whatever your baseline is. Improve by 5-10 points per quarter through spec quality improvements and agent prompt refinement.

Collect this by running each golden task, submitting the output for review, and recording pass/fail before any human correction.

**Metric 2: Review Rework Rate**

Pull this from your PR history each week:

```bash
# GitHub CLI: PRs merged this week with re-review requests
gh pr list --state merged --limit 50 --json number,reviewDecision,reviews \
  | jq '[.[] | select(.reviews | map(.state) | contains(["CHANGES_REQUESTED"]))] | length'

# Total PRs merged this week
gh pr list --state merged --limit 50 --json number | jq 'length'
```

```
Review Rework Rate = (PRs with zero re-review requests) / (Total PRs merged)
```

Target: >70% first-pass approval rate within 8 weeks of starting the framework.

**Metric 3: Escaped Defects**

Count bugs opened in the bug tracker this week that trace to code merged in the previous two weeks.

```
Escaped Defects = Count of production bugs per release cycle
```

This metric lags by 1-2 weeks. Do not try to measure it in real-time. Look back at what shipped two weeks ago and count bugs opened against it since.

Target: <2 escaped defects per release cycle within 12 weeks.

**Metric 4: Median Time-to-Merge**

```bash
# GitHub CLI: calculate median time from PR open to merge for this week
gh pr list --state merged --limit 50 --json number,createdAt,mergedAt \
  | jq 'map((.mergedAt | fromdateiso8601) - (.createdAt | fromdateiso8601)) | sort | .[length/2|floor] / 3600 | round'
```

Output is in hours. Record as median hours from PR open to merge.

Target: 30-40% reduction from baseline within 12 weeks.

### Weekly Review Process

Friday, 30 minutes:

1. **Pull metrics (10 minutes)** — Run the commands above, update the weekly scorecard

2. **Identify trends (10 minutes)** — Is any metric moving in the wrong direction two weeks in a row? That is a signal, not noise.

3. **Update golden task set (5 minutes)** — Did you ship something new this week? Add a representative task to the golden set. Remove tasks that no longer reflect real work.

4. **Plan one improvement (5 minutes)** — Pick one thing to change next week. Not five things. One. Write it down in the scorecard.

```bash
# Generate the scorecard
python tools/golden-task-set/evaluate.py --week $(date +%Y-%m-%d)

# Store it
cp scorecard-output.md docs/metrics/scorecard-$(date +%Y-%m-%d).md
```

### Metrics Trend Interpretation

| Pattern | Likely Cause | Response |
|---------|-------------|----------|
| Task success rate falling | Spec quality degraded, or new task type added | Review recent specs; add examples for new task type |
| Review rework rate rising | Agents drifting from spec; reviewers raising bar | Tighten spec acceptance criteria; check if coding standards changed |
| Escaped defects spiking | Test coverage insufficient; edge cases missed | Add edge case to spec template; expand golden task set |
| Time-to-merge increasing | CI checks blocking; review bottleneck | Profile CI run times; identify review bottlenecks |
| All metrics flat for 4+ weeks | Framework not being used consistently | Audit actual usage; re-engage team |

### Quarterly Framework Review

Every 12 weeks, spend 2-3 hours reviewing the framework itself:

```bash
# Review all spec templates for clarity
# Review golden task set for relevance
# Review CI/CD pipeline for new tools to add
# Review audit trail for gaps
# Review agent prompts for drift

# Document decisions in an ADR
cp templates/architecture-decision-record.md docs/adr/adr-$(date +%Y%m%d)-framework-review.md
```

---

## References

- [Framework Overview](../docs/framework-overview.md)
- [How to Use](../docs/how-to-use.md)
- [Agent-Ready Spec Template](../templates/agent-ready-spec.md)
- [Handoff Packet Template](../templates/handoff-packet.md)
- [Weekly Scorecard Template](../templates/weekly-scorecard.md)
- [Guardrail Scripts](../tools/guardrail-scripts/)
- [DORA Metrics](https://dora.dev/)
- [NeuEon FRAME Framework](https://www.neueon.com/insights/agentic-coding-works-when-technique-leads-a-practical-framework-for-teams/)
