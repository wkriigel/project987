"""
Extractors Package - Modular data extraction system

PROVIDES: Modular data extraction system with field-specific extractors
DEPENDS: Base extractor classes and registry system
CONSUMED BY: x987.pipeline.steps.transformation:TransformationStep and scraping modules
CONTRACT: Provides standardized data extraction from HTML content with confidence scoring
TECH CHOICE: Single-purpose modules with registry-based discovery
RISK: Medium - extractors must handle varying HTML structures, patterns may become outdated

Each field has its own file with extraction logic.
The ExtractorsRegistry automatically discovers all extractor definitions.
"""

from .base import BaseExtractor, ExtractionResult

# Import registry after base classes are defined
# This avoids circular import issues
__all__ = [
    'BaseExtractor',
    'ExtractionResult',
]

# Lazy import to avoid circular dependencies
def get_registry():
    from .registry import EXTRACTORS_REGISTRY
    return EXTRACTORS_REGISTRY

def get_unified_extractor():
    from .unified import UNIFIED_EXTRACTOR
    return UNIFIED_EXTRACTOR
