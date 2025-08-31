"""
Configuration management for View-from-CSV

PROVIDES: Configuration loading, validation, and defaults
DEPENDS: tomli/tomllib for TOML parsing
CONSUMED BY: All modules that need configuration (pipeline, CLI, etc.)
CONTRACT: Provides validated configuration data with environment variable overrides
TECH CHOICE: TOML for human-friendly configuration
RISK: Low - configuration validation prevents runtime errors
"""

from .manager import ConfigManager, get_config, get_timestamp_run_id, get_config_dir, get_data_dir, get_manual_csv_dir
from .validation import validate_config, ConfigError
from .defaults import DEFAULT_CONFIG

__all__ = [
    "ConfigManager",
    "get_config",
    "get_timestamp_run_id",
    "get_config_dir",
    "get_data_dir", 
    "get_manual_csv_dir",
    "validate_config",
    "ConfigError",
    "DEFAULT_CONFIG"
]
