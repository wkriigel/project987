"""
Heated Seats Option

This file contains everything needed to detect the Heated Seats option.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List


class HeatedSeatsOption:
    """Heated Seats option detection and definition"""
    
    def __init__(self):
        # Option metadata
        self.id = "Heated Seats"
        self.display = "Heated Seats"
        self.value_usd = 150
        self.category = "seating"
        
        # Detection patterns - all variations that indicate this option
        self.patterns = [
            r"\bheated\s+seats\b",
            r"\bseat\s+heating\b",
            r"\bheated\s+front\s+seats\b",
            r"\bheated\s+driver\s+seat\b",
            r"\bheated\s+passenger\s+seat\b",
            r"\b342\b",
            r"\b4a3\b"
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
        Check if Heated Seats are present in the given text
        
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
        Get the value of Heated Seats if present
        
        Args:
            text: Raw text to search for the option
            trim: Vehicle trim (not used for this option)
            
        Returns:
            Option value ($150) if present, 0 if not present
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
HEATED_SEATS_OPTION = HeatedSeatsOption()
