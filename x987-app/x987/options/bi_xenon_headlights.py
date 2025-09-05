"""
Bi-Xenon Headlights with Dynamic Cornering Option

This file contains everything needed to detect the Bi-Xenon Headlights option.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List


class BiXenonHeadlightsOption:
    """Bi-Xenon Headlights option detection and definition"""
    
    def __init__(self):
        # Option metadata
        self.id = "Bi-Xenon"
        self.display = "Bi-Xenon Headlights with Dynamic Cornering"
        self.value_usd = 250
        self.category = "exterior"
        
        # Detection patterns - all variations that indicate this option
        self.patterns = [
            r"\bbi[-\s]?xenon\b",
            r"\bxenon\s+headlights\b",
            r"\bxenon\s+lighting\b",
            r"\bprojector\s+beam\s+headlights\b",
            r"\bprojector\s+headlights\b",
            r"\bdynamic\s+cornering\s+lights\b",
            r"\bcornering\s+lights\b",
            r"\badaptive\s+headlights\b",
            r"\badaptive\s+lighting\b",
            r"\b601\b",
            r"\bpdls\b",
            r"\b8ju\b",
            r"\b8is\b"
        ]
        
        # Compile patterns for efficient matching
        self.compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for efficient matching"""
        compiled = []
        for pattern in self.patterns:
            try:
                compiled.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                # Skip invalid patterns
                continue
        return compiled
    
    def is_present(self, text: str, trim: str = None) -> bool:
        """
        Check if Bi-Xenon Headlights are present in the given text
        
        Args:
            text: Raw text to search for the option
            trim: Vehicle trim (e.g., "S", "R") - not used for this option
            
        Returns:
            True if the option is detected, False otherwise
        """
        if not text:
            return False
        
        # Check each compiled pattern
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        
        return False
    
    def get_value(self, text: str, trim: str = None) -> int:
        """
        Get the value of Bi-Xenon Headlights if present
        
        Args:
            text: Raw text to search for the option
            trim: Vehicle trim (not used for this option)
            
        Returns:
            Option value ($250) if present, 0 if not present
        """
        return self.value_usd if self.is_present(text, trim) else 0
    
    def get_display(self) -> str:
        """Get the display name for this option"""
        return self.display
    
    def get_category(self) -> str:
        """Get the category for this option"""
        return self.category
    
    def get_id(self) -> str:
        """Get the ID for this option"""
        return self.id


# Export the option instance
BI_XENON_HEADLIGHTS_OPTION = BiXenonHeadlightsOption()
