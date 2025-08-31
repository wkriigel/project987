"""
Park Assist Option

This file contains everything needed to detect the Park Assist option.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List


class ParkAssistOption:
    """Park Assist option detection and definition"""
    
    def __init__(self):
        # Option metadata
        self.id = "Park Assist"
        self.display = "Park Assist"
        self.value_usd = 200
        self.category = "convenience"
        
        # Detection patterns - all variations that indicate this option
        self.patterns = [
            r"\bpark\s+assist\b",
            r"\bparking\s+assist\b",
            r"\bparking\s+aid\b",
            r"\bparking\s+sensors\b",
            r"\brear\s+parking\s+sensors\b",
            r"\bfront\s+parking\s+sensors\b"
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
        Check if Park Assist is present in the given text
        
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
        Get the value of Park Assist if present
        
        Args:
            text: Raw text to search for the option
            trim: Vehicle trim (not used for this option)
            
        Returns:
            Option value ($200) if present, 0 if not present
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
PARK_ASSIST_OPTION = ParkAssistOption()
