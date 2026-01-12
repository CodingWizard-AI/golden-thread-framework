"""Tests for configuration loading."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from golden_thread import ConfigError
from golden_thread.config import Config, NotionConfig


class TestConfig:
    """Test configuration loading and validation."""

    def test_load_valid_config(self, tmp_path):
        """Test loading a valid configuration file."""
        config_file = tmp_path / ".golden-thread.config.yaml"
        config_data = {
            "notion": {
                "api_token": "test_token_123",
                "databases": {
                    "BR": "db-br-123",
                    "UR": "db-ur-123",
                    "FEAT": "db-feat-123",
                },
            },
            "services": {
                "discovery": {
                    "manifest_filename": ".golden-thread.yaml",
                    "root_directories": ["services/"],
                }
            },
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = Config.load(str(config_file))

        assert config.notion.api_token == "test_token_123"
        assert config.notion.databases["BR"] == "db-br-123"
        assert config.services.manifest_filename == ".golden-thread.yaml"

    def test_load_config_with_env_var(self, tmp_path):
        """Test environment variable substitution."""
        os.environ["TEST_NOTION_TOKEN"] = "secret_token"

        config_file = tmp_path / ".golden-thread.config.yaml"
        config_data = {"notion": {"api_token": "${TEST_NOTION_TOKEN}"}}

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = Config.load(str(config_file))

        assert config.notion.api_token == "secret_token"

        del os.environ["TEST_NOTION_TOKEN"]

    def test_load_config_missing_env_var(self, tmp_path):
        """Test error when environment variable is not set."""
        config_file = tmp_path / ".golden-thread.config.yaml"
        config_data = {"notion": {"api_token": "${MISSING_VAR}"}}

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        with pytest.raises(ConfigError, match="MISSING_VAR"):
            Config.load(str(config_file))

    def test_load_config_file_not_found(self):
        """Test error when config file doesn't exist."""
        with pytest.raises(ConfigError, match="not found"):
            Config.load("nonexistent.yaml")

    def test_load_config_missing_api_token(self, tmp_path):
        """Test error when API token is missing."""
        config_file = tmp_path / ".golden-thread.config.yaml"
        config_data = {"notion": {}}

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        with pytest.raises(ConfigError, match="api_token"):
            Config.load(str(config_file))

    def test_load_config_empty_file(self, tmp_path):
        """Test error when config file is empty."""
        config_file = tmp_path / ".golden-thread.config.yaml"
        config_file.touch()

        with pytest.raises(ConfigError, match="empty"):
            Config.load(str(config_file))

    def test_config_defaults(self, tmp_path):
        """Test default configuration values."""
        config_file = tmp_path / ".golden-thread.config.yaml"
        config_data = {"notion": {"api_token": "test_token"}}

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = Config.load(str(config_file))

        # Check defaults
        assert config.notion.version == "2022-06-28"
        assert config.notion.timeout == 30
        assert config.notion.cache_enabled is True
        assert config.notion.cache_ttl == 3600
        assert config.services.manifest_filename == ".golden-thread.yaml"
        assert config.validation.strict_mode is False
        assert "**/test_*.py" in config.validation.ignore_patterns

    def test_get_parser_config(self, tmp_path):
        """Test getting parser configuration."""
        config_file = tmp_path / ".golden-thread.config.yaml"
        config_data = {
            "notion": {"api_token": "test_token"},
            "parsers": {"python": {"enabled": True, "extract": ["classes", "functions"]}},
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = Config.load(str(config_file))

        python_config = config.get_parser_config("python")
        assert python_config is not None
        assert python_config.enabled is True
        assert "classes" in python_config.extract
