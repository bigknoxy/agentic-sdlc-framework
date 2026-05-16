"""Tests for core/config.py."""

import pytest
import yaml
from pathlib import Path

from agentic_sdlc.core.config import (
    find_config_file,
    load_config,
    save_config,
    DEFAULT_CONFIG_YAML,
    _DEFAULT_CONFIG,
)


class TestFindConfigFile:
    def test_finds_config_in_cwd(self, tmp_path):
        cfg = tmp_path / ".agentic-sdlc.yaml"
        cfg.write_text("project:\n  name: test\n")
        result = find_config_file(tmp_path)
        assert result == cfg

    def test_finds_config_in_parent(self, tmp_path):
        cfg = tmp_path / ".agentic-sdlc.yaml"
        cfg.write_text("project:\n  name: test\n")
        subdir = tmp_path / "sub"
        subdir.mkdir()
        result = find_config_file(subdir)
        assert result == cfg

    def test_returns_none_when_not_found(self, tmp_path):
        result = find_config_file(tmp_path)
        assert result is None


class TestLoadConfig:
    def test_returns_defaults_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = load_config(tmp_path)
        assert cfg["templates"]["specs_dir"] == "specs"
        assert cfg["framework"]["strict_mode"] is False

    def test_loads_from_file(self, tmp_path):
        cfg_file = tmp_path / ".agentic-sdlc.yaml"
        cfg_file.write_text("project:\n  name: myproject\n  type: web\n")
        cfg = load_config(tmp_path)
        assert cfg["project"]["name"] == "myproject"
        assert cfg["project"]["type"] == "web"

    def test_merges_with_defaults(self, tmp_path):
        cfg_file = tmp_path / ".agentic-sdlc.yaml"
        cfg_file.write_text("project:\n  name: partial\n")
        cfg = load_config(tmp_path)
        # Specified value overrides default
        assert cfg["project"]["name"] == "partial"
        # Unspecified value comes from defaults
        assert cfg["templates"]["specs_dir"] == "specs"

    def test_graceful_on_invalid_yaml(self, tmp_path):
        cfg_file = tmp_path / ".agentic-sdlc.yaml"
        cfg_file.write_text(":\t invalid: yaml: {{{{")
        cfg = load_config(tmp_path)
        # Should fall back to defaults
        assert cfg["templates"]["specs_dir"] == "specs"


class TestSaveConfig:
    def test_saves_yaml(self, tmp_path):
        cfg = {"project": {"name": "test"}}
        out = tmp_path / ".agentic-sdlc.yaml"
        save_config(cfg, out)
        loaded = yaml.safe_load(out.read_text())
        assert loaded["project"]["name"] == "test"


class TestDefaultConfigTemplate:
    def test_template_formats_correctly(self):
        rendered = DEFAULT_CONFIG_YAML.format(project_name="my-api")
        assert "my-api" in rendered
        assert "specs_dir" in rendered

    def test_default_config_has_all_top_level_keys(self):
        for key in ["project", "framework", "templates", "guardrails", "agents", "compliance"]:
            assert key in _DEFAULT_CONFIG
