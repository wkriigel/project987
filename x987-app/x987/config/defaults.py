"""
Default configuration values for View-from-CSV

PROVIDES: Default configuration settings
DEPENDS: None
CONSUMED BY: Configuration manager
CONTRACT: Provides sensible defaults for all configuration options
TECH CHOICE: Python dictionary for easy modification
RISK: Low - defaults can be overridden by user config
"""

# Default configuration values
DEFAULT_CONFIG = {
    "pricing_mode": "msrp_only",  # pricing modes: 'msrp_only' | 'current'
    "search": {
        "urls": [
            #"https://www.autotempest.com/results?localization=country&make=porsche&maxyear=2012&minyear=2009&model=cayman&transmission=auto&zip=30214",
            "https://www.autotempest.com/results?localization=country&make=porsche&maxyear=2012&minyear=2009&model=cayman&transmission=auto&zip=30214"
        ]
    },
    "fair_value": {
        "base_value_usd": 30500,
        "year_step_usd": 500,
        "s_premium_usd": 7000,
        "exterior_color_usd": 300,
        "interior_color_usd": 300,
        "special_trim_premiums": {
            "Cayman R": 30000,
            "Boxster Spyder": 30000,
            "Black Edition": 1500
        }
    },
    "scraping": {
        "concurrency": 2,
        "polite_delay_ms": 1000,
        "cap_listings": 150,
        "debug": True,
        "headful": True,  # Use headful mode for browser automation
        "timeout_seconds": 30
    },
    "options_v2": {
        "enabled": True,
        "confidence_threshold": 0.7,
        "max_options_display": 100  # Show all options, no "+n more"
    },
    "pipeline": {
        "output_directory": "x987-data/results",
        "create_separate_files": True,  # Create separate files for each property/option
        "raw_csv_name": "raw_extracted_data.csv",
        "transformed_csv_name": "transformed_data.csv",
        "options_csv_name": "extracted_options.csv"
    },
    "view": {
        "theme": "default",
        "show_progress": True,
        "detailed_output": True,
        "color_output": True
    }
}
