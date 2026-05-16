"""Tests for core/templates.py."""

import pytest
from agentic_sdlc.core.templates import get_spec_template, get_handoff_template


class TestGetSpecTemplate:
    def test_returns_string(self):
        content = get_spec_template()
        assert isinstance(content, str)

    def test_contains_frontmatter(self):
        content = get_spec_template()
        assert content.startswith("---")

    def test_contains_required_sections(self):
        content = get_spec_template()
        for section in ["Context", "Goal State", "Acceptance Criteria", "Rollback"]:
            assert section in content, f"Missing section: {section}"

    def test_contains_spec_id_placeholder(self):
        content = get_spec_template()
        assert "spec_id" in content

    def test_not_empty(self):
        content = get_spec_template()
        assert len(content) > 100


class TestGetHandoffTemplate:
    def test_returns_string(self):
        content = get_handoff_template()
        assert isinstance(content, str)

    def test_contains_frontmatter(self):
        content = get_handoff_template()
        assert content.startswith("---")

    def test_contains_required_sections(self):
        content = get_handoff_template()
        for section in ["Milestone Summary", "Work Completed", "Test Results", "Audit Trail Entry"]:
            assert section in content, f"Missing section: {section}"

    def test_contains_packet_id_placeholder(self):
        content = get_handoff_template()
        assert "packet_id" in content

    def test_not_empty(self):
        content = get_handoff_template()
        assert len(content) > 100
