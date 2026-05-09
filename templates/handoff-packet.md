---
packet_id: HANDOFF-[planner|executor]-###
milestone: [Number/Name]
date: YYYY-MM-DD
agent: [Agent ID - e.g., "claude-code-001"]
supervisor: [Human owner - e.g., "josh@apexfinancial.example.com"]
workflow: [Name of workflow/project]
---

# Handoff Packet: [Milestone Name]

> **Purpose:** This document captures the complete state of work at a milestone boundary, enabling seamless handoff between agents and maintaining audit trail.

## Milestone Summary

### Objective
[What this milestone was intended to accomplish - one sentence]

### Status
- [ ] ✅ Completed successfully
- [ ] ⚠️ Completed with issues
- [ ] ❌ Blocked/Incomplete

### Completion Criteria
| Criterion | Status | Evidence |
|-----------|--------|----------|
| [Criterion 1] | ✅/❌ | [Link/commit] |
| [Criterion 2] | ✅/❌ | [Link/commit] |
| [Criterion 3] | ✅/❌ | [Link/commit] |

## Work Completed

### Files Created

| File | Purpose | Lines | Tests |
|------|---------|-------|-------|
| `path/to/file.py` | [Description] | [Count] | [Coverage] |
| `path/to/file2.py` | [Description] | [Count] | [Coverage] |

### Files Modified

| File | Changes | Reason |
|------|---------|--------|
| `path/to/existing.py` | [Summary] | [Why] |
| `path/to/config.yaml` | [Summary] | [Why] |

### Files Deleted

| File | Reason |
|------|--------|
| `path/to/old.py` | [Why deleted] |

## Test Results

### Unit Tests

| Test Suite | Tests | Passed | Failed | Skipped | Coverage |
|------------|-------|--------|--------|---------|----------|
| `tests/unit/test_*.py` | [Count] | [Count] | [Count] | [Count] | [Percent] |

### Integration Tests

| Test Suite | Tests | Passed | Failed | Status |
|------------|-------|--------|--------|--------|
| `tests/integration/test_*.py` | [Count] | [Count] | [Count] | ✅/❌ |

### E2E Tests

| Test Suite | Tests | Passed | Failed | Status |
|------------|-------|--------|--------|--------|
| `tests/e2e/test_*.py` | [Count] | [Count] | [Count] | ✅/❌ |

### Failed Tests

| Test | Error | Action Required |
|------|-------|-----------------|
| `test_name` | [Error message] | [Fix needed] |

## Security Scan Results

### Secret Scanning

| Tool | Status | Findings |
|------|--------|----------|
| TruffleHog | ✅/❌ | [Count] secrets found |
| GitLeaks | ✅/❌ | [Count] secrets found |

**Findings:**
- [ ] No secrets found
- [ ] Secrets found and resolved
- [ ] False positives whitelisted

### Static Analysis (SAST)

| Tool | Status | Issues | Critical | High | Medium | Low |
|------|--------|--------|----------|------|--------|-----|
| Bandit | ✅/❌ | [Total] | [Count] | [Count] | [Count] | [Count] |
| Semgrep | ✅/❌ | [Total] | [Count] | [Count] | [Count] | [Count] |

**Critical/High Issues:**
| Issue | File | Line | Severity | Action |
|-------|------|------|----------|--------|
| [Description] | `file.py` | [Num] | Critical | [Fix/Defer] |

### Dependency Scanning (SCA)

| Tool | Status | Vulnerabilities | Critical | High |
|------|--------|-----------------|----------|------|
| Safety | ✅/❌ | [Count] | [Count] | [Count] |
| Snyk | ✅/❌ | [Count] | [Count] | [Count] |

**Vulnerable Dependencies:**
| Package | Current | Fixed In | Severity | Action |
|---------|---------|----------|----------|--------|
| [package] | [version] | [version] | [Severity] | [Update/Defer] |

### Compliance Checks

| Check | Status | Notes |
|-------|--------|-------|
| Data classification validated | ✅/❌ | [Notes] |
| Audit logging implemented | ✅/❌ | [Notes] |
| Access controls verified | ✅/❌ | [Notes] |

## Code Quality Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Test coverage | [Percent] | >80% | ✅/❌ |
| Code duplication | [Percent] | <5% | ✅/❌ |
| Cyclomatic complexity (avg) | [Value] | <10 | ✅/❌ |
| Documentation coverage | [Percent] | >90% | ✅/❌ |

## Open Risks & Issues

### Blockers

| Issue | Impact | Owner | ETA | Mitigation |
|-------|--------|-------|-----|------------|
| [Blocker 1] | [Description] | [Name] | [Date] | [Strategy] |

### Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|------|-----------|--------|------------|-------|
| [Risk 1] | High/Med/Low | High/Med/Low | [Strategy] | [Name] |

### Technical Debt

| Item | Impact | Priority | Plan |
|------|--------|----------|------|
| [Debt 1] | [Description] | P0/P1/P2 | [When to address] |

## Unresolved Questions

| Question | Context | Suggested Answer | Needs Input From |
|----------|---------|------------------|------------------|
| [Question 1] | [Background] | [Suggestion] | [Role/Name] |
| [Question 2] | [Background] | [Suggestion] | [Role/Name] |

## Next Steps

### Immediate (Next Milestone)

1. [Step 1 - clear action item]
2. [Step 2 - clear action item]
3. [Step 3 - clear action item]

### Upcoming

- [Future milestone 1]
- [Future milestone 2]

## Next Prompt Seed

```
[Context for the next agent to continue work]

Current state:
- [What was just completed]
- [Current architecture/design]
- [Known issues to watch for]

Next milestone:
- [What needs to be done next]
- [Key constraints to respect]
- [Success criteria]

Reference:
- [Important files]
- [Key decisions]
- [Open questions]
```

## Audit Trail Entry

### This Milestone

| Field | Value |
|-------|-------|
| **Action** | [milestone.completed / milestone.blocked / milestone.partial] |
| **Actor** | [Agent ID] |
| **Actor Type** | system |
| **Supervisor** | [Human name] |
| **Timestamp** | YYYY-MM-DDTHH:MM:SSZ |
| **Correlation ID** | [UUID] |
| **Resource** | [Project/Workflow name] |
| **Result** | success/partial/failure |
| **Duration** | [Minutes] |

### Changes Summary

```json
{
  "milestone": "[Name]",
  "status": "completed|blocked|partial",
  "files_changed": {
    "created": ["list"],
    "modified": ["list"],
    "deleted": ["list"]
  },
  "tests": {
    "total": [count],
    "passed": [count],
    "failed": [count]
  },
  "security": {
    "secrets_found": [count],
    "vulnerabilities": {
      "critical": [count],
      "high": [count]
    }
  },
  "coverage": [percent],
  "blockers": ["list"],
  "risks": ["list"]
}
```

## Attachments

- [Link to full test logs]
- [Link to security scan report]
- [Link to architecture diagram]
- [Link to related specs]

---

**Packet Generated:** YYYY-MM-DD HH:MM:SS
**Generated By:** [Agent ID]
**Reviewed By:** [Supervisor name]
**Next Milestone:** [Name]
**Estimated Remaining Work:** [Hours/Points]
