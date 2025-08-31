"""
View-from-CSV: Vehicle Data Extraction and Analysis Pipeline

PROVIDES: Main package initialization and public API exports
DEPENDS: All submodules (cli, pipeline, view, utils, config, extractors, options, scrapers)
CONSUMED BY: External applications and scripts
CONTRACT: Exports core functionality and maintains version info
TECH CHOICE: Clean package structure with explicit __all__ declarations
RISK: Low - well-defined public API with minimal coupling

A comprehensive system for collecting, scraping, transforming, and analyzing
vehicle listing data from multiple sources with a focus on Porsche 987.2 models.

Key Features:
- Modular pipeline architecture with clear separation of concerns
- Universal scraping system with site-specific profiles
- Intelligent data transformation and validation
- Comprehensive options detection and analysis
- Clean, maintainable codebase following single-purpose principles

Configuration is managed through TOML files with environment variable overrides.
See `ARCHITECTURE.md` for detailed configuration options.
"""

__version__ = "4.5.0"
__author__ = "View-from-CSV Team"

# Core public API - organized by functionality
from .cli import main
from .pipeline import (
    get_pipeline_runner,
    get_registry
)
from .view import (
    THEME,
    theme_style,
    price_style_key,
    miles_style_key
)
from .utils import (
    setup_logging,
    get_logger
)
from .config import get_config, get_timestamp_run_id

__all__ = [
    # Core functionality
    "main",
    
    # Pipeline operations
    "get_pipeline_runner",
    "get_registry", 
    
    # View and display
    "THEME",
    "theme_style",
    "price_style_key",
    "miles_style_key",
    
    # Utilities
    "setup_logging",
    "get_logger",
    
    # Configuration
    "get_config",
    "get_timestamp_run_id"
]

# Version info
def get_version_info():
    """Get detailed version information"""
    return {
        "version": __version__,
        "author": __author__,
        "architecture": "v4.5 (Clean Architecture)",
        "modules": {
            "cli": "Organized CLI package",
            "pipeline": "Modular data processing pipeline",
            "scrapers": "Universal scraping with site profiles",
            "view": "Modular data visualization",
            "config": "Centralized configuration management",
            "utils": "Common utility functions"
        }
    }
