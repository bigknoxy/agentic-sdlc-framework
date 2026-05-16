# Apex Financial Corp Pilot — Example

This directory contains a fully worked example of the Agentic SDLC Framework applied to the Apex Financial Corp's Member Services engineering team. It demonstrates the FRAME methodology in a regulated banking environment where FHFA oversight, SOX controls, and strict data handling requirements are non-negotiable constraints — not afterthoughts.

---

## What This Pilot Is

**Organization:** Apex Financial Corp  
**Workflow targeted:** API endpoint changes in the Member Services API (member data, advance requests, collateral management)  
**Duration:** 30-day pilot (4 weeks)  
**Team:** 3 backend engineers + 1 tech lead  
**Goal:** Reduce PR cycle time from 5 days to 3.5 days while maintaining zero escaped critical defects and full audit compliance

The pilot does not introduce autonomous deployment. Every agent-generated PR requires human review and approval before merge. The agent's role is to produce a correct, test-covered, audit-logged first draft — the engineer's role is to verify and own it.

---

## Files in This Directory

| File | What It Is |
|------|-----------|
| `pilot-proposal.md` | The filled-in pilot proposal: business case, scope, success criteria, risks, compliance sign-offs, and 4-week timeline |
| `agent-ready-spec.md` | A fully worked agent-ready spec for the first pilot task: `GET /members/{member_id}/advance-eligibility` |
| `README.md` | This file |

---

## How It Relates to FRAME

Each artifact maps to a FRAME pillar:

| FRAME Pillar | Artifact / Practice |
|-------------|---------------------|
| **Focus** | Pilot proposal scopes the workflow to one team and one API surface (Member Services API, GET/POST only) |
| **Requirements** | `agent-ready-spec.md` translates a business need into executable Gherkin acceptance criteria, edge cases, and data-handling rules before the agent writes a single line of code |
| **Automation** | Pilot proposal mandates CI guardrails: coverage threshold, Bandit SAST, TruffleHog secret scan, validate-spec.py — all blocking gates |
| **Multi-agent** | The spec defines a planner-executor boundary: tech lead writes/approves the spec (planner role); Claude Code implements from it (executor role); tech lead reviews the PR (reviewer role) |
| **Evaluation** | The golden task set (`tools/golden-task-set/`) provides a weekly measurement baseline; the pilot tracks four metrics (cycle time, first-pass rate, escaped defects, coverage) against defined targets |

---

## What Makes This a Regulated-Industry Example

Standard FRAME examples focus on speed and quality. This pilot adds a compliance layer appropriate for any regulated financial institution:

**Data classification is explicit in every artifact.** The spec identifies which data fields are `confidential` (member financials, advance balances), which are `restricted` (advance account numbers, SSNs), and specifies exact handling rules — SHA-256 hash of member_id in logs, no SELECT * queries, no float arithmetic for monetary values.

**Audit trail is a first-class requirement, not a note.** Section 8 of the agent-ready spec defines the exact JSON structure every log entry must produce, including `actor.human_supervisor` populated from the JWT claim. The compliance team can verify audit completeness against this schema.

**Human approval is architecturally enforced.** The pilot proposal explicitly excludes autonomous deployment. The rollback plan, failure conditions, and compliance approval gates all assume a human is in the loop at every merge boundary.

**Regulatory risk is named.** The pilot proposal names FHFA Model Risk Management and SOX IT General Controls as applicable frameworks and identifies a pre-pilot compliance sign-off as a hard dependency. The pilot does not start until those gates are cleared.

---

## How to Adapt This for Your Organization

**Step 1: Replace the regulatory context.**  
The organization operates under FHFA/SOX. Your organization may operate under HIPAA, PCI-DSS, SOC 2, GDPR, or a different framework. Identify your applicable regulations and update:
- Section 3 (Non-Negotiable Constraints) of the spec template
- The Compliance & Security section of the pilot proposal
- The audit log format in Section 8 to match your SIEM's ingestion schema

**Step 2: Replace the data classification rules.**  
This example uses AFC's four-tier classification (restricted / confidential / internal / public). Map your organization's classification policy to the same tiers, or adjust the tier names to match your internal terminology.

**Step 3: Replace the business metrics.**  
The AFC pilot targets a 30% reduction in PR cycle time from a 5-day baseline. Your baseline will differ. Run a two-sprint measurement cycle before starting the pilot to establish your actual baseline numbers, then set targets relative to that baseline — not against this example's numbers.

**Step 4: Adjust the approval gate structure.**  
This pilot requires sign-offs from VP Engineering, Chief Compliance Officer, Information Security Officer, and Tech Lead before starting. A less-regulated organization may require fewer gates. A more highly regulated one (e.g., a federally chartered bank under OCC supervision) may require additional gates. Match your existing change management process.

**Step 5: Run the golden task set first.**  
Before starting the pilot, run the tasks in `tools/golden-task-set/tasks.yaml` against your codebase (or adapt the tasks to reflect your domain). Establish baseline pass rates. This gives you a pre-pilot measurement point so you can demonstrate improvement at the 30-day mark.

---

## Quick Start Checklist

Before Week 1 of your pilot:

- [ ] Compliance sign-off obtained (whatever your regulatory framework requires)
- [ ] Security review of AI tool data handling complete
- [ ] CI guardrails configured: coverage threshold, secret scan, SAST
- [ ] validate-spec.py runs clean on your spec
- [ ] Team has completed the 3-hour FRAME methodology training
- [ ] Golden task set baseline run complete (pre-pilot pass rate recorded)
- [ ] PR cycle time baseline measured (at least 2 prior sprints of data)
- [ ] First-pass approval rate baseline measured

---

## Related Resources

- [Pilot Proposal Template](../../templates/pilot-proposal.md)
- [Agent-Ready Spec Template](../../templates/agent-ready-spec.md)
- [FRAME Framework Overview](../../docs/framework-overview.md)
- [Security Guardrails Guide](../../docs/security-guardrails.md)
- [Golden Task Set](../../tools/golden-task-set/)
- [Enterprise Pilot Example (Internal Reporting)](../enterprise-pilot-example/) — a lower-regulatory-risk example for comparison
