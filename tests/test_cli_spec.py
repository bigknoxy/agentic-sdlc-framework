"""Tests for agentic-sdlc spec command group."""

import re
from pathlib import Path
from click.testing import CliRunner

from agentic_sdlc.cli import cli


class TestSpecCreate:
    def setup_method(self):
        self.runner = CliRunner()

    def test_spec_create_requires_title(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["spec", "create"])
            assert result.exit_code != 0

    def test_spec_create_with_title(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["spec", "create", "--title", "My Feature"])
            assert result.exit_code == 0, result.output
            specs = list(Path("specs").glob("*.md"))
            assert len(specs) == 1

    def test_spec_create_generates_spec_id(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["spec", "create", "--title", "My Feature"])
            assert result.exit_code == 0, result.output
            spec_file = next(Path("specs").glob("*.md"))
            content = spec_file.read_text()
            assert re.search(r"spec_id: SPEC-\d{4}-\d{2}-\d{2}-\d{3}", content)

    def test_spec_create_inserts_title(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["spec", "create", "--title", "Auth Service"])
            assert result.exit_code == 0, result.output
            spec_file = next(Path("specs").glob("*.md"))
            content = spec_file.read_text()
            assert "Auth Service" in content

    def test_spec_create_default_priority(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["spec", "create", "--title", "Test"])
            assert result.exit_code == 0, result.output
            spec_file = next(Path("specs").glob("*.md"))
            content = spec_file.read_text()
            assert "priority: p1" in content

    def test_spec_create_custom_priority(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["spec", "create", "--title", "Urgent", "--priority", "p0"])
            assert result.exit_code == 0, result.output
            spec_file = next(Path("specs").glob("*.md"))
            content = spec_file.read_text()
            assert "priority: p0" in content

    def test_spec_create_auto_increments(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            self.runner.invoke(cli, ["spec", "create", "--title", "First"])
            self.runner.invoke(cli, ["spec", "create", "--title", "Second"])
            specs = sorted(Path("specs").glob("*.md"))
            assert len(specs) == 2
            assert specs[0].name < specs[1].name

    def test_spec_create_creates_specs_dir(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["spec", "create", "--title", "Test"])
            assert result.exit_code == 0, result.output
            assert Path("specs").is_dir()

    def test_spec_create_invalid_priority(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["spec", "create", "--title", "T", "--priority", "invalid"])
            assert result.exit_code != 0

    def test_spec_create_custom_specs_dir(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, [
                "spec", "create", "--title", "Test", "--specs-dir", "my-specs"
            ])
            assert result.exit_code == 0, result.output
            assert Path("my-specs").is_dir()
            specs = list(Path("my-specs").glob("*.md"))
            assert len(specs) == 1


class TestSpecValidate:
    def setup_method(self):
        self.runner = CliRunner()

    def test_validate_existing_spec(self, tmp_path):
        # Create a spec first, then validate it
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            self.runner.invoke(cli, ["spec", "create", "--title", "Test"])
            spec_file = next(Path("specs").glob("*.md"))
            result = self.runner.invoke(cli, ["spec", "validate", str(spec_file)])
            # New spec from template may not pass (has unfilled placeholders)
            # but the command should run without crashing
            assert result.exit_code in (0, 1)

    def test_validate_nonexistent_file(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["spec", "validate", "nonexistent.md"])
            assert result.exit_code != 0
            assert "not found" in result.output.lower() or "File" in result.output

    def test_validate_all_specs_empty_dir(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            Path("specs").mkdir()
            result = self.runner.invoke(cli, ["spec", "validate"])
            # Empty dir: no specs to fail
            assert result.exit_code == 0

    def test_validate_all_specs_no_dir(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["spec", "validate"])
            # No specs dir: warn but don't crash
            assert result.exit_code == 0


class TestSpecList:
    def setup_method(self):
        self.runner = CliRunner()

    def test_list_with_specs(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            self.runner.invoke(cli, ["spec", "create", "--title", "My Feature"])
            result = self.runner.invoke(cli, ["spec", "list"])
            assert result.exit_code == 0, result.output
            assert "SPEC-" in result.output
            assert "My Feature" in result.output

    def test_list_empty(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            Path("specs").mkdir()
            result = self.runner.invoke(cli, ["spec", "list"])
            assert result.exit_code == 0
            assert "No specs" in result.output

    def test_list_no_directory(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["spec", "list"])
            assert result.exit_code == 0
            assert "not found" in result.output.lower() or "No" in result.output
