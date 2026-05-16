"""Tests for agentic-sdlc check command."""

from pathlib import Path
from click.testing import CliRunner

from agentic_sdlc.cli import cli
from agentic_sdlc.commands.check import _scan_secrets, _iter_files


class TestCheckCommand:
    def setup_method(self):
        self.runner = CliRunner()

    def test_check_no_flags_shows_help(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["check"])
            assert result.exit_code == 0

    def test_check_secrets_clean_project(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            Path("clean.py").write_text("def hello():\n    return 'world'\n")
            result = self.runner.invoke(cli, ["check", "--secrets"])
            assert result.exit_code == 0
            assert "No secrets" in result.output

    def test_check_secrets_finds_api_key(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            # Use a value that matches [A-Za-z0-9+/]{20,} (no hyphens/underscores)
            Path("config.py").write_text(
                'API_KEY = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEF"\n'
            )
            result = self.runner.invoke(cli, ["check", "--secrets"])
            assert result.exit_code == 1
            assert "API key" in result.output or "api" in result.output.lower()

    def test_check_specs_no_specs_dir(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["check", "--specs"])
            assert result.exit_code == 0
            assert "skipping" in result.output.lower() or "not found" in result.output.lower()

    def test_check_handoffs_no_handoffs_dir(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            result = self.runner.invoke(cli, ["check", "--handoffs"])
            assert result.exit_code == 0

    def test_check_all_clean_project(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            Path("specs").mkdir()
            Path("handoffs").mkdir()
            result = self.runner.invoke(cli, ["check", "--all"])
            assert result.exit_code == 0
            assert "passed" in result.output.lower()

    def test_check_exits_1_on_failure(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            Path("bad.py").write_text(
                'SECRET_KEY = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGH"\n'
            )
            result = self.runner.invoke(cli, ["check", "--secrets"])
            assert result.exit_code == 1

    def test_check_skips_comments(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            Path("code.py").write_text(
                "# api_key = 'sk-abcdefghijklmnopqrstuvwxyz123456'\n"
                "x = 1\n"
            )
            result = self.runner.invoke(cli, ["check", "--secrets"])
            assert result.exit_code == 0

    def test_check_skips_placeholder_lines(self, tmp_path):
        with self.runner.isolated_filesystem(temp_dir=tmp_path):
            Path("code.py").write_text(
                'api_key = "your_api_key_here"\n'
            )
            result = self.runner.invoke(cli, ["check", "--secrets"])
            assert result.exit_code == 0


class TestScanSecrets:
    def test_detects_aws_key(self, tmp_path):
        f = tmp_path / "config.py"
        # Real AWS access key format: AKIA + 16 uppercase chars/digits (no 'example' word)
        f.write_text('AWS_KEY = "AKIAIOSFODNN7REALKEYBCD"\n')
        findings = _scan_secrets(tmp_path)
        assert len(findings) >= 1

    def test_skips_git_directory(self, tmp_path):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text('[core]\n    key = "AKIAIOSFODNN7EXAMPLE_abc"\n')
        findings = _scan_secrets(tmp_path)
        assert len(findings) == 0

    def test_skips_pycache(self, tmp_path):
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "code.py").write_text('SECRET = "abcdefghijklmnopqrstuvwxyz_key"\n')
        findings = _scan_secrets(tmp_path)
        assert len(findings) == 0

    def test_clean_file_no_findings(self, tmp_path):
        (tmp_path / "app.py").write_text("def main():\n    pass\n")
        findings = _scan_secrets(tmp_path)
        assert findings == []
