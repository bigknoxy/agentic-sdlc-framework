---
pilot_id: PILOT-2026-AFC-001
title: Agentic SDLC Pilot — Member Services API, Apex Financial Corp
status: proposed
proposed_date: 2026-05-15
duration_weeks: 4
team_size: 3
risk_level: Medium
regulatory_impact: High
---

# Agentic SDLC Pilot Proposal

## Executive Summary

| Field | Value |
|-------|-------|
| **Organization** | Apex Financial Corp |
| **Workflow** | API endpoint changes — Member Services API (member data, advance requests, collateral management) |
| **Proposed Start Date** | 2026-06-02 |
| **Duration** | 4 weeks (30-day pilot) |
| **Pilot Phase** | Phase B (first enterprise pilot) |
| **Team Size** | 3 backend engineers (Member Services team) |
| **Risk Level** | Medium |
| **Regulatory Impact** | High — FHFA oversight, SOX controls apply |

**One-line Summary:** Introduce AI-assisted code generation for Member Services API endpoint changes to reduce PR cycle time by 30% while maintaining zero escaped critical defects and full FHFA/SOX audit compliance.

---

## Business Case

### Problem Statement

**Current Pain Point:**
The Member Services team implements 8–12 API endpoint changes per sprint (new endpoints, modifications to existing member, advance, and collateral endpoints). Each change follows a manual spec-to-PR workflow: an engineer interprets a Jira ticket, writes code, opens a PR, waits for review, addresses comments, and merges. The process is slow because tickets are written at a business level and require significant engineering translation before implementation can begin. Review cycles are long because the first draft often misses edge cases or data-handling requirements specific to the FHFA regulatory environment.

**Evidence:**
- PR cycle time (open to merge): **5 days median** across the last two quarters
- First-pass PR approval rate: **~40%** (most PRs require at least one round of revision)
- Engineering time spent on review comments addressing missing edge cases or incorrect data handling: estimated **30% of total review time**
- Missed test coverage on edge cases (member not found, suspended member, zero-collateral state): flagged in 3 of the last 4 quarterly FHFA compliance reviews

**Who is affected:**
- Member Services engineering team (3 backend engineers + tech lead)
- API consumers: Member Portal, Advance Origination System, Collateral Management System
- Compliance team (audit trail gaps increase their review burden)
- AFC member institutions (slower turnaround on API changes affects their integration timelines)

### Proposed Solution

**What we will build:**
A structured agentic development workflow for Member Services API changes using the FRAME methodology. Engineers write executable specs using the Agent-Ready Spec template; a Claude Code agent implements the endpoint; CI guardrails enforce FHFA data-handling requirements and test coverage thresholds; a human engineer reviews and merges.

**How it addresses the problem:**
- Executable specs pre-resolve ambiguity before implementation begins, reducing review rework on edge cases
- AI-generated first drafts are complete (tests, validation, audit logging) rather than skeleton implementations
- Automated guardrails catch data-handling violations before they reach human review
- Human approval is mandatory for all merges — no autonomous deployment

**Approach:**
The pilot applies the Agentic SDLC Framework across the full Phase 0 → Phase 3 cycle for each API change:
- **Phase 0:** Engineer writes an intake ticket with business requirement
- **Phase 1:** Engineer completes the Agent-Ready Spec template (constraints, acceptance criteria, edge cases, data classification)
- **Phase 2 (condensed):** Architecture review is synchronous for pilot scope (existing service patterns apply)
- **Phase 3:** Claude Code agent implements the endpoint from the spec; engineer reviews the PR

### Expected Value

**Primary Metrics:**

| Metric | Current Baseline | 30-Day Target | Improvement |
|--------|-----------------|---------------|-------------|
| PR cycle time (open to merge) | 5 days median | 3.5 days median | -30% |
| First-pass approval rate | ~40% | >60% | +20 points |
| Escaped critical/high defects per sprint | baseline TBD (target: 0) | 0 | 0 critical/high |
| Test coverage on Member Services API | ~75% | >80% | +5 points |

**Secondary Benefits:**
- Improved spec quality as a by-product: executable specs become reusable documentation
- Audit trail completeness: agent-generated code includes structured audit logging by convention
- Onboarding acceleration: new engineers can follow the spec → implementation workflow without deep codebase history

