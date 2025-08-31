"""
Configuration management for View-from-CSV

PROVIDES: Configuration loading, validation, and defaults
DEPENDS: tomli/tomllib for TOML parsing
CONSUMED BY: All modules that need configuration
CONTRACT: Provides validated configuration data
TECH CHOICE: TOML for human-friendly configuration
RISK: Low - configuration validation prevents runtime errors
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import tomllib

from .defaults import DEFAULT_CONFIG
from .validation import validate_config, ConfigError

class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or self._get_default_config_file()
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
    
    def _get_default_config_file(self) -> Path:
        """Get the default configuration file path"""
        # Use x987-config in current directory for development
        # In production, this could be %APPDATA%/x987/
        config_dir = Path.cwd().parent / "x987-config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.toml"
    
    def load_config(self):
        """Load configuration from TOML file"""
        if not self.config_file.exists():
            self.create_default_config()
            return
        
        try:
            with open(self.config_file, 'rb') as f:
                file_config = tomllib.load(f)
            
            # Merge file config with defaults
            self._merge_config(file_config)
            
            # Validate the merged configuration
            validate_config(self.config)
            
        except Exception as e:
            raise ConfigError(f"Failed to load configuration from {self.config_file}: {e}")
    
    def _merge_config(self, file_config: Dict[str, Any]):
        """Merge file configuration with defaults"""
        def merge_dicts(default: Dict, override: Dict):
            for key, value in override.items():
                if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                    merge_dicts(default[key], value)
                else:
                    default[key] = value
        
        merge_dicts(self.config, file_config)
    
    def create_default_config(self):
        """Create a default configuration file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_file, 'w') as f:
                f.write("# View-from-CSV Configuration\n")
                f.write("# Generated automatically - modify as needed\n\n")
                
                # Convert DEFAULT_CONFIG to TOML format
                self._write_toml_section(f, self.config, "")
                
            print(f"✓ Created default configuration file: {self.config_file}")
            
        except Exception as e:
            raise ConfigError(f"Failed to create default configuration: {e}")
    
    def _write_toml_section(self, f, data: Dict[str, Any], prefix: str):
        """Write a TOML section to file"""
        for key, value in data.items():
            if isinstance(value, dict):
                section_name = f"{prefix}.{key}" if prefix else key
                f.write(f"\n[{section_name}]\n")
                self._write_toml_section(f, value, section_name)
            elif isinstance(value, list):
                f.write(f"{key} = [\n")
                for item in value:
                    if isinstance(item, str):
                        f.write(f'    "{item}",\n')
                    else:
                        f.write(f"    {item},\n")
                f.write("]\n")
            elif isinstance(value, str):
                f.write(f'{key} = "{value}"\n')
            else:
                f.write(f"{key} = {value}\n")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_search_urls(self) -> List[str]:
        """Get search URLs from configuration"""
        return self.get('search.urls', [])
    
    def get_scraping_config(self) -> Dict[str, Any]:
        """Get scraping configuration"""
        return self.get('scraping', {})
    
    def get_fair_value_config(self) -> Dict[str, Any]:
        """Get fair value configuration"""
        return self.get('fair_value', {})
    
    def get_options_config(self) -> Dict[str, Any]:
        """Get options configuration"""
        return self.get('options_v2', {})
    
    def reload(self):
        """Reload configuration from file"""
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            'config_file': str(self.config_file),
            'search_urls_count': len(self.get_search_urls()),
            'scraping_concurrency': self.get('scraping.concurrency'),
            'scraping_polite_delay_ms': self.get('scraping.polite_delay_ms'),
            'fair_value_base': self.get('fair_value.base_value_usd'),
            'options_enabled': self.get('options_v2.enabled')
        }

# Global configuration instance
_config_manager: Optional[ConfigManager] = None

def get_config() -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_timestamp_run_id() -> str:
    """Generate a timestamp-based run ID for this execution"""
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def reload_config():
    """Reload the global configuration"""
    global _config_manager
    if _config_manager:
        _config_manager.reload()
    else:
        _config_manager = ConfigManager()

def get_config_dir() -> Path:
    """Get the configuration directory path"""
    return Path.cwd().parent / "x987-config"

def get_data_dir() -> Path:
    """Get the data directory path"""
    return Path.cwd().parent / "x987-data"

def get_manual_csv_dir() -> Path:
    """Get the manual CSV directory path"""
    return get_config_dir() / "input" / "manual-csv"
