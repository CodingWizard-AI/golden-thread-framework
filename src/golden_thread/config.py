"""Configuration management for Golden Thread Framework."""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from . import ConfigError


@dataclass
class NotionConfig:
    """Notion API configuration."""

    api_token: str
    version: str = "2022-06-28"
    timeout: int = 30
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour
    cache_directory: str = ".golden-thread-cache"
    databases: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServicesConfig:
    """Service discovery configuration."""

    discovery_strategy: str = "manifest"
    manifest_filename: str = ".golden-thread.yaml"
    root_directories: List[str] = field(default_factory=lambda: ["services/", "packages/"])


@dataclass
class ParserConfig:
    """Parser configuration for a specific language."""

    enabled: bool = True
    extract: List[str] = field(default_factory=list)


@dataclass
class ParsersConfig:
    """Configuration for all parsers."""

    python: ParserConfig = field(default_factory=lambda: ParserConfig(
        enabled=True,
        extract=["classes", "functions", "methods"]
    ))
    typescript: ParserConfig = field(default_factory=lambda: ParserConfig(
        enabled=True,
        extract=["classes", "functions", "interfaces", "types"]
    ))
    go: ParserConfig = field(default_factory=lambda: ParserConfig(
        enabled=True,
        extract=["structs", "functions", "methods", "interfaces"]
    ))


@dataclass
class ValidationConfig:
    """Validation behavior configuration."""

    strict_mode: bool = False
    ignore_patterns: List[str] = field(default_factory=lambda: [
        "**/test_*.py",
        "**/*.test.ts",
        "**/*_test.go",
        "**/mock_*.py",
    ])
    required_ids: List[str] = field(default_factory=lambda: ["BR", "UR", "FEAT", "FR"])


@dataclass
class ReportsConfig:
    """Report generation configuration."""

    output_directory: str = ".golden-thread-reports"
    formats: List[str] = field(default_factory=lambda: ["json", "html"])


@dataclass
class Config:
    """Main configuration for Golden Thread Framework."""

    notion: NotionConfig
    services: ServicesConfig = field(default_factory=ServicesConfig)
    parsers: ParsersConfig = field(default_factory=ParsersConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    reports: ReportsConfig = field(default_factory=ReportsConfig)

    @classmethod
    def load(cls, config_path: str = ".golden-thread.config.yaml") -> "Config":
        """
        Load configuration from YAML file.

        Supports environment variable substitution using ${VAR_NAME} syntax.

        Args:
            config_path: Path to configuration file

        Returns:
            Config object

        Raises:
            ConfigError: If configuration file is invalid or missing
        """
        config_file = Path(config_path)

        if not config_file.exists():
            raise ConfigError(
                f"Configuration file not found: {config_path}\n"
                f"Please create a .golden-thread.config.yaml file in your repository root."
            )

        try:
            with open(config_file) as f:
                raw_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Failed to parse configuration file: {e}")

        if not raw_config:
            raise ConfigError("Configuration file is empty")

        # Substitute environment variables
        raw_config = cls._substitute_env_vars(raw_config)

        # Validate and construct
        try:
            return cls.from_dict(raw_config)
        except Exception as e:
            raise ConfigError(f"Invalid configuration: {e}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Construct Config from dictionary."""
        # Parse Notion config
        notion_data = data.get("notion", {})
        if not notion_data.get("api_token"):
            raise ConfigError(
                "Missing required configuration: notion.api_token\n"
                "Set NOTION_API_TOKEN environment variable or add it to config file."
            )

        notion_config = NotionConfig(
            api_token=notion_data["api_token"],
            version=notion_data.get("version", "2022-06-28"),
            timeout=notion_data.get("timeout", 30),
            cache_enabled=notion_data.get("cache", {}).get("enabled", True),
            cache_ttl=notion_data.get("cache", {}).get("ttl", 3600),
            cache_directory=notion_data.get("cache", {}).get("directory", ".golden-thread-cache"),
            databases=notion_data.get("databases", {}),
        )

        # Parse services config
        services_data = data.get("services", {})
        services_config = ServicesConfig(
            discovery_strategy=services_data.get("discovery", {}).get("strategy", "manifest"),
            manifest_filename=services_data.get("discovery", {}).get(
                "manifest_filename", ".golden-thread.yaml"
            ),
            root_directories=services_data.get("discovery", {}).get(
                "root_directories", ["services/", "packages/"]
            ),
        )

        # Parse parsers config
        parsers_data = data.get("parsers", {})
        python_data = parsers_data.get("python", {})
        typescript_data = parsers_data.get("typescript", {})
        go_data = parsers_data.get("go", {})

        parsers_config = ParsersConfig(
            python=ParserConfig(
                enabled=python_data.get("enabled", True),
                extract=python_data.get("extract", ["classes", "functions", "methods"]),
            ),
            typescript=ParserConfig(
                enabled=typescript_data.get("enabled", True),
                extract=typescript_data.get("extract", ["classes", "functions", "interfaces", "types"]),
            ),
            go=ParserConfig(
                enabled=go_data.get("enabled", True),
                extract=go_data.get("extract", ["structs", "functions", "methods", "interfaces"]),
            ),
        )

        # Parse validation config
        validation_data = data.get("validation", {})
        validation_config = ValidationConfig(
            strict_mode=validation_data.get("strict_mode", False),
            ignore_patterns=validation_data.get("ignore_patterns", [
                "**/test_*.py", "**/*.test.ts", "**/*_test.go", "**/mock_*.py"
            ]),
            required_ids=validation_data.get("required_ids", ["BR", "UR", "FEAT", "FR"]),
        )

        # Parse reports config
        reports_data = data.get("reports", {})
        reports_config = ReportsConfig(
            output_directory=reports_data.get("output_directory", ".golden-thread-reports"),
            formats=reports_data.get("formats", ["json", "html"]),
        )

        return cls(
            notion=notion_config,
            services=services_config,
            parsers=parsers_config,
            validation=validation_config,
            reports=reports_config,
        )

    @classmethod
    def _substitute_env_vars(cls, obj: Any) -> Any:
        """
        Recursively substitute environment variables in configuration.

        Replaces ${VAR_NAME} with the value of the environment variable.
        """
        if isinstance(obj, dict):
            return {key: cls._substitute_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [cls._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # Find all ${VAR_NAME} patterns
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, obj)

            result = obj
            for var_name in matches:
                env_value = os.environ.get(var_name)
                if env_value is None:
                    raise ConfigError(
                        f"Environment variable ${{{var_name}}} is not set\n"
                        f"Please set the {var_name} environment variable."
                    )
                result = result.replace(f"${{{var_name}}}", env_value)

            return result
        else:
            return obj

    def get_parser_config(self, language: str) -> Optional[ParserConfig]:
        """Get parser configuration for a specific language."""
        return getattr(self.parsers, language.lower(), None)
