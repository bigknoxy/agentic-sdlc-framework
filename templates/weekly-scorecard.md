# Weekly Evaluation Scorecard

**Week of:** [Date - YYYY-MM-DD]
**Team:** [Team Name]
**Workflow:** [Workflow/Project Name]
**Framework Phase:** [Phase A/B/C/D]

---

## Executive Summary

| Metric | Target | Actual | Trend | Status |
|--------|--------|--------|-------|--------|
| Task Success Rate | >80% | ___% | ↑↓→ | 🟢🟡🔴 |
| Review Rework Rate | <30% | ___% | ↑↓→ | 🟢🟡🔴 |
| Escaped Defects | <3% | ___% | ↑↓→ | 🟢🟡🔴 |
| Median Time-to-Merge | <2 days | ___ | ↑↓→ | 🟢🟡🔴 |

**Overall Assessment:** [One sentence summary]

---

## 1. Task Success Rate (Golden Set)

### Definition
Percentage of tasks in the "golden set" (representative tasks) that agents complete successfully on first attempt.

### Results

| Task ID | Task Name | Expected Result | Actual Result | Status | Notes |
|---------|-----------|-----------------|---------------|--------|-------|
| GS-001 | [Task name] | [Expected] | [Actual] | ✅/❌ | [Notes] |
| GS-002 | [Task name] | [Expected] | [Actual] | ✅/❌ | [Notes] |
| GS-003 | [Task name] | [Expected] | [Actual] | ✅/❌ | [Notes] |
| GS-004 | [Task name] | [Expected] | [Actual] | ✅/❌ | [Notes] |
| GS-005 | [Task name] | [Expected] | [Actual] | ✅/❌ | [Notes] |

**Calculation:**
- Total tasks: [Count]
- Successful: [Count]
- Failed: [Count]
- **Success rate:** [Percent]

### Analysis

**What worked well:**
- [Observation 1]
- [Observation 2]

**What didn't work:**
- [Observation 1]
- [Observation 2]

**Root causes of failures:**
| Failure | Root Cause | Fix Required |
|---------|-----------|--------------|
| [Task X] | [Why it failed] | [Action] |

---

## 2. Review Rework Rate

### Definition
Percentage of pull requests that require revision after initial submission (first-pass approval rate inverse).

### Results

| PR | Agent | First Pass | Rework Required | Rounds | Reason |
|----|-------|------------|-----------------|--------|--------|
| #123 | [Agent] | ✅/❌ | [What changed] | [Count] | [Why] |
| #124 | [Agent] | ✅/❌ | [What changed] | [Count] | [Why] |

**Calculation:**
- Total PRs: [Count]
- First-pass approved: [Count]
- Required rework: [Count]
- **Rework rate:** [Percent]

### Analysis

**Common rework reasons:**

| Reason | Count | Percentage | Trend |
|--------|-------|------------|-------|
| Spec unclear | [Count] | [Percent] | ↑↓→ |
| Edge case missed | [Count] | [Percent] | ↑↓→ |
| Security issue | [Count] | [Percent] | ↑↓→ |
| Style/quality | [Count] | [Percent] | ↑↓→ |
| Architecture drift | [Count] | [Percent] | ↑↓→ |

**Specs that produced clean first drafts:**
- [Spec 1] - [Why it worked]
- [Spec 2] - [Why it worked]

**Specs that needed significant rework:**
- [Spec 3] - [Root cause]
- [Spec 4] - [Root cause]

---

## 3. Escaped Defects

### Definition
Percentage of defects found in production that should have been caught earlier.

### Results

| Defect ID | Severity | Found In | Should Have Been Caught | Root Cause |
|-----------|----------|----------|------------------------|------------|
| BUG-001 | Critical/High/Med/Low | Production | [Stage] | [Why] |
| BUG-002 | Critical/High/Med/Low | Staging | [Stage] | [Why] |

**Calculation:**
- Total defects found: [Count]
- Production defects: [Count]
- **Escape rate:** [Percent]

### Analysis

**Defects by stage where they should have been caught:**

| Stage | Count | Percentage |
|-------|-------|------------|
| Unit testing | [Count] | [Percent] |
| Integration testing | [Count] | [Percent] |
| Code review | [Count] | [Percent] |
| Security scan | [Count] | [Percent] |
| Spec review | [Count] | [Percent] |

**Actions to prevent recurrence:**
- [Action 1]
- [Action 2]

---

## 4. Median Time-to-Merge

### Definition
Time from PR creation to merge (for PRs that pass).

### Results

| PR | Created | Merged | Duration | Status |
|----|---------|--------|----------|--------|
| #123 | [Date] | [Date] | [Duration] | ✅ |
| #124 | [Date] | [Date] | [Duration] | ✅ |

**Calculation:**
- Total PRs: [Count]
- Median time: [Duration]
- Mean time: [Duration]
- 90th percentile: [Duration]

### Analysis

**Time breakdown:**

| Phase | Median Time | Percentage |
|-------|-------------|------------|
| Waiting for review | [Duration] | [Percent] |
| In review | [Duration] | [Percent] |
| Rework | [Duration] | [Percent] |
| CI/CD | [Duration] | [Percent] |

