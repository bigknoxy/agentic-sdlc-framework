"""Tests for agentic-sdlc init command."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from agentic_sdlc.cli import cli


class TestInitCommand:
    def setup_method(self):
        self.runner = CliRunner()

    def test_init_creates_project_directory(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["init", "my-project"])
            assert result.exit_code == 0, result.output
            assert Path("my-project").is_dir()

    def test_init_creates_subdirectories(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["init", "my-project"])
            assert result.exit_code == 0, result.output
            for subdir in ["specs", "handoffs", "adrs"]:
                assert Path(f"my-project/{subdir}").is_dir(), f"Missing: {subdir}"

    def test_init_creates_config_file(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["init", "my-project"])
            assert result.exit_code == 0, result.output
            cfg_path = Path("my-project/.agentic-sdlc.yaml")
            assert cfg_path.exists()
            content = cfg_path.read_text()
            assert "my-project" in content

    def test_init_fails_on_existing_directory(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            Path("existing").mkdir()
            result = self.runner.invoke(cli, ["init", "existing"])
            assert result.exit_code != 0

    def test_init_prints_next_steps(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["init", "my-project"])
            assert result.exit_code == 0
            assert "Next steps" in result.output
            assert "my-project" in result.output

    def test_init_shows_success_message(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["init", "cool-project"])
            assert result.exit_code == 0
            assert "cool-project" in result.output

    def test_init_with_hyphens_in_name(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["init", "my-cool-api"])
            assert result.exit_code == 0
            assert Path("my-cool-api").is_dir()
