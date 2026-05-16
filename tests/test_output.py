"""Tests for utils/output.py."""

import click
from click.testing import CliRunner

from agentic_sdlc.utils.output import success, error, warn, info, step, header


def make_cmd(fn):
    """Wrap a function as a Click command for testing."""
    @click.command()
    def _cmd():
        fn()
    return _cmd


class TestOutputHelpers:
    def setup_method(self):
        self.runner = CliRunner()

    def test_success_outputs_text(self):
        @click.command()
        def cmd():
            success("All good!")
        result = self.runner.invoke(cmd)
        assert "All good!" in result.output

    def test_error_outputs_text(self):
        @click.command()
        def cmd():
            error("Something broke")
        result = self.runner.invoke(cmd)
        assert "Something broke" in result.output

    def test_warn_outputs_text(self):
        @click.command()
        def cmd():
            warn("Watch out")
        result = self.runner.invoke(cmd)
        assert "Watch out" in result.output

    def test_info_outputs_text(self):
        @click.command()
        def cmd():
            info("FYI")
        result = self.runner.invoke(cmd)
        assert "FYI" in result.output

    def test_step_outputs_text(self):
        @click.command()
        def cmd():
            step("Step 1")
        result = self.runner.invoke(cmd)
        assert "Step 1" in result.output

    def test_header_outputs_text(self):
        @click.command()
        def cmd():
            header("My Section")
        result = self.runner.invoke(cmd)
        assert "My Section" in result.output
