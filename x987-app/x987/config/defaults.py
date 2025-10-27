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
    "storage": {
        # Storage backend: 'sqlite' (preferred) or 'files' (legacy)
        "mode": "sqlite",
        # Default DB path; resolved relative to project root data dir
        "db_path": "x987-data/x987.db",
        "retention": {
            # Keep at most N recent successful scrapes per listing (None = unlimited)
            "scrapes_max_per_listing": 5,
            # If true, failed scrapes do not count against the per-listing limit
            "keep_failed": True
        }
    },
    "search": {
        "urls": [
            #"https://www.autotempest.com/results?localization=country&make=porsche&maxyear=2012&minyear=2009&model=cayman&transmission=auto&zip=30214",
            "https://www.autotempest.com/results?localization=country&make=porsche&maxyear=2012&minyear=2009&model=cayman&transmission=auto&zip=30214"
        ]
    },
    "scraping": {
        "concurrency": 2,
        "polite_delay_ms": 1000,
        "cap_listings": 150,
        "debug": True,
        "headful": True,  # Use headful mode for browser automation
        "timeout_seconds": 30
    },
    "options": {
        "enabled": True,
        "confidence_threshold": 0.7,
        "max_options_display": 100  # Show all options, no "+n more"
    },
    "pipeline": {
        "output_directory": "x987-data/results",
        # Export CSV files (collection/scraping/transformed/deduped/ranking)
        "export_csv": True,
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
