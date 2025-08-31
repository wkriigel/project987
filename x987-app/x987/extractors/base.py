"""
Base classes for the modular extraction system

PROVIDES: Abstract base classes and data structures for field extractors
DEPENDS: Standard library (re, abc, dataclasses, typing)
CONSUMED BY: All field-specific extractor implementations
CONTRACT: Defines interface and common functionality for extractors
TECH CHOICE: ABC with dataclasses for clean, type-safe design
RISK: Low - base classes provide stable foundation
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Pattern, Any


@dataclass
class ExtractionResult:
    """Result of a data extraction operation"""
    value: Any
    confidence: float = 1.0
    source_pattern: Optional[str] = None
    raw_match: Optional[str] = None


class BaseExtractor(ABC):
    """Abstract base class for individual field extractors"""
    
    def __init__(self):
        self.compiled_patterns = self._compile_patterns()
    
    @abstractmethod
    def get_field_name(self) -> str:
        """Return the field name this extractor handles"""
        pass
    
    @abstractmethod
    def get_patterns(self) -> List[str]:
        """Return the regex patterns for extraction"""
        pass
    
    def _compile_patterns(self) -> List[Pattern]:
        """Compile regex patterns for efficient matching"""
        compiled = []
        for pattern in self.get_patterns():
            try:
                compiled.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                # Skip invalid patterns
                continue
        return compiled
    
    def extract(self, text: str, **kwargs) -> Optional[ExtractionResult]:
        """Extract data from text using compiled patterns"""
        if not text:
            return None
        
        # Use compiled regex patterns
        for i, pattern in enumerate(self.compiled_patterns):
            match = pattern.search(text)
            if match:
                raw_match = match.group(0)
                value = self._process_match(match, **kwargs)
                if value is not None:
                    return ExtractionResult(
                        value=value,
                        confidence=1.0,
                        source_pattern=self.get_patterns()[i],
                        raw_match=raw_match
                    )
        
        return None
    
    def _process_match(self, match: re.Match, **kwargs) -> Any:
        """Process a regex match to extract the actual value"""
        # Default implementation - return first group
        # Override in subclasses for custom processing
        try:
            return match.group(1)
        except (IndexError, AttributeError):
            return None
    
    def get_field_name(self) -> str:
        """Get the field name this extractor handles"""
        return self.get_field_name()
