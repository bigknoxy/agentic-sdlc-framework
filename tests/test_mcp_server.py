"""Tests for tools/mcp-server/server.py.

Strategy
--------
- Import the tool-implementation coroutines directly (_tool_create_spec, etc.)
  and drive them with pytest-asyncio (or plain asyncio.run).
- Mock filesystem operations and template loading where appropriate so tests
  run without side-effects on the developer's working tree.
- Each of the 5 public tools is covered with:
    * valid-input happy path
    * invalid/missing file
    * missing required parameters

The conftest.py at the project root adds tools/mcp-server/ to sys.path so
``import server`` resolves to tools/mcp-server/server.py directly.
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# conftest.py adds tools/mcp-server to sys.path so we can import directly.
import server as server_mod  # noqa: E402

from server import (
    _tool_create_spec,
    _tool_validate_spec,
    _tool_create_handoff,
    _tool_validate_handoff,
    _tool_check_guardrails,
    _resolve,
    _ok,
    _err,
)


def run(coro):
    """Run a coroutine synchronously (Python 3.11+)."""
    return asyncio.run(coro)


def parse(result) -> dict:
    """Parse the JSON payload from an MCP TextContent result list."""
    assert len(result) == 1
    return json.loads(result[0].text)


# ---------------------------------------------------------------------------
# Minimal valid spec/handoff content (mirrors test_validation.py fixtures)
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
  "status": "completed"
}
```
"""


