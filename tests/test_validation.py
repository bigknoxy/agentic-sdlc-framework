"""Tests for core/validation.py."""

import pytest
from pathlib import Path

from agentic_sdlc.core.validation import (
    validate_spec_frontmatter,
    validate_spec_sections,
    validate_spec_acceptance_criteria,
    validate_spec_constraints,
    validate_spec,
    validate_spec_directory,
    validate_handoff_frontmatter,
    validate_handoff_sections,
    validate_handoff_milestone_status,
    validate_handoff_security_scans,
    validate_handoff_test_results,
    validate_handoff_next_steps,
    validate_handoff_prompt_seed,
    validate_handoff_audit_trail,
    validate_handoff,
    validate_handoff_directory,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

MINIMAL_VALID_SPEC = """\
---
spec_id: SPEC-2025-01-15-001
title: Test Feature
status: draft
priority: p1
estimated_effort: 8h
template_version: 1.0.0
---

# Agent-Ready Specification

## 1. Context (Business Problem)

Some context here.

## 2. Goal State (Definition of Done)

Goals here.

## 3. Non-Negotiable Constraints

### Security Constraints

**Data Classification:**
- [ ] Restricted
- [x] Internal

**Approval Gates:**
- [ ] Business stakeholder approval required

## 4. Acceptance Criteria (Executable Tests)

Given [some precondition]
When [some action]
Then [some result]

```gherkin
Scenario: basic test
Given a user exists
When they log in
Then they see the dashboard
```

## 5. Edge Cases & Error Handling

Edge cases here.

## 6. Rollback Conditions

Rollback info here.

## 7. Data Classification & Handling

Data handling here.

## 8. Audit Trail Requirements

Audit info here.
"""

MINIMAL_VALID_HANDOFF = """\
---
packet_id: HANDOFF-executor-001
milestone: M1
date: 2025-01-15
agent: claude-code
supervisor: human
workflow: test-project
---

# Handoff Packet: M1

## Milestone Summary

### Objective
Completed milestone one.

### Status
- [x] ✅ Completed successfully

### Completion Criteria
| Criterion | Status | Evidence |
|-----------|--------|----------|
| API done | ✅ | commit abc |

## Work Completed

### Files Created

| File | Purpose | Lines | Tests |
|------|---------|-------|-------|
| `src/main.py` | Entry point | 100 | 90% |

### Files Modified

| File | Changes | Reason |
|------|---------|--------|
| `README.md` | Updated | docs |

## Test Results

### Unit Tests

| Test Suite | Tests | Passed | Failed | Skipped | Coverage |
|------------|-------|--------|--------|---------|----------|
| `tests/unit/test_main.py` | 10 | 10 | 0 | 0 | 85% |

## Security Scan Results

### Secret Scanning ✅

| Tool | Status | Findings |
|------|--------|----------|
| TruffleHog | ✅ | 0 secrets found |

### Static Analysis (SAST) ✅

| Tool | Status | Issues | Critical | High | Medium | Low |
|------|--------|--------|----------|------|--------|-----|
| Bandit | ✅ | 0 | 0 | 0 | 0 | 0 |

### Dependency Scanning (SCA) ✅

| Tool | Status | Vulnerabilities | Critical | High |
|------|--------|-----------------|----------|------|
| Safety | ✅ | 0 | 0 | 0 |

## Next Steps

### Immediate

1. [Deploy to staging environment]
2. [Run smoke tests]
3. [Notify stakeholders]

## Next Prompt Seed

```
This is a sufficiently long next prompt seed that provides meaningful context
for the next agent to continue the work. It describes what was completed,
the current architecture, known issues to watch for, and the next milestone
objectives including success criteria and constraints to respect.
```

## Audit Trail Entry

### This Milestone

| Field | Value |
|-------|-------|
| **Action** | milestone.completed |
| **Actor** | claude-code |
| **Actor Type** | system |
| **Supervisor** | human |
| **Timestamp** | 2025-01-15T10:00:00Z |
| **Correlation ID** | 550e8400-e29b-41d4-a716-446655440000 |
| **Resource** | test-project |
| **Result** | success |
| **Duration** | 60 |

### Changes Summary

```json
{
  "milestone": "M1",
  "status": "completed",
  "files_changed": {
    "created": ["src/main.py"],
    "modified": ["README.md"],
    "deleted": []
  },
  "tests": {
    "total": 10,
    "passed": 10,
    "failed": 0
  },
  "security": {
    "secrets_found": 0,
    "vulnerabilities": {
      "critical": 0,
      "high": 0
    }
  },
  "coverage": 85,
  "blockers": [],
  "risks": []
}
```
"""


# ---------------------------------------------------------------------------
# Spec validation tests
# ---------------------------------------------------------------------------

class TestValidateSpecFrontmatter:
    def test_valid_frontmatter(self):
        valid, errors = validate_spec_frontmatter(MINIMAL_VALID_SPEC)
        assert valid
        assert errors == []

    def test_missing_frontmatter(self):
        valid, errors = validate_spec_frontmatter("# No frontmatter here\n")
        assert not valid
        assert any("frontmatter" in e.lower() for e in errors)

    def test_malformed_frontmatter(self):
        valid, errors = validate_spec_frontmatter("---\nno closing\n")
        assert not valid

    def test_missing_required_field(self):
        content = "---\nspec_id: SPEC-001\ntitle: Test\nstatus: draft\n---\n# body"
        valid, errors = validate_spec_frontmatter(content)
        assert not valid
        assert any("priority" in e for e in errors)


class TestValidateSpecSections:
    def test_all_sections_present(self):
        valid, errors = validate_spec_sections(MINIMAL_VALID_SPEC)
        assert valid, errors

    def test_missing_section(self):
        content = MINIMAL_VALID_SPEC.replace("## 5. Edge Cases", "## 5. OTHER")
        valid, errors = validate_spec_sections(content)
        assert not valid
        assert any("Edge Cases" in e for e in errors)


class TestValidateSpecAcceptanceCriteria:
    def test_valid_gherkin(self):
        valid, errors = validate_spec_acceptance_criteria(MINIMAL_VALID_SPEC)
        assert valid, errors

    def test_missing_gherkin(self):
        content = "## 4. Acceptance Criteria\n\nSome acceptance criteria without gherkin"
        valid, errors = validate_spec_acceptance_criteria(content)
        assert not valid


class TestValidateSpecConstraints:
    def test_valid_constraints(self):
        valid, errors = validate_spec_constraints(MINIMAL_VALID_SPEC)
        assert valid, errors

    def test_unchecked_data_classification(self):
        content = (
            "Data Classification\n"
            "- [ ] Restricted\n"
            "- [ ] Internal\n"
        )
        valid, errors = validate_spec_constraints(content)
        assert not valid
        assert any("classification" in e.lower() for e in errors)


class TestValidateSpec:
    def test_valid_spec_file(self, tmp_path):
        spec_file = tmp_path / "SPEC-2025-01-15-001.md"
        spec_file.write_text(MINIMAL_VALID_SPEC)
        valid, errors = validate_spec(spec_file)
        assert valid, errors

    def test_missing_file(self, tmp_path):
        valid, errors = validate_spec(tmp_path / "nonexistent.md")
        assert not valid
        assert any("read" in e.lower() or "found" in e.lower() for e in errors)

    def test_empty_file(self, tmp_path):
        spec_file = tmp_path / "empty.md"
        spec_file.write_text("")
        valid, errors = validate_spec(spec_file)
        assert not valid


class TestValidateSpecDirectory:
    def test_valid_directory(self, tmp_path):
        (tmp_path / "SPEC-001.md").write_text(MINIMAL_VALID_SPEC)
        total, passed, errors = validate_spec_directory(tmp_path)
        assert total == 1
        assert passed == 1
        assert errors == []

    def test_empty_directory(self, tmp_path):
        total, passed, errors = validate_spec_directory(tmp_path)
        assert total == 0
        assert passed == 0

    def test_mixed_results(self, tmp_path):
        (tmp_path / "SPEC-001.md").write_text(MINIMAL_VALID_SPEC)
        (tmp_path / "SPEC-002.md").write_text("# bad spec no frontmatter")
        total, passed, errors = validate_spec_directory(tmp_path)
        assert total == 2
        assert passed == 1
        assert len(errors) > 0


# ---------------------------------------------------------------------------
# Handoff validation tests
# ---------------------------------------------------------------------------

class TestValidateHandoffFrontmatter:
    def test_valid_frontmatter(self):
        valid, errors, meta = validate_handoff_frontmatter(MINIMAL_VALID_HANDOFF)
        assert valid, errors
        assert meta["packet_id"] == "HANDOFF-executor-001"

    def test_missing_frontmatter(self):
        valid, errors, _ = validate_handoff_frontmatter("# No frontmatter")
        assert not valid

    def test_invalid_packet_id_format(self):
        content = MINIMAL_VALID_HANDOFF.replace(
            "packet_id: HANDOFF-executor-001",
            "packet_id: BAD-FORMAT-001"
        )
        valid, errors, _ = validate_handoff_frontmatter(content)
        assert not valid
        assert any("packet_id" in e for e in errors)

    def test_invalid_date_format(self):
        content = MINIMAL_VALID_HANDOFF.replace("date: 2025-01-15", "date: 15/01/2025")
        valid, errors, _ = validate_handoff_frontmatter(content)
        assert not valid


class TestValidateHandoffSections:
    def test_all_sections_present(self):
        valid, errors = validate_handoff_sections(MINIMAL_VALID_HANDOFF)
        assert valid, errors

    def test_missing_section(self):
        content = MINIMAL_VALID_HANDOFF.replace("## Work Completed", "## Something Else")
        valid, errors = validate_handoff_sections(content)
        assert not valid
        assert any("Work Completed" in e for e in errors)


class TestValidateHandoffMilestoneStatus:
    def test_valid_status(self):
        valid, errors = validate_handoff_milestone_status(MINIMAL_VALID_HANDOFF)
        assert valid, errors

    def test_missing_status(self):
        content = MINIMAL_VALID_HANDOFF.replace(
            "- [x] ✅ Completed successfully",
            "No status checkbox here"
        )
        valid, errors = validate_handoff_milestone_status(content)
        assert not valid


class TestValidateHandoffSecurityScans:
    def test_valid_security_scans(self):
        valid, errors = validate_handoff_security_scans(MINIMAL_VALID_HANDOFF)
        assert valid, errors

    def test_missing_security_check(self):
        content = MINIMAL_VALID_HANDOFF.replace("### Secret Scanning ✅", "### Something Else")
        valid, errors = validate_handoff_security_scans(content)
        assert not valid
        assert any("Secret Scanning" in e for e in errors)

    def test_critical_vulnerabilities_fail(self):
        content = MINIMAL_VALID_HANDOFF + "\n| Critical | 2 |\n"
        valid, errors = validate_handoff_security_scans(content)
        assert not valid
        assert any("critical" in e.lower() for e in errors)


class TestValidateHandoffTestResults:
    def test_valid_test_results(self):
        valid, errors = validate_handoff_test_results(MINIMAL_VALID_HANDOFF)
        assert valid, errors

    def test_missing_unit_tests_section(self):
        content = MINIMAL_VALID_HANDOFF.replace("### Unit Tests", "### Integration Tests Only")
        valid, errors = validate_handoff_test_results(content)
        assert not valid

    def test_failed_tests_fail_validation(self):
        content = MINIMAL_VALID_HANDOFF.replace(
            "| Failed | Skipped |",
            "| Failed | Skipped |"
        )
        # Insert a row with failing tests
        content = content + "\n| Failed | 3 |\n"
        valid, errors = validate_handoff_test_results(content)
        assert not valid


class TestValidateHandoffNextSteps:
    def test_valid_next_steps(self):
        valid, errors = validate_handoff_next_steps(MINIMAL_VALID_HANDOFF)
        assert valid, errors

    def test_missing_immediate_section(self):
        content = MINIMAL_VALID_HANDOFF.replace("### Immediate", "### Upcoming")
        valid, errors = validate_handoff_next_steps(content)
        assert not valid


class TestValidateHandoffPromptSeed:
    def test_valid_prompt_seed(self):
        valid, errors = validate_handoff_prompt_seed(MINIMAL_VALID_HANDOFF)
        assert valid, errors

    def test_missing_prompt_seed_section(self):
        content = MINIMAL_VALID_HANDOFF.replace("## Next Prompt Seed", "## Something Else")
        valid, errors = validate_handoff_prompt_seed(content)
        assert not valid

    def test_prompt_seed_too_short(self):
        content = MINIMAL_VALID_HANDOFF.replace(
            "This is a sufficiently long next prompt seed that provides meaningful context\n"
            "for the next agent to continue the work. It describes what was completed,\n"
            "the current architecture, known issues to watch for, and the next milestone\n"
            "objectives including success criteria and constraints to respect.",
            "Too short."
        )
        valid, errors = validate_handoff_prompt_seed(content)
        assert not valid
        assert any("short" in e.lower() for e in errors)


class TestValidateHandoffAuditTrail:
    def test_valid_audit_trail(self):
        valid, errors = validate_handoff_audit_trail(MINIMAL_VALID_HANDOFF)
        assert valid, errors

    def test_missing_audit_section(self):
        content = MINIMAL_VALID_HANDOFF.replace("## Audit Trail Entry", "## Something Else")
        valid, errors = validate_handoff_audit_trail(content)
        assert not valid


class TestValidateHandoff:
    def test_valid_handoff_file(self, tmp_path):
        pf = tmp_path / "HANDOFF-001.md"
        pf.write_text(MINIMAL_VALID_HANDOFF)
        valid, errors = validate_handoff(pf)
        assert valid, errors

    def test_missing_file(self, tmp_path):
        valid, errors = validate_handoff(tmp_path / "nonexistent.md")
        assert not valid

    def test_empty_file(self, tmp_path):
        pf = tmp_path / "HANDOFF-001.md"
        pf.write_text("")
        valid, errors = validate_handoff(pf)
        assert not valid


class TestValidateHandoffDirectory:
    def test_valid_directory(self, tmp_path):
        (tmp_path / "HANDOFF-001.md").write_text(MINIMAL_VALID_HANDOFF)
        total, passed, errors = validate_handoff_directory(tmp_path)
        assert total == 1
        assert passed == 1

    def test_empty_directory(self, tmp_path):
        total, passed, errors = validate_handoff_directory(tmp_path)
        assert total == 0

    def test_mixed_results(self, tmp_path):
        (tmp_path / "HANDOFF-001.md").write_text(MINIMAL_VALID_HANDOFF)
        (tmp_path / "HANDOFF-002.md").write_text("# bad packet")
        total, passed, errors = validate_handoff_directory(tmp_path)
        assert total == 2
        assert passed == 1
        assert len(errors) > 0
