"""
Base classes for the modular options system

PROVIDES: Abstract base classes and data structures for option detection
DEPENDS: Standard library (re, abc, dataclasses, typing)
CONSUMED BY: All option-specific implementations
CONTRACT: Defines interface and common functionality for option detection
TECH CHOICE: ABC with dataclasses for clean, type-safe design
RISK: Low - base classes provide stable foundation

"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Pattern


@dataclass
class OptionDefinition:
    """Definition of a car option with detection patterns and value"""
    id: str
    display: str
    value_usd: int
    patterns: List[str]
    standard_on_trims: List[str] = None
    category: str = "performance"
    
    def __post_init__(self):
        if self.standard_on_trims is None:
            self.standard_on_trims = []


class BaseOption(ABC):
    """Abstract base class for individual option implementations"""
    
    def __init__(self):
        self.definition = self.get_definition()
        self.compiled_patterns = self._compile_patterns()
    
    @abstractmethod
    def get_definition(self) -> OptionDefinition:
        """Return the option definition"""
        pass
    
    def _compile_patterns(self) -> List[Pattern]:
        """Compile regex patterns for efficient matching"""
        compiled = []
        for pattern in self.definition.patterns:
            try:
                compiled.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                # Skip invalid patterns
                continue
        return compiled
    
    def is_present(self, text: str, trim: str = None) -> bool:
        """Check if this option is present in the given text"""
        if not text:
            return False
        
        # Check if option is standard on this trim (don't count it)
        if trim and self.definition.standard_on_trims:
            if any(trim.lower() == std.lower() for std in self.definition.standard_on_trims):
                return False
        
        # Use compiled regex patterns
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        
        return False
    
    def get_value(self, text: str, trim: str = None) -> int:
        """Get the value of this option if present"""
        return self.definition.value_usd if self.is_present(text, trim) else 0
    
    def get_display(self) -> str:
        """Get the display name of this option"""
        return self.definition.display
    
    def get_category(self) -> str:
        """Get the category of this option"""
        return self.definition.category
