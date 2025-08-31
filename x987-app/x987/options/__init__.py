"""
Options Package - Modular car options detection system

PROVIDES: Modular system for detecting vehicle options and features
DEPENDS: Base option classes and detector system
CONSUMED BY: x987.pipeline.steps.transformation:TransformationStep and analysis modules
CONTRACT: Provides standardized option detection from vehicle descriptions with value estimation
TECH CHOICE: Single-purpose modules with pattern-based detection
RISK: Medium - option patterns may change across sites and models, value estimates may be inaccurate

Each option has its own file with pattern matching logic.
The OptionsDetector aggregates all option definitions.
"""

from .base import OptionDefinition, BaseOption
from .detector import OptionsDetector
from .registry import OptionsRegistry, OPTIONS_REGISTRY

__all__ = [
    'OptionDefinition',
    'BaseOption', 
    'OptionsDetector',
    'OptionsRegistry',
    'OPTIONS_REGISTRY',
    'get_registry'
]

def get_registry():
    """Get the global options registry instance"""
    return OPTIONS_REGISTRY
