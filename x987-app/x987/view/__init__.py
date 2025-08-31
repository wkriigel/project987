"""
View and display modules for View-from-CSV

PROVIDES: Data visualization and report generation
DEPENDS: Core modules and rich library
CONSUMED BY: x987.cli.main:main function and main application
CONTRACT: Provides formatted output and reports with Rich library styling
TECH CHOICE: Rich library for terminal formatting
RISK: Low - display changes don't affect data
"""

# Core view modules
from .theme import THEME, theme_style, price_style_key, miles_style_key

__all__ = [
    # Core view
    "THEME",
    "theme_style", 
    "price_style_key",
    "miles_style_key",
    # Modular view removed
]
