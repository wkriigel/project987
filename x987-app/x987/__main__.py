"""
Main entry point for View-from-CSV package

PROVIDES: Package execution entry point
DEPENDS: x987.cli.main:main function
CONSUMED BY: Python -m x987 command
CONTRACT: Executes main CLI function
TECH CHOICE: Standard Python package execution pattern
RISK: Low - simple entry point
"""

from .cli import main

if __name__ == "__main__":
    main()
