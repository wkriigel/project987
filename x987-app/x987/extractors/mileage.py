"""
Mileage Extractor - Extracts vehicle mileage from text

This file contains everything needed to extract the vehicle mileage.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List, Any
from .base import BaseExtractor, ExtractionResult


class MileageExtractor(BaseExtractor):
    """Mileage extraction from vehicle text"""
    
    def get_field_name(self) -> str:
        return "mileage"
    
    def get_patterns(self) -> List[str]:
        return [
            # Plain digits with unit (commas optional)
            r'(\d{1,6}(?:,\d{3})*)\s*(?:miles?|mi)\b',  # 103617 miles / 103,720 miles / 103617 mi
            # Labelled mileage (colon optional)
            r'Mileage\s*:?\s*(\d{1,6}(?:,\d{3})*)',  # Mileage 103617 / Mileage: 103,720
            r'(\d{1,3}(?:,\d{3})*)\s*k\s*miles?\b',  # 30.5k miles
            r'(\d{1,3}(?:,\d{3})*)\s*k\s*mi\b',  # 30.5k mi
            r'(\d{1,3}(?:,\d{3})*)\s*K\b',  # 30.5K
            r'(\d{1,3}(?:,\d{3})*)\s*km\b',  # 30,500 km (convert to miles)
        ]
    
    def _process_match(self, match: re.Match, **kwargs) -> Any:
        """Process mileage match to return integer"""
        try:
            mileage_str = match.group(1)
            # Remove commas and convert to integer
            mileage_int = int(mileage_str.replace(",", ""))
            
            # Check if it's in kilometers (km) and convert to miles
            raw_text = match.group(0).lower()
            if 'km' in raw_text:
                mileage_int = int(mileage_int * 0.621371)  # Convert km to miles
            
            # Validate reasonable mileage range (0 - 500,000 miles)
            if 0 <= mileage_int <= 500000:
                return mileage_int
        except (ValueError, AttributeError):
            pass
        return None


# Export the extractor instance
MILEAGE_EXTRACTOR = MileageExtractor()