**Bottlenecks identified:**
- [Bottleneck 1]
- [Bottleneck 2]

---

## 5. Additional Metrics

### Agent Performance

| Agent | Tasks Completed | Success Rate | Avg Time | Quality Score |
|-------|-----------------|--------------|----------|---------------|
| [Agent 1] | [Count] | [Percent] | [Duration] | [Score] |
| [Agent 2] | [Count] | [Percent] | [Duration] | [Score] |

### Security Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Security scan pass rate | [Percent] | 100% | 🟢🟡🔴 |
| Vulnerabilities introduced | [Count] | 0 | 🟢🟡🔴 |
| Secrets committed | [Count] | 0 | 🟢🟡🔴 |

### Compliance Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Audit trail completeness | [Percent] | 100% | 🟢🟡🔴 |
| Data classification accuracy | [Percent] | 100% | 🟢🟡🔴 |
| Approval gate compliance | [Percent] | 100% | 🟢🟡🔴 |

---

## 6. Qualitative Assessment

### What Worked Well This Week

1. [Success 1 - with evidence]
2. [Success 2 - with evidence]
3. [Success 3 - with evidence]

### What Didn't Work

1. [Problem 1 - with evidence]
2. [Problem 2 - with evidence]

### Learnings & Insights

**Technical:**
- [Learning 1]
- [Learning 2]

**Process:**
- [Learning 1]
- [Learning 2]

**Tooling:**
- [Learning 1]
- [Learning 2]

---

## 7. FRAME Framework Health

### Focus
- **Current workflow:** [Name]
- **Business value delivered:** [Evidence]
- **Executive confidence:** [High/Med/Low]

### Requirements
- **Spec quality trend:** [Improving/Stable/Declining]
- **Executable spec compliance:** [Percent]
- **Common spec issues:** [List]

### Automation Guardrails
- **Guardrail effectiveness:** [High/Med/Low]
- **False positive rate:** [Percent]
- **Coverage gaps:** [List]

### Multi-Agent Coordination
- **Handoff success rate:** [Percent]
- **Context drift incidents:** [Count]
- **Packet quality:** [Score]

### Evaluation Cadence
- **Review consistency:** [Yes/No]
- **Action item completion:** [Percent]
- **Framework adherence:** [Percent]

---

## 8. Actions This Week

### Immediate Actions (This Week)

| Action | Owner | Priority | Due Date | Status |
|--------|-------|----------|----------|--------|
| [Action 1] | [Name] | P0 | [Date] | ⬜ |
| [Action 2] | [Name] | P1 | [Date] | ⬜ |
| [Action 3] | [Name] | P1 | [Date] | ⬜ |

### Process Improvements

| Improvement | Expected Impact | Effort | Priority |
|-------------|-----------------|--------|----------|
| [Improvement 1] | [Impact] | High/Med/Low | P0/P1/P2 |
| [Improvement 2] | [Impact] | High/Med/Low | P0/P1/P2 |

### Spec Template Updates

| Change | Reason | Priority |
|--------|--------|----------|
| [Change 1] | [Why] | P0/P1/P2 |

---

## 9. Golden Task Set Review

### Current Tasks

| ID | Task | Last Run | Status | Keep/Remove/Update |
|----|------|----------|--------|-------------------|
| GS-001 | [Task] | [Date] | ✅/❌ | [Decision] |
| GS-002 | [Task] | [Date] | ✅/❌ | [Decision] |

### Proposed Additions

| Task | Rationale | Priority |
|------|-----------|----------|
| [New task] | [Why add] | P0/P1/P2 |

### Proposed Removals

| Task | Rationale |
|------|-----------|
| [Old task] | [Why remove] |

---

## 10. Risk Register Update

| Risk | Likelihood | Impact | Status | Mitigation | Owner |
|------|-----------|--------|--------|------------|-------|
| [Risk 1] | High/Med/Low | High/Med/Low | Active/Mitigated/Closed | [Strategy] | [Name] |
| [Risk 2] | High/Med/Low | High/Med/Low | Active/Mitigated/Closed | [Strategy] | [Name] |

---

## 11. Next Week Preview

### Planned Work

| Milestone | Target Completion | Confidence |
|-----------|------------------|------------|
| [Milestone 1] | [Date] | High/Med/Low |
| [Milestone 2] | [Date] | High/Med/Low |

### Expected Challenges

- [Challenge 1]
- [Challenge 2]

### Resources Needed

- [Resource 1]
- [Resource 2]

---

## Appendix

### Raw Data

- [Link to full metrics export]
- [Link to agent logs]
- [Link to CI/CD reports]

### Meeting Notes

- [Link to weekly review meeting notes]

### Related Documents

- [Link to spec]
- [Link to ADR]
- [Link to runbook]

---

**Scorecard Prepared By:** [Name]
**Preparation Date:** YYYY-MM-DD
**Reviewed By:** [Name]
**Review Date:** YYYY-MM-DD
**Next Review:** YYYY-MM-DD

**Distribution:** [List who receives this]