**Financial Impact:**
- Cost savings: internal engineering time only; no new tooling cost
- Risk reduction: avoiding a single FHFA compliance finding (which triggers remediation cycles) is estimated to save 40–80 engineer-hours per incident

### Risk if Not Done

**Consequences:**
- PR cycle time remains at 5 days; Member Portal team continues to wait 1–2 sprints for API changes to unblock their feature work
- First-pass approval rate stays at ~40%; senior engineer review time is consumed by predictable, preventable comments rather than architectural judgment
- Compliance audit gap on test coverage remains unresolved; risk of FHFA examiner observation in next scheduled review

**Opportunity cost:**
Senior engineers currently spend estimated 6–8 hours per sprint on review comments that address missing edge cases — time that could be applied to architectural improvements to the Core Banking System integration layer.

---

## Scope

### In Scope

**Workflow targeted:**
- New endpoint additions to the Member Services API (GET, POST operations)
- Modifications to existing member, advance, and collateral endpoints
- Associated test creation (unit and integration)
- Audit logging additions required by the spec

**Deliverables:**
- 4–6 completed API changes implemented via the agentic workflow over the 4-week pilot
- Executable spec for each change (stored in the team's internal spec repository)
- CI guardrail configuration: coverage threshold enforcement, data-handling checks
- Pilot retrospective report with metrics vs. baselines

**Boundaries:**
- All code changes are reviewed and merged by a human engineer
- No autonomous deployment; all production releases follow existing change management
- Data scope: confidential (member financials, advance records, collateral) and restricted (advance account numbers) — both classifications are handled under existing security controls

### Out of Scope

**Explicitly excluded:**
- PUT/DELETE operations (higher-risk mutations — reserved for Phase C after pilot validates the workflow)
- External-facing API changes (Member Portal public API) — internal API only for pilot
- Automated deployment or canary rollout decisions
- Changes to the Core Banking System or Collateral Management System directly
- Model fine-tuning or custom AI infrastructure

**Future phases:**
- Expand to PUT/DELETE mutations with additional guardrails (Phase C, Weeks 13–24)
- Extend to Advance Origination System API changes
- Automated spec generation from Jira tickets (Phase D)

---

## Success Criteria

### 30-Day Targets

| Metric | Target | Measurement Method | Owner |
|--------|--------|-------------------|-------|
| PR cycle time | ≤3.5 days median | GitHub API timestamp: PR open → merge | Tech Lead |
| First-pass approval rate | >60% | PR review data: PRs merged without revision request | Tech Lead |
| Escaped critical/high defects | 0 per sprint | Production incident tracker + QA log | Tech Lead |
| Test coverage | >80% on changed files | CI coverage report (pytest-cov) | Engineer |
| Security scan pass | 100% on all pilot PRs | CI pipeline (TruffleHog + Bandit) | Tech Lead |
| Audit trail completeness | 100% on agent-generated endpoints | Log analysis: every endpoint call has a structured log entry | Compliance |

### Success Definition

**Minimum Viable Success:**
PR cycle time reduced by at least 15% (from 5 days to ≤4.25 days median) AND zero escaped critical/high defects AND all pilot PRs pass security scan. If these three conditions are met, the workflow is validated for Phase C expansion.

**Full Success:**
All 30-day targets met. First-pass approval rate exceeds 60%. Engineering team self-reports reduced cognitive load on edge-case discovery. Compliance team validates audit trail completeness without manual intervention.

**Failure Conditions:**
- Any escaped critical defect traced to agent-generated code → immediate pause, root cause analysis
- Any data-handling violation (raw PII in logs, wrong data classification) → immediate pause, security review
- First-pass approval rate falls below 30% (worse than baseline) → workflow review before continuing
- Tech lead or compliance team requests abort → honored without delay

---

## Risk Assessment

### Risk Matrix

| Risk | Likelihood | Impact | Risk Score | Mitigation Strategy | Contingency | Owner |
|------|-----------|--------|------------|---------------------|-------------|-------|
| Agent generates code that leaks member PII into logs | Low | High | Medium | CI guardrail scans for raw member_id/SSN patterns in log statements; code review checklist item | Immediate rollback; security incident process | Tech Lead |
| FHFA examiner concern about AI-generated code in regulated system | Low | High | Medium | Maintain full human review gate; document human accountability in audit trail; brief compliance team before pilot starts | Pause pilot; engage compliance counsel | Compliance Officer |
| Spec quality insufficient (vague acceptance criteria produce wrong implementations) | Medium | Medium | Medium | 30-minute spec review gate before agent runs; use validate-spec.py guardrail script | Engineer rewrites spec; agent reruns | Tech Lead |
| Agent-generated code introduces regression in existing endpoints | Medium | Medium | Medium | Full regression test suite runs on every PR; 80% coverage threshold blocks merge | Revert PR; root cause analysis before next task | Engineer |
| SOX control gap: audit trail for AI-generated changes | Low | High | Medium | Agent provenance logged in every commit message and PR description; audit trail entry generated by evaluate.py | Manual audit log supplement | Compliance Officer |
| Team adoption resistance (engineers prefer manual workflow) | Medium | Low | Low | Voluntary participation; pilot framed as tool augmentation, not replacement; weekly retrospective | Reduce task scope; focus on highest-pain tasks | Tech Lead |

### Risk Categories

**Technical Risks:**
- Regression in existing member/advance/collateral endpoints from agent changes
- CI guardrail false positives blocking valid PRs (accept some noise during calibration)

**Process Risks:**
- Spec writing takes longer than implementation (net-negative if spec overhead exceeds review savings)
- Inconsistent spec quality between engineers produces inconsistent agent output

**Organizational Risks:**
- Compliance team unfamiliar with agent-generated code review expectations
- Perception that AI authorship reduces accountability for defects

**Compliance Risks:**
- FHFA Model Risk Management guidelines may require documentation of AI tool usage in regulated workflows
- SOX IT General Controls audit may flag AI-generated code without documented human oversight evidence

---

## Compliance & Security

### Data Classification

**Data types involved:**
- [x] Restricted (advance account numbers) — present in advance endpoints; handled under existing controls; never logged in plaintext
- [x] Confidential (member financials, advance balances, collateral valuations) — primary data type; requires audit logging and encryption
- [ ] Internal (business data) — not in scope for this pilot
- [ ] Public — not applicable

**Data handling:**
- Source: PostgreSQL member database (internal network, VPN-gated)
- Processing: Read-only for GET endpoints; write-validated for POST endpoints (human-reviewed before merge)
- Storage: No new data stores introduced by pilot; existing PostgreSQL + audit log (Splunk)
- Retention: Audit log entries retained per existing policy (7 years for SOX-relevant events)
- PII masking: All log statements must use SHA-256 hash of member_id, never raw value; advance account numbers masked with last-4 only in debug logs

### Regulatory Impact

**Applicable regulations:**
- **FHFA Safety and Soundness standards** — Member Services API is a core operational system; changes require documented testing and human approval
- **SOX IT General Controls** — Change management process requires documented review and approval for production code changes; agent-generated PRs must satisfy the same controls as manually written PRs
- **FHFA Model Risk Management** — AI code generation may be subject to model risk documentation requirements; compliance team to assess before pilot start

**Compliance requirements:**
- Human engineer must review and approve every PR before merge (no autonomous merge)
- Every production-bound commit must include a change ticket reference and human approver identity
- Audit trail entry must be generated for each agent implementation run (actor=api-agent, action, result, timestamp)
- Compliance Officer must sign off on pilot scope before Week 1 kickoff

**Audit trail:**
- What will be logged: every agent implementation run (task ID, spec ID, result, human approver), every PR merge (GitHub audit log + Jira ticket link), every CI scan result
- Retention period: 7 years (aligned to SOX retention schedule)
- Review process: Compliance Officer reviews audit log monthly during pilot; full review at 30-day retrospective

### Security Requirements

**Authentication:**
- Method: OAuth 2.0 with corporate Azure AD (existing)
- MFA required: Yes (existing requirement for all production system access)
- Session management: JWT with 1-hour expiry (existing)

**Authorization:**
- RBAC roles: existing roles apply (Engineer, Tech Lead, Compliance Reviewer)
- Least privilege: Yes — agent runs with read-only access to codebase during analysis; write access scoped to feature branch only
- No new service accounts introduced by pilot

**Data protection:**
- Encryption at rest: AES-256 (existing)
- Encryption in transit: TLS 1.3 (existing)
- PII handling: SHA-256 hash of member_id in all log statements; advance account numbers masked to last-4 in debug; SSNs/TINs never stored in API layer

### Approval Gates

| Gate | Required | Approver | Criteria |
|------|----------|----------|----------|
| Business | Yes | VP Engineering | Business case and scope approved |
| Compliance | Yes | Chief Compliance Officer | Regulatory impact assessed; FHFA notification if required |
| Technical | Yes | Tech Lead, Member Services | Architecture consistent with existing service patterns |
| Security | Yes | Information Security Officer | Data handling rules validated; no new attack surface |
| Operations | Yes | Platform Engineering Lead | CI changes reviewed; rollback plan documented |

---

## Team & Resources

### Team Structure

| Role | Name | Time Commitment | Responsibilities |
|------|------|-----------------|------------------|
| Executive Sponsor | VP Engineering | 2 hrs/week | Remove blockers; brief leadership on progress |
| Technical Lead | Member Services Tech Lead | 50% | Spec review gate; PR approval; pilot metrics tracking |
| Engineer 1 | Backend Engineer (Member Services) | 80% | Primary implementer; spec writing; agent operation |
| Engineer 2 | Backend Engineer (Member Services) | 50% | Secondary implementer; peer review of agent PRs |
| Engineer 3 | Backend Engineer (Member Services) | 30% | Spot coverage; edge-case validation |
| Compliance Reviewer | Compliance Officer | 4 hrs/week | Audit trail review; FHFA documentation |
| Security Reviewer | Information Security | 2 hrs/week | Security scan review; PII handling spot checks |

### Skills Required

**Technical:**
- Python 3.11+, FastAPI (existing team proficiency)
- PostgreSQL, SQLAlchemy ORM (existing)
- GitHub Actions CI/CD (existing)
- Prompt engineering for executable spec writing (training required — see below)

**Domain:**
- advance eligibility and collateral rules
- FHFA data classification requirements
- SOX change management documentation standards

### Training Needs

| Training | Audience | Duration | Before Date |
|----------|----------|----------|-------------|
| Agentic SDLC Framework overview + FRAME methodology | Full team | 3 hours | 2026-05-30 |
| Agent-Ready Spec writing workshop (hands-on) | Engineers 1, 2, 3 | 2 hours | 2026-05-30 |
| Security guardrails: PII handling and data classification | Full team | 1.5 hours | 2026-05-30 |
| Compliance: SOX audit trail requirements for AI-assisted changes | Tech Lead + Compliance Officer | 1 hour | 2026-05-30 |

### Tools & Infrastructure

**Required (all existing, no new procurement):**
- GitHub Enterprise (code hosting, PR workflow, GitHub Actions CI)
- Claude Code (AI agent — engineer desktop license)
- Splunk (audit log aggregation)
- PostgreSQL 15 (existing database)
- pytest + pytest-cov (test runner and coverage)

**To be configured for pilot:**
- CI coverage threshold job: enforce >80% coverage on changed files (new GitHub Actions step)
- TruffleHog secret scan on PR diffs (already in repo CI; verify it catches PII patterns)
- Bandit SAST scan on Python files changed in PR (new GitHub Actions step)
- validate-spec.py guardrail run on spec files before agent is invoked

---

## Timeline

### Phase Breakdown

| Week | Phase | Activities | Deliverables | Success Criteria |
|------|-------|------------|--------------|------------------|
| 1 | Setup & Training | Framework training; CI guardrail configuration; compliance sign-off; select 2 pilot tasks | Team trained; CI gates active; compliance approved; first spec drafted | Training complete; all approval gates signed |
| 2 | First Implementation Cycle | Engineer 1 writes spec for Task A; agent implements; tech lead reviews PR; measure cycle time | Merged PR for Task A; first cycle time measurement | PR merged; all CI gates pass; cycle time recorded |
| 3 | Second Implementation Cycle + Calibration | Engineer 2 runs Task B; retrospective on Week 2 learnings; spec template refinements | Merged PR for Task B; refined spec template | PR merged; first-pass rate calculated; retrospective notes |
| 4 | Full Coverage + Evaluation | Engineers 1–3 run Tasks C–F; golden task set evaluation; generate 30-day report | 4–6 total merged PRs; golden task set results; pilot retrospective report | All 30-day targets measured; go/no-go for Phase C |

### Milestones

| Milestone | Target Date | Definition | Owner |
|-----------|-------------|------------|-------|
| Compliance Sign-Off | 2026-05-30 | Chief Compliance Officer approves pilot scope | Compliance Officer |
| Kickoff | 2026-06-02 | Team assembled, training complete, CI configured | Tech Lead |
| First PR Merged via Agentic Workflow | 2026-06-12 | Task A complete, cycle time recorded | Engineer 1 |
| Mid-Point Retrospective | 2026-06-19 | Week 2 learnings documented, spec template updated | Tech Lead |
| Pilot Complete | 2026-06-30 | All pilot tasks complete, all metrics recorded | Tech Lead |
| 30-Day Review | 2026-06-30 | Retrospective report delivered to VP Engineering | Tech Lead + Compliance |

### Dependencies

| Dependency | Required By | Status | Owner |
|------------|-------------|--------|-------|
| Compliance Officer review of FHFA Model Risk implications | 2026-05-28 | Pending | Compliance Officer |
| Information Security sign-off on Claude Code data handling | 2026-05-28 | Pending | Information Security |
| CI guardrail jobs (coverage threshold, Bandit) added to repo | 2026-05-30 | Not started | Engineer 1 |
| Golden task set calibration run (establish baseline pass rates) | 2026-06-06 | Not started | Tech Lead |

### Critical Path

```
Compliance sign-off (2026-05-30)
        ↓
Kickoff + Training (2026-06-02)
        ↓
CI guardrails active (2026-06-02)
        ↓
First spec approved (2026-06-05) → Agent implementation → PR review → Merge (2026-06-12)
        ↓
Mid-point retrospective (2026-06-19)
        ↓
30-day evaluation (2026-06-30)
```

---

## Rollback Plan

### Trigger Conditions

**Automatic triggers (pause pilot immediately):**
- Any escaped critical or high defect traced to agent-generated code
- Any PII data-handling violation (raw member_id or advance account number in logs)
- Any CI security scan failure that reaches production

**Manual triggers:**
- Compliance Officer or Information Security Officer requests pause
- Tech Lead judgment: agent output quality is consistently insufficient
- VP Engineering decision based on mid-point review

### Rollback Procedure

**Before Rollback:**
1. [ ] Confirm trigger condition met and document in incident ticket
2. [ ] Notify team in #member-services-pilot Slack channel
3. [ ] Notify VP Engineering and Compliance Officer
4. [ ] Freeze all in-flight agent PRs (do not merge)

**Rollback Steps:**
1. Close all open agent-generated PRs without merging
2. Revert any merged PRs from the pilot period if the trigger is a production defect (use standard Git revert workflow)
3. Restore previous CI configuration if guardrail changes introduced noise
4. Run full regression test suite on main branch to confirm stability

**Post-Rollback:**
1. [ ] Verify all production endpoints functioning normally
2. [ ] Document root cause in incident report
3. [ ] Schedule post-mortem with full team within 48 hours
4. [ ] Update pilot proposal with lessons learned before any restart decision

**Rollback SLA:**
- Detection to decision: 2 hours (business hours) / 4 hours (off-hours)
- Decision to completion: 4 hours
- Total rollback time: ≤6 hours business hours

---

## Budget

### Resource Costs

| Category | Item | Cost | Period | Total |
|----------|------|------|--------|-------|
| Personnel | Engineer 1 (80% for 4 weeks) | Internal | 4 weeks | Internal allocation |
| Personnel | Engineer 2 (50% for 4 weeks) | Internal | 4 weeks | Internal allocation |
| Personnel | Engineer 3 (30% for 4 weeks) | Internal | 4 weeks | Internal allocation |
| Personnel | Tech Lead (50% for 4 weeks) | Internal | 4 weeks | Internal allocation |
| Personnel | Compliance Officer (4 hrs/week) | Internal | 4 weeks | Internal allocation |
| Tools | Claude Code (existing desktop license) | $0 incremental | — | $0 |
| Infrastructure | GitHub Actions CI minutes (incremental) | ~$0 | 4 weeks | Negligible |
| **Total incremental cost** | | | | **$0 new spend** |

### Expected ROI

**Costs:** Internal engineering time only (estimated 0.5 FTE-equivalent for 4 weeks)
**Benefits if 30% cycle time reduction holds at scale:** ~1.5 engineer-weeks recovered per sprint across the team
**Payback period:** Approximately 3 sprints post-pilot if targets are met

---

## Communication Plan

### Stakeholders

| Stakeholder | Interest | Communication | Frequency |
|-------------|----------|--------------|-----------|
| VP Engineering | High | Weekly status email + mid-point briefing | Weekly |
| Chief Compliance Officer | High | Compliance checkpoint at start + end; ad-hoc if issues arise | Bi-weekly |
| Information Security Officer | Medium | Security review at Week 1; scan results weekly | Weekly |
| Member Services Engineering Team | High | Daily standups; weekly retrospective | Daily |
| Advance Origination System Team | Low | Notification if pilot PRs touch shared interfaces | Per event |

### Reporting

**Weekly Status (every Friday):**
- Format: Email to VP Engineering + Compliance Officer
- Content: PRs completed, cycle time running average, first-pass rate, blockers, risks

**Mid-Point Review (end of Week 2):**
- Format: 45-minute meeting + written summary
- Audience: Full pilot team + VP Engineering + Compliance Officer
- Content: Metrics vs. targets, spec quality findings, go/no-go to continue

**Final Report (end of Week 4):**
- Format: Written retrospective report + 30-minute presentation
- Audience: VP Engineering, Compliance Officer, Member Services leadership
- Content: Full metrics, lessons learned, recommendation for Phase C

---

## Success Criteria Checklist

### Go/No-Go Decision

**Ready to proceed:**
- [ ] Business case approved by VP Engineering
- [ ] Compliance Officer sign-off on scope and FHFA risk assessment
- [ ] Information Security sign-off on Claude Code data handling
- [ ] CI guardrails configured and tested (coverage threshold, Bandit, TruffleHog)
- [ ] Team training complete (FRAME methodology + spec writing)
- [ ] Golden task set baseline run completed (establishes pre-pilot pass rate)

**Approval Required:**
- [ ] VP Engineering (business + budget)
- [ ] Chief Compliance Officer (regulatory)
- [ ] Information Security Officer (security)
- [ ] Tech Lead, Member Services (technical architecture)

---

## Appendix

### Related Documents

- [Agent-Ready Spec Template](../../templates/agent-ready-spec.md)
- [FRAME Framework Overview](../../docs/framework-overview.md)
- [Security Guardrails Guide](../../docs/security-guardrails.md)
- [Example Spec: Add advance-eligibility endpoint](./agent-ready-spec.md)
- [Golden Task Set](../../tools/golden-task-set/)

### References

- FHFA Advisory Bulletin on Model Risk Management (AB 2013-07)
- SOX IT General Controls: Change Management requirements
- NIST AI Risk Management Framework (NIST AI 100-1)
- Agentic SDLC Framework documentation (this repository)

### Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-05-15 | J. Knox | Initial draft |

---

## Approvals

### Business Approval

**Approved By:** _________________________
**Title:** VP Engineering, Apex Financial Corp
**Date:** _________________________
**Signature:** _________________________

**Conditions:** Pilot scope limited to internal Member Services API; no autonomous production deployment.

### Technical Approval

**Approved By:** _________________________
**Title:** Tech Lead, Member Services
**Date:** _________________________
**Signature:** _________________________

**Conditions:** All PRs require tech lead approval before merge; CI guardrails must be active for all pilot PRs.

### Security Approval

**Approved By:** _________________________
**Title:** Information Security Officer, Apex Financial Corp
**Date:** _________________________
**Signature:** _________________________

**Conditions:** Claude Code data handling reviewed and approved; PII masking requirements enforced in CI.

### Compliance Approval

**Approved By:** _________________________
**Title:** Chief Compliance Officer, Apex Financial Corp
**Date:** _________________________
**Signature:** _________________________

**Conditions:** FHFA Model Risk documentation completed before pilot start; human approval gate maintained for all production changes.

---

**Proposal Prepared By:** J. Knox, Member Services Engineering
**Preparation Date:** 2026-05-15
**Version:** 0.1
**Status:** Draft
