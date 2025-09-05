"""
18–19" Upgraded Wheels Option

This file contains everything needed to detect the Upgraded Wheels option.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List


class UpgradedWheelsOption:
    """Upgraded Wheels option detection and definition"""
    
    def __init__(self):
        # Option metadata
        self.id = "Wheels"
        self.display = "18–19\" Upgraded Wheels"
        self.value_usd = 400
        self.category = "exterior"
        
        # Detection patterns - all variations that indicate this option
        self.patterns = [
            r"\b19\s*inch\b",
            r"\b19\s*\"\b",
            r"\b19\s*x\s*\d+\s*inch\b",
            r"\b19\s*x\s*\d+\s*\"\b",
            r"\b18\s*inch\b",
            r"\b18\s*\"\b",
            r"\b18\s*x\s*\d+\s*inch\b",
            r"\b18\s*x\s*\d+\s*\"\b",
            # Model phrasing e.g., "18 Cayman S Wheels"
            r"\b18\s*(?:in(?:ch(?:es)?)?|\")?\s*(?:Cayman|Boxster)\s*S?\s*wheels\b",
            # Generic inch forms with wheels
            r"\b1[89]\s*(?:in(?:ch(?:es)?)?|\")\s*wheels\b",
            r"\balloy\s+wheels\b",
            r"\bupgraded\s+wheels\b",
            r"\bpremium\s+wheels\b",
            r"\bsport\s+wheels\b",
            r"\b19\s*inch\s+alloy\s+wheels\b",
            r"\b18\s*inch\s+alloy\s+wheels\b",
            # Common wheel codes (911)
            r"\b404\b",
            r"\b405\b",
            r"\b446\b"
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
        Check if Upgraded Wheels are present in the given text
        
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
        Get the value of Upgraded Wheels if present
        
        Args:
            text: Raw text to search for the option
            trim: Vehicle trim (not used for this option)
            
        Returns:
            Option value ($400) if present, 0 if not present
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
UPGRADED_WHEELS_OPTION = UpgradedWheelsOption()
