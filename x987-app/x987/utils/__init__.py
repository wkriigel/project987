"""
Utility modules for View-from-CSV

PROVIDES: Common utilities for logging, I/O, and text processing
DEPENDS: Standard library only
CONSUMED BY: All other modules (pipeline, CLI, extractors, etc.)
CONTRACT: Provides reusable utility functions with clear interfaces
TECH CHOICE: Standard library with clear interfaces
RISK: Low - utility functions are generally safe
"""

from .log import setup_logging, get_logger, ProgressLogger
from .io import read_csv, write_csv, append_csv, read_json, write_json
from .text import clean_text, extract_number, extract_price, extract_mileage

__all__ = [
    "setup_logging",
    "get_logger", 
    "ProgressLogger",
    "read_csv",
    "write_csv",
    "append_csv",
    "read_json",
    "write_json",
    "clean_text",
    "extract_number",
    "extract_price",
    "extract_mileage"
]
