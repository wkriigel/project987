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
        # Fair value configuration removed in MSRP-only cleanup
        _validate_pricing_mode(config.get('pricing_mode', 'msrp_only'))
        _validate_options_section(config.get('options_v2', {}))
        _validate_pipeline_section(config.get('pipeline', {}))
        _validate_vehicles_section(config.get('vehicles', {}))
        _validate_options_per_generation(config.get('options_per_generation', {}))
        _validate_view_section(config.get('view', {}))
        
    except Exception as e:
        if isinstance(e, ConfigError):
            raise
        raise ConfigError(f"Configuration validation failed: {e}")

def _validate_required_sections(config: Dict[str, Any]) -> None:
    """Validate that required configuration sections exist"""
    required_sections = ['search', 'scraping']
    # fair_value removed in MSRP-only cleanup
    
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

def _validate_pricing_mode(mode: Any) -> None:
    """Validate pricing_mode flag"""
    allowed = {'msrp_only', 'current'}
    m = str(mode).lower() if mode is not None else 'msrp_only'
    if m not in allowed:
        raise ConfigError(f"pricing_mode must be one of {sorted(allowed)}")

def _validate_fair_value_section(fair_value_config: Dict[str, Any]) -> None:
    """Deprecated: kept for backward compatibility (no validation)."""
    return

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

def _validate_vehicles_section(vehicles_config: Dict[str, Any]) -> None:
    """Validate vehicles (models/generations/trims) section"""
    if not vehicles_config:
        return
    if not isinstance(vehicles_config, dict):
        raise ConfigError("'vehicles' must be a table (dict)")
    models = vehicles_config.get('models', {})
    if not isinstance(models, dict):
        raise ConfigError("'vehicles.models' must be a table (dict)")
    for model_key, model_cfg in models.items():
        if not isinstance(model_cfg, dict):
            raise ConfigError(f"vehicles.models.{model_key} must be a table")
        name = model_cfg.get('name')
        if not isinstance(name, str) or not name:
            raise ConfigError(f"vehicles.models.{model_key}.name must be a non-empty string")
        syns = model_cfg.get('synonyms', [])
        if not isinstance(syns, list) or not all(isinstance(s, str) for s in syns):
            raise ConfigError(f"vehicles.models.{model_key}.synonyms must be a list of strings")
        # Validate generations (optional)
        gens = model_cfg.get('generations', [])
        if gens:
            if not isinstance(gens, list):
                raise ConfigError(f"vehicles.models.{model_key}.generations must be a list")
            for g in gens:
                if not isinstance(g, dict):
                    raise ConfigError(f"vehicles.models.{model_key}.generations[] must be tables")
                code = g.get('code')
                if not isinstance(code, str) or not code:
                    raise ConfigError(f"vehicles.models.{model_key}.generations.code must be a non-empty string")
                years = g.get('years', {})
                if not isinstance(years, dict) or 'min' not in years:
                    raise ConfigError(f"vehicles.models.{model_key}.generations.years must include 'min'")
                min_year = years.get('min')
                max_year = years.get('max', None)
                if not isinstance(min_year, int):
                    raise ConfigError(f"vehicles.models.{model_key}.generations.years.min must be an integer")
                if max_year is not None and not isinstance(max_year, int):
                    raise ConfigError(f"vehicles.models.{model_key}.generations.years.max must be an integer if present")
                trims = g.get('trims', [])
                if not isinstance(trims, list):
                    raise ConfigError(f"vehicles.models.{model_key}.generations.trims must be a list")
                for t in trims:
                    if not isinstance(t, dict):
                        raise ConfigError(f"vehicles.models.{model_key}.generations.trims[] must be tables")
                    tname = t.get('name')
                    if not isinstance(tname, str) or not tname:
                        raise ConfigError(f"vehicles.models.{model_key}.generations.trims.name must be a non-empty string")
                    tsyns = t.get('synonyms', [])
                    if not isinstance(tsyns, list) or not all(isinstance(s, str) for s in tsyns):
                        raise ConfigError(f"vehicles.models.{model_key}.generations.trims.synonyms must be list of strings")

def _validate_options_per_generation(opg: Dict[str, Any]) -> None:
    """Validate options_per_generation section"""
    if not opg:
        return
    if not isinstance(opg, dict):
        raise ConfigError("'options_per_generation' must be a table (dict)")
    # Defaults
    defaults = opg.get('defaults', {})
    if defaults:
        if not isinstance(defaults, dict):
            raise ConfigError("options_per_generation.defaults must be a table")
        top = defaults.get('top_options', [])
        if not isinstance(top, list) or not all(isinstance(s, str) for s in top):
            raise ConfigError("options_per_generation.defaults.top_options must be a list of strings")
    # Per-model entries
    for model_key, model_map in opg.items():
        if model_key == 'defaults':
            continue
        if not isinstance(model_map, dict):
            raise ConfigError(f"options_per_generation.{model_key} must be a table")
        # Each key under model is a generation code mapping to { msrp = { id = int } }
        for gen_code, gen_map in model_map.items():
            if not isinstance(gen_map, dict):
                raise ConfigError(f"options_per_generation.{model_key}.{gen_code} must be a table")
            msrp = gen_map.get('msrp', {})
            if not isinstance(msrp, dict):
                raise ConfigError(f"options_per_generation.{model_key}.{gen_code}.msrp must be a table")
            for opt_id, val in msrp.items():
                if not isinstance(opt_id, str):
                    raise ConfigError(f"Option id in MSRP map must be a string (model {model_key} gen {gen_code})")
                if not isinstance(val, int) or val < 0:
                    raise ConfigError(f"Option MSRP for '{opt_id}' must be a non-negative integer (model {model_key} gen {gen_code})")

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
