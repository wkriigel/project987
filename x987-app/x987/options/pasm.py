"""
PASM (Porsche Active Suspension Management) Option

This file contains everything needed to detect the PASM option.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List


class PASMOption:
    """PASM option detection and definition"""
    
    def __init__(self):
        # Option metadata
        self.id = "PASM"
        self.display = "PASM"
        self.value_usd = 800
        self.category = "performance"
        
        # Detection patterns - all variations that indicate this option
        self.patterns = [
            r"\bpasm\b",
            r"\badaptive\s+suspension\b",
            r"\bactive\s+suspension\b",
            r"\badaptive\s+damping\b",
            r"\bporsche\s+active\s+suspension\s+management\b",
            r"\badaptive\s+sport\s+suspension\b",
            r"\bsport\s+suspension\b"
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
        Check if PASM is present in the given text
        
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
        Get the value of PASM if present
        
        Args:
            text: Raw text to search for the option
            trim: Vehicle trim (not used for this option)
            
        Returns:
            Option value ($800) if present, 0 if not present
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
PASM_OPTION = PASMOption()
