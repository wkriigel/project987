"""
Year Extractor - Extracts vehicle year from text

This file contains everything needed to extract the vehicle year.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List, Any
from .base import BaseExtractor, ExtractionResult


class YearExtractor(BaseExtractor):
    """Year extraction from vehicle text"""
    
    def get_field_name(self) -> str:
        return "year"
    
    def get_patterns(self) -> List[str]:
        return [
            r'\b(19[9][0-9]|20[0-2][0-9])\b',  # 1990-2029
            r'Year\s*:?\s*(\d{4})',  # Year: 2010
            r'(\d{4})\s*Porsche',  # 2010 Porsche
            r'Porsche\s*(\d{4})',  # Porsche 2010
        ]
    
    def _process_match(self, match: re.Match, **kwargs) -> Any:
        """Process year match to return integer"""
        try:
            year_str = match.group(1)
            year_int = int(year_str)
            # Validate reasonable year range
            if 1990 <= year_int <= 2029:
                return year_int
        except (ValueError, AttributeError):
            pass
        return None


# Export the extractor instance
YEAR_EXTRACTOR = YearExtractor()
