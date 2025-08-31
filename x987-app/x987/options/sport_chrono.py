"""
Sport Chrono Package Plus Option

This file contains everything needed to detect the Sport Chrono Package Plus option.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List, Tuple


class SportChronoOption:
    """Sport Chrono Package Plus option detection and definition"""
    
    def __init__(self):
        # Option metadata
        self.id = "639/640"
        self.display = "Sport Chrono Package Plus"
        self.value_usd = 1000
        self.category = "performance"
        
        # Detection patterns - all variations that indicate this option
        self.patterns = [
            r"\bsport\s+chrono\b",
            r"\bchrono\s+package\b", 
            r"\bchrono\s+plus\b",
            r"\bsport\s+chrono\s+plus\b",
            r"\bchrono\s+package\s+plus\b",
            r"\bsport\s+chrono\s+package\b",
            r"\bchrono\b",
            r"\bsport\s+chrono\s+package\s+plus\b"
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
        Check if Sport Chrono Package Plus is present in the given text
        
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
        Get the value of Sport Chrono Package Plus if present
        
        Args:
            text: Raw text to search for the option
            trim: Vehicle trim (not used for this option)
            
        Returns:
            Option value ($1000) if present, 0 if not present
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
SPORT_CHRONO_OPTION = SportChronoOption()
