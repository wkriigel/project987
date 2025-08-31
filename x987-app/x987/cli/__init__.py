"""
Command Line Interface package for View-from-CSV

PROVIDES: Organized CLI modules and command handling
DEPENDS: Core modules and utilities
CONSUMED BY: End users and x987.__main__:main function
CONTRACT: Provides user-friendly command interface with pipeline orchestration
TECH CHOICE: Modular CLI with clear separation of concerns
RISK: Low - CLI interface is straightforward
"""

from .main import (
    main,
    cmd_doctor,
    cmd_collect,
    cmd_scrape,
    cmd_transform,
    cmd_dedupe,
    cmd_fair_value,
    cmd_rank,
    cmd_pipeline,
    cmd_info,
    cmd_config
)
from .utils import with_timeout, TimeoutError

__all__ = [
    "main",
    "cmd_doctor",
    "cmd_collect",
    "cmd_scrape",
    "cmd_transform",
    "cmd_dedupe",
    "cmd_fair_value",
    "cmd_rank",
    "cmd_pipeline",
    "cmd_info",
    "cmd_config",
    "with_timeout",
    "TimeoutError"
]
