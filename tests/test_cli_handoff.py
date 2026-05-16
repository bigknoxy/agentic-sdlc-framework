"""Tests for agentic-sdlc handoff command group."""

import re
from pathlib import Path
from click.testing import CliRunner

from agentic_sdlc.cli import cli


class TestHandoffCreate:
    def setup_method(self):
        self.runner = CliRunner()

    def test_handoff_create_requires_milestone(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["handoff", "create"])
            assert result.exit_code != 0

    def test_handoff_create_with_milestone(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["handoff", "create", "--milestone", "M1"])
            assert result.exit_code == 0, result.output
            packets = list(Path("handoffs").glob("*.md"))
            assert len(packets) == 1

    def test_handoff_create_generates_packet_id(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["handoff", "create", "--milestone", "M1"])
            assert result.exit_code == 0, result.output
            packet_file = next(Path("handoffs").glob("*.md"))
            content = packet_file.read_text()
            assert re.search(r"packet_id: HANDOFF-(planner|executor)-\d+", content)

    def test_handoff_create_inserts_milestone(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["handoff", "create", "--milestone", "Sprint 1"])
            assert result.exit_code == 0, result.output
            packet_file = next(Path("handoffs").glob("*.md"))
            content = packet_file.read_text()
            assert "Sprint 1" in content

    def test_handoff_create_default_agent(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["handoff", "create", "--milestone", "M1"])
            assert result.exit_code == 0, result.output
            packet_file = next(Path("handoffs").glob("*.md"))
            content = packet_file.read_text()
            assert "claude-code" in content

    def test_handoff_create_custom_agent(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, [
                "handoff", "create", "--milestone", "M1", "--agent", "custom-agent"
            ])
            assert result.exit_code == 0, result.output
            packet_file = next(Path("handoffs").glob("*.md"))
            content = packet_file.read_text()
            assert "custom-agent" in content

    def test_handoff_create_planner_role(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, [
                "handoff", "create", "--milestone", "M1", "--agent", "claude-code-planner"
            ])
            assert result.exit_code == 0, result.output
            packet_file = next(Path("handoffs").glob("*.md"))
            content = packet_file.read_text()
            assert "HANDOFF-planner-" in content

    def test_handoff_create_auto_increments(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            self.runner.invoke(cli, ["handoff", "create", "--milestone", "M1"])
            self.runner.invoke(cli, ["handoff", "create", "--milestone", "M2"])
            packets = sorted(Path("handoffs").glob("*.md"))
            assert len(packets) == 2
            assert packets[0].name < packets[1].name

    def test_handoff_create_creates_handoffs_dir(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["handoff", "create", "--milestone", "M1"])
            assert result.exit_code == 0, result.output
            assert Path("handoffs").is_dir()


class TestHandoffValidate:
    def setup_method(self):
        self.runner = CliRunner()

    def test_validate_nonexistent_file(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["handoff", "validate", "nonexistent.md"])
            assert result.exit_code != 0

    def test_validate_all_empty_dir(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            Path("handoffs").mkdir()
            result = self.runner.invoke(cli, ["handoff", "validate"])
            assert result.exit_code == 0

    def test_validate_all_no_dir(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["handoff", "validate"])
            assert result.exit_code == 0


class TestHandoffList:
    def setup_method(self):
        self.runner = CliRunner()

    def test_list_with_packets(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            self.runner.invoke(cli, ["handoff", "create", "--milestone", "M1"])
            result = self.runner.invoke(cli, ["handoff", "list"])
            assert result.exit_code == 0, result.output
            assert "HANDOFF-" in result.output
            assert "M1" in result.output

    def test_list_empty(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            Path("handoffs").mkdir()
            result = self.runner.invoke(cli, ["handoff", "list"])
            assert result.exit_code == 0
            assert "No handoff" in result.output

    def test_list_no_directory(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["handoff", "list"])
            assert result.exit_code == 0
