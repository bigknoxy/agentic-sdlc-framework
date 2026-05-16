"""Tests for agentic-sdlc metrics command."""

import json
from pathlib import Path
from click.testing import CliRunner

from agentic_sdlc.cli import cli


class TestMetricsCommand:
    def setup_method(self):
        self.runner = CliRunner()

    def test_metrics_no_directories(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["metrics"])
            assert result.exit_code == 0

    def test_metrics_json_format(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["metrics", "--format", "json"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert "specs" in data
            assert "handoffs" in data
            assert "scope" in data

    def test_metrics_json_with_scope(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["metrics", "--format", "json"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["scope"] == "All Time"

    def test_metrics_week_flag(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["metrics", "--week", "--format", "json"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["scope"] == "This Week"

    def test_metrics_with_specs(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            # Create a spec via the CLI
            self.runner.invoke(cli, ["spec", "create", "--title", "My Feature"])
            result = self.runner.invoke(cli, ["metrics", "--format", "json"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["specs"]["total"] == 1

    def test_metrics_with_handoffs(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            self.runner.invoke(cli, ["handoff", "create", "--milestone", "M1"])
            result = self.runner.invoke(cli, ["metrics", "--format", "json"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["handoffs"]["total"] == 1

    def test_metrics_table_format_default(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["metrics"])
            assert result.exit_code == 0
            assert "Specs" in result.output or "Handoffs" in result.output or "Metrics" in result.output

    def test_metrics_pass_rate_in_json(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["metrics", "--format", "json"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert "validation_pass_rate_pct" in data["specs"]
            assert "validation_pass_rate_pct" in data["handoffs"]

    def test_metrics_invalid_format(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["metrics", "--format", "xml"])
            assert result.exit_code != 0