# ---------------------------------------------------------------------------
# Helpers / utilities
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_resolve_relative(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = _resolve("specs/foo.md")
        assert result == tmp_path / "specs" / "foo.md"

    def test_resolve_absolute(self, tmp_path):
        abs_path = str(tmp_path / "foo.md")
        result = _resolve(abs_path)
        assert result == tmp_path / "foo.md"

    def test_ok_returns_json(self):
        result = _ok({"key": "value"})
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data["key"] == "value"

    def test_err_returns_error_key(self):
        result = _err("something went wrong")
        data = json.loads(result[0].text)
        assert "error" in data
        assert "something went wrong" in data["error"]


# ---------------------------------------------------------------------------
# create_spec
# ---------------------------------------------------------------------------

class TestCreateSpec:
    def test_create_spec_valid(self, tmp_path):
        with patch("server.get_spec_template", return_value=MINIMAL_VALID_SPEC):
            result = run(_tool_create_spec({"title": "My Feature", "specs_dir": str(tmp_path / "specs")}))
        data = parse(result)
        assert "spec_id" in data
        assert re.match(r"SPEC-\d{4}-\d{2}-\d{2}-\d{3}", data["spec_id"])
        assert "path" in data
        assert Path(data["path"]).exists()

    def test_create_spec_missing_title(self, tmp_path):
        result = run(_tool_create_spec({}))
        data = parse(result)
        assert "error" in data
        assert "title" in data["error"]

    def test_create_spec_empty_title(self, tmp_path):
        result = run(_tool_create_spec({"title": "  "}))
        data = parse(result)
        assert "error" in data

    def test_create_spec_priority_p0(self, tmp_path):
        with patch("server.get_spec_template", return_value=MINIMAL_VALID_SPEC):
            result = run(_tool_create_spec({
                "title": "Urgent",
                "priority": "p0",
                "specs_dir": str(tmp_path / "specs"),
            }))
        data = parse(result)
        assert data["priority"] == "P0"
        assert "priority: p0" in Path(data["path"]).read_text()

    def test_create_spec_invalid_priority(self, tmp_path):
        result = run(_tool_create_spec({"title": "Test", "priority": "invalid"}))
        data = parse(result)
        assert "error" in data
        assert "priority" in data["error"].lower()

    def test_create_spec_invalid_template(self, tmp_path):
        result = run(_tool_create_spec({"title": "Test", "template": "unknown"}))
        data = parse(result)
        assert "error" in data
        assert "template" in data["error"].lower()

    def test_create_spec_auto_increments(self, tmp_path):
        specs_dir = str(tmp_path / "specs")
        with patch("server.get_spec_template", return_value=MINIMAL_VALID_SPEC):
            r1 = parse(run(_tool_create_spec({"title": "First", "specs_dir": specs_dir})))
            r2 = parse(run(_tool_create_spec({"title": "Second", "specs_dir": specs_dir})))
        assert r1["spec_id"] != r2["spec_id"]
        # Second should have a higher sequence number
        assert r1["spec_id"] < r2["spec_id"]

    def test_create_spec_default_priority_p1(self, tmp_path):
        with patch("server.get_spec_template", return_value=MINIMAL_VALID_SPEC):
            result = run(_tool_create_spec({"title": "Test", "specs_dir": str(tmp_path / "specs")}))
        data = parse(result)
        assert data["priority"] == "P1"

    def test_create_spec_inserts_title(self, tmp_path):
        template = MINIMAL_VALID_SPEC.replace("Test Feature", "[Feature/Workflow Name]")
        with patch("server.get_spec_template", return_value=template):
            result = run(_tool_create_spec({"title": "Auth Service", "specs_dir": str(tmp_path / "specs")}))
        data = parse(result)
        content = Path(data["path"]).read_text()
        assert "Auth Service" in content

    def test_create_spec_template_not_found(self, tmp_path):
        with patch("server.get_spec_template", side_effect=FileNotFoundError("missing")):
            result = run(_tool_create_spec({"title": "Test", "specs_dir": str(tmp_path / "specs")}))
        data = parse(result)
        assert "error" in data
        assert "template" in data["error"].lower()

    def test_create_spec_creates_directory(self, tmp_path):
        new_dir = tmp_path / "new" / "specs"
        with patch("server.get_spec_template", return_value=MINIMAL_VALID_SPEC):
            result = run(_tool_create_spec({"title": "Test", "specs_dir": str(new_dir)}))
        data = parse(result)
        assert new_dir.is_dir()


# ---------------------------------------------------------------------------
# validate_spec
# ---------------------------------------------------------------------------

class TestValidateSpec:
    def test_validate_valid_spec(self, tmp_path):
        spec_file = tmp_path / "SPEC-2025-01-15-001.md"
        spec_file.write_text(MINIMAL_VALID_SPEC)
        result = run(_tool_validate_spec({"path": str(spec_file)}))
        data = parse(result)
        assert data["passed"] is True
        assert data["errors"] == []

    def test_validate_invalid_spec(self, tmp_path):
        spec_file = tmp_path / "bad.md"
        spec_file.write_text("# No frontmatter at all")
        result = run(_tool_validate_spec({"path": str(spec_file)}))
        data = parse(result)
        assert data["passed"] is False
        assert len(data["errors"]) > 0

    def test_validate_missing_file(self, tmp_path):
        result = run(_tool_validate_spec({"path": str(tmp_path / "nonexistent.md")}))
        data = parse(result)
        assert "error" in data
        assert "not found" in data["error"].lower()

    def test_validate_missing_path_param(self):
        result = run(_tool_validate_spec({}))
        data = parse(result)
        assert "error" in data
        assert "path" in data["error"]

    def test_validate_returns_path(self, tmp_path):
        spec_file = tmp_path / "SPEC-2025-01-15-001.md"
        spec_file.write_text(MINIMAL_VALID_SPEC)
        result = run(_tool_validate_spec({"path": str(spec_file)}))
        data = parse(result)
        assert "path" in data
        assert str(spec_file) == data["path"]

    def test_validate_has_warnings_key(self, tmp_path):
        spec_file = tmp_path / "SPEC-2025-01-15-001.md"
        spec_file.write_text(MINIMAL_VALID_SPEC)
        result = run(_tool_validate_spec({"path": str(spec_file)}))
        data = parse(result)
        assert "warnings" in data

    def test_validate_empty_file(self, tmp_path):
        spec_file = tmp_path / "empty.md"
        spec_file.write_text("")
        result = run(_tool_validate_spec({"path": str(spec_file)}))
        data = parse(result)
        assert data["passed"] is False


# ---------------------------------------------------------------------------
# create_handoff
# ---------------------------------------------------------------------------

class TestCreateHandoff:
    def test_create_handoff_valid(self, tmp_path):
        with patch("server.get_handoff_template", return_value=MINIMAL_VALID_HANDOFF):
            result = run(_tool_create_handoff({
                "milestone": "M1",
                "handoffs_dir": str(tmp_path / "handoffs"),
            }))
        data = parse(result)
        assert "packet_id" in data
        assert re.match(r"HANDOFF-(executor|planner)-\d{3}", data["packet_id"])
        assert "path" in data
        assert Path(data["path"]).exists()

    def test_create_handoff_missing_milestone(self):
        result = run(_tool_create_handoff({}))
        data = parse(result)
        assert "error" in data
        assert "milestone" in data["error"]

    def test_create_handoff_empty_milestone(self):
        result = run(_tool_create_handoff({"milestone": "  "}))
        data = parse(result)
        assert "error" in data

    def test_create_handoff_planner_role(self, tmp_path):
        with patch("server.get_handoff_template", return_value=MINIMAL_VALID_HANDOFF):
            result = run(_tool_create_handoff({
                "milestone": "M1",
                "agent": "planner-agent",
                "handoffs_dir": str(tmp_path / "handoffs"),
            }))
        data = parse(result)
        assert "planner" in data["packet_id"]

    def test_create_handoff_executor_role(self, tmp_path):
        with patch("server.get_handoff_template", return_value=MINIMAL_VALID_HANDOFF):
            result = run(_tool_create_handoff({
                "milestone": "M1",
                "agent": "claude-code",
                "handoffs_dir": str(tmp_path / "handoffs"),
            }))
        data = parse(result)
        assert "executor" in data["packet_id"]

    def test_create_handoff_auto_increments(self, tmp_path):
        handoffs_dir = str(tmp_path / "handoffs")
        with patch("server.get_handoff_template", return_value=MINIMAL_VALID_HANDOFF):
            r1 = parse(run(_tool_create_handoff({"milestone": "M1", "handoffs_dir": handoffs_dir})))
            r2 = parse(run(_tool_create_handoff({"milestone": "M2", "handoffs_dir": handoffs_dir})))
        assert r1["path"] != r2["path"]

    def test_create_handoff_default_agent(self, tmp_path):
        with patch("server.get_handoff_template", return_value=MINIMAL_VALID_HANDOFF):
            result = run(_tool_create_handoff({
                "milestone": "M1",
                "handoffs_dir": str(tmp_path / "handoffs"),
            }))
        data = parse(result)
        assert data["agent"] == "claude-code"

    def test_create_handoff_template_not_found(self, tmp_path):
        with patch("server.get_handoff_template", side_effect=FileNotFoundError("missing")):
            result = run(_tool_create_handoff({
                "milestone": "M1",
                "handoffs_dir": str(tmp_path / "handoffs"),
            }))
        data = parse(result)
        assert "error" in data

    def test_create_handoff_creates_directory(self, tmp_path):
        new_dir = tmp_path / "deep" / "handoffs"
        with patch("server.get_handoff_template", return_value=MINIMAL_VALID_HANDOFF):
            result = run(_tool_create_handoff({"milestone": "M1", "handoffs_dir": str(new_dir)}))
        data = parse(result)
        assert new_dir.is_dir()


# ---------------------------------------------------------------------------
# validate_handoff
# ---------------------------------------------------------------------------

class TestValidateHandoff:
    def test_validate_valid_handoff(self, tmp_path):
        packet_file = tmp_path / "HANDOFF-001.md"
        packet_file.write_text(MINIMAL_VALID_HANDOFF)
        result = run(_tool_validate_handoff({"path": str(packet_file)}))
        data = parse(result)
        assert data["passed"] is True
        assert data["errors"] == []

    def test_validate_invalid_handoff(self, tmp_path):
        packet_file = tmp_path / "bad.md"
        packet_file.write_text("# No frontmatter at all")
        result = run(_tool_validate_handoff({"path": str(packet_file)}))
        data = parse(result)
        assert data["passed"] is False
        assert len(data["errors"]) > 0

    def test_validate_missing_file(self, tmp_path):
        result = run(_tool_validate_handoff({"path": str(tmp_path / "ghost.md")}))
        data = parse(result)
        assert "error" in data
        assert "not found" in data["error"].lower()

    def test_validate_missing_path_param(self):
        result = run(_tool_validate_handoff({}))
        data = parse(result)
        assert "error" in data
        assert "path" in data["error"]

    def test_validate_returns_path(self, tmp_path):
        packet_file = tmp_path / "HANDOFF-001.md"
        packet_file.write_text(MINIMAL_VALID_HANDOFF)
        result = run(_tool_validate_handoff({"path": str(packet_file)}))
        data = parse(result)
        assert str(packet_file) == data["path"]

    def test_validate_has_warnings_key(self, tmp_path):
        packet_file = tmp_path / "HANDOFF-001.md"
        packet_file.write_text(MINIMAL_VALID_HANDOFF)
        result = run(_tool_validate_handoff({"path": str(packet_file)}))
        data = parse(result)
        assert "warnings" in data

    def test_validate_empty_file(self, tmp_path):
        packet_file = tmp_path / "HANDOFF-001.md"
        packet_file.write_text("")
        result = run(_tool_validate_handoff({"path": str(packet_file)}))
        data = parse(result)
        assert data["passed"] is False


# ---------------------------------------------------------------------------
# check_guardrails
# ---------------------------------------------------------------------------

class TestCheckGuardrails:
    def test_check_clean_project(self, tmp_path):
        # Empty project directory — no secrets, no specs/handoffs dirs
        result = run(_tool_check_guardrails({"root_dir": str(tmp_path)}))
        data = parse(result)
        assert "secrets" in data
        assert "specs" in data
        assert "handoffs" in data
        assert "overall_passed" in data
        assert data["secrets"]["passed"] is True
        assert data["overall_passed"] is True

    def test_check_with_valid_specs(self, tmp_path):
        specs_dir = tmp_path / "specs"
        specs_dir.mkdir()
        (specs_dir / "SPEC-2025-01-15-001.md").write_text(MINIMAL_VALID_SPEC)

        result = run(_tool_check_guardrails({
            "root_dir": str(tmp_path),
            "specs_dir": str(specs_dir),
            "handoffs_dir": str(tmp_path / "handoffs"),
        }))
        data = parse(result)
        assert data["specs"]["passed"] is True
        assert data["specs"]["total"] == 1
        assert data["specs"]["passed_count"] == 1

    def test_check_with_invalid_specs(self, tmp_path):
        specs_dir = tmp_path / "specs"
        specs_dir.mkdir()
        (specs_dir / "bad.md").write_text("# No frontmatter")

        result = run(_tool_check_guardrails({
            "root_dir": str(tmp_path),
            "specs_dir": str(specs_dir),
        }))
        data = parse(result)
        assert data["specs"]["passed"] is False
        assert data["specs"]["failed_count"] == 1
        assert len(data["specs"]["errors"]) > 0
        assert data["overall_passed"] is False

    def test_check_with_valid_handoffs(self, tmp_path):
        handoffs_dir = tmp_path / "handoffs"
        handoffs_dir.mkdir()
        (handoffs_dir / "HANDOFF-001.md").write_text(MINIMAL_VALID_HANDOFF)

        result = run(_tool_check_guardrails({
            "root_dir": str(tmp_path),
            "handoffs_dir": str(handoffs_dir),
        }))
        data = parse(result)
        assert data["handoffs"]["passed"] is True
        assert data["handoffs"]["total"] == 1

    def test_check_with_invalid_handoffs(self, tmp_path):
        handoffs_dir = tmp_path / "handoffs"
        handoffs_dir.mkdir()
        (handoffs_dir / "HANDOFF-001.md").write_text("# bad")

        result = run(_tool_check_guardrails({
            "root_dir": str(tmp_path),
            "handoffs_dir": str(handoffs_dir),
        }))
        data = parse(result)
        assert data["handoffs"]["passed"] is False
        assert data["overall_passed"] is False

    def test_check_skips_missing_specs_dir(self, tmp_path):
        result = run(_tool_check_guardrails({
            "root_dir": str(tmp_path),
            "specs_dir": str(tmp_path / "nonexistent"),
        }))
        data = parse(result)
        assert "skipped" in data["specs"]
        assert data["specs"]["passed"] is True

    def test_check_skips_missing_handoffs_dir(self, tmp_path):
        result = run(_tool_check_guardrails({
            "root_dir": str(tmp_path),
            "handoffs_dir": str(tmp_path / "nonexistent"),
        }))
        data = parse(result)
        assert "skipped" in data["handoffs"]
        assert data["handoffs"]["passed"] is True

    def test_check_secrets_finding(self, tmp_path):
        # Write a file with a pattern that the scanner will flag
        (tmp_path / "config.py").write_text('AKIA1234567890ABCDEF = "something"\n')

        result = run(_tool_check_guardrails({"root_dir": str(tmp_path)}))
        data = parse(result)
        assert data["secrets"]["passed"] is False
        assert data["secrets"]["finding_count"] > 0
        assert len(data["secrets"]["findings"]) > 0
        assert data["overall_passed"] is False

    def test_check_default_cwd(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = run(_tool_check_guardrails({}))
        data = parse(result)
        # Should run without error (empty temp dir = clean)
        assert "overall_passed" in data

    def test_check_results_structure(self, tmp_path):
        result = run(_tool_check_guardrails({"root_dir": str(tmp_path)}))
        data = parse(result)
        # Verify all expected keys are present in each sub-result
        assert set(data["secrets"].keys()) >= {"passed", "finding_count", "findings"}
        assert set(data["specs"].keys()) >= {"passed"}
        assert set(data["handoffs"].keys()) >= {"passed"}


# ---------------------------------------------------------------------------
# list_tools (smoke test — just ensures the decorator ran without error)
# ---------------------------------------------------------------------------

class TestListTools:
    def test_list_tools_returns_five(self):
        from server import list_tools
        tools = run(list_tools())
        assert len(tools) == 5
        names = {t.name for t in tools}
        assert names == {
            "create_spec",
            "validate_spec",
            "create_handoff",
            "validate_handoff",
            "check_guardrails",
        }

    def test_all_tools_have_schemas(self):
        from server import list_tools
        tools = run(list_tools())
        for tool in tools:
            assert tool.inputSchema is not None
            assert "properties" in tool.inputSchema


# ---------------------------------------------------------------------------
# call_tool dispatcher
# ---------------------------------------------------------------------------

class TestCallTool:
    def test_unknown_tool_returns_error(self):
        from server import call_tool
        result = run(call_tool("nonexistent_tool", {}))
        data = parse(result)
        assert "error" in data
        assert "nonexistent_tool" in data["error"]
