"""
Configuration validation for View-from-CSV

PROVIDES: Configuration validation and error handling
DEPENDS: None
CONSUMED BY: Configuration manager
CONTRACT: Validates configuration data and provides helpful error messages
TECH CHOICE: Python validation with clear error messages
RISK: Low - validation prevents runtime errors
"""

from typing import Dict, Any, List
from pathlib import Path

class ConfigError(Exception):
    """Configuration validation error"""
    pass

def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the configuration dictionary
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ConfigError: If configuration is invalid
    """
    try:
        _validate_required_sections(config)
        _validate_search_section(config.get('search', {}))
        _validate_scraping_section(config.get('scraping', {}))
        _validate_fair_value_section(config.get('fair_value', {}))
        _validate_options_section(config.get('options_v2', {}))
        _validate_pipeline_section(config.get('pipeline', {}))
        _validate_view_section(config.get('view', {}))
        
    except Exception as e:
        if isinstance(e, ConfigError):
            raise
        raise ConfigError(f"Configuration validation failed: {e}")

def _validate_required_sections(config: Dict[str, Any]) -> None:
    """Validate that required configuration sections exist"""
    required_sections = ['search', 'scraping', 'fair_value']
    
    for section in required_sections:
        if section not in config:
            raise ConfigError(f"Missing required configuration section: {section}")
        
        if not isinstance(config[section], dict):
            raise ConfigError(f"Configuration section '{section}' must be a dictionary")

def _validate_search_section(search_config: Dict[str, Any]) -> None:
    """Validate search configuration section"""
    if 'urls' not in search_config:
        raise ConfigError("Search configuration must contain 'urls' list")
    
    urls = search_config['urls']
    if not isinstance(urls, list):
        raise ConfigError("Search URLs must be a list")
    
    if not urls:
        raise ConfigError("Search URLs list cannot be empty")
    
    for i, url in enumerate(urls):
        if not isinstance(url, str):
            raise ConfigError(f"Search URL at index {i} must be a string")
        
        if not url.startswith(('http://', 'https://')):
            raise ConfigError(f"Search URL at index {i} must be a valid HTTP/HTTPS URL: {url}")

def _validate_scraping_section(scraping_config: Dict[str, Any]) -> None:
    """Validate scraping configuration section"""
    required_keys = ['concurrency', 'polite_delay_ms', 'cap_listings']
    
    for key in required_keys:
        if key not in scraping_config:
            raise ConfigError(f"Scraping configuration must contain '{key}'")
    
    # Validate concurrency
    concurrency = scraping_config['concurrency']
    if not isinstance(concurrency, int) or concurrency < 1:
        raise ConfigError("Scraping concurrency must be a positive integer")
    
    # Validate polite delay
    delay = scraping_config['polite_delay_ms']
    if not isinstance(delay, (int, float)) or delay < 0:
        raise ConfigError("Scraping polite delay must be a non-negative number")
    
    # Validate cap listings
    cap = scraping_config['cap_listings']
    if not isinstance(cap, int) or cap < 1:
        raise ConfigError("Scraping cap listings must be a positive integer")
    
    # Validate timeout
    if 'timeout_seconds' in scraping_config:
        timeout = scraping_config['timeout_seconds']
        if not isinstance(timeout, (int, float)) or timeout < 1:
            raise ConfigError("Scraping timeout must be a positive number")

def _validate_fair_value_section(fair_value_config: Dict[str, Any]) -> None:
    """Validate fair value configuration section"""
    required_keys = ['base_value_usd', 'year_step_usd']
    
    for key in required_keys:
        if key not in fair_value_config:
            raise ConfigError(f"Fair value configuration must contain '{key}'")
    
    # Validate base value
    base_value = fair_value_config['base_value_usd']
    if not isinstance(base_value, (int, float)) or base_value < 0:
        raise ConfigError("Fair value base value must be a non-negative number")
    
    # Validate year step
    year_step = fair_value_config['year_step_usd']
    if not isinstance(year_step, (int, float)) or year_step < 0:
        raise ConfigError("Fair value year step must be a non-negative number")
    
    # Validate special trim premiums if present
    if 'special_trim_premiums' in fair_value_config:
        premiums = fair_value_config['special_trim_premiums']
        if not isinstance(premiums, dict):
            raise ConfigError("Special trim premiums must be a dictionary")
        
        for trim, premium in premiums.items():
            if not isinstance(premium, (int, float)) or premium < 0:
                raise ConfigError(f"Special trim premium for '{trim}' must be a non-negative number")

def _validate_options_section(options_config: Dict[str, Any]) -> None:
    """Validate options configuration section"""
    if 'enabled' in options_config:
        enabled = options_config['enabled']
        if not isinstance(enabled, bool):
            raise ConfigError("Options enabled must be a boolean")
    
    if 'confidence_threshold' in options_config:
        threshold = options_config['confidence_threshold']
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
            raise ConfigError("Options confidence threshold must be between 0 and 1")
    
    if 'max_options_display' in options_config:
        max_display = options_config['max_options_display']
        if not isinstance(max_display, int) or max_display < 1:
            raise ConfigError("Options max display must be a positive integer")

def _validate_pipeline_section(pipeline_config: Dict[str, Any]) -> None:
    """Validate pipeline configuration section"""
    if 'output_directory' in pipeline_config:
        output_dir = pipeline_config['output_directory']
        if not isinstance(output_dir, str):
            raise ConfigError("Pipeline output directory must be a string")
    
    if 'create_separate_files' in pipeline_config:
        create_separate = pipeline_config['create_separate_files']
        if not isinstance(create_separate, bool):
            raise ConfigError("Pipeline create separate files must be a boolean")

def _validate_view_section(view_config: Dict[str, Any]) -> None:
    """Validate view configuration section"""
    if 'theme' in view_config:
        theme = view_config['theme']
        if not isinstance(theme, str):
            raise ConfigError("View theme must be a string")
    
    if 'show_progress' in view_config:
        show_progress = view_config['show_progress']
        if not isinstance(show_progress, bool):
            raise ConfigError("View show progress must be a boolean")
    
    if 'detailed_output' in view_config:
        detailed = view_config['detailed_output']
        if not isinstance(detailed, bool):
            raise ConfigError("View detailed output must be a boolean")
    
    if 'color_output' in view_config:
        color = view_config['color_output']
        if not isinstance(color, bool):
            raise ConfigError("View color output must be a boolean")

def validate_url(url: str) -> bool:
    """Validate a single URL"""
    return isinstance(url, str) and url.startswith(('http://', 'https://'))

def validate_file_path(path: str) -> bool:
    """Validate a file path"""
    try:
        Path(path)
        return True
    except Exception:
        return False
