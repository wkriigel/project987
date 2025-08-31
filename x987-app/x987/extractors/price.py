"""
Price Extractor - Extracts vehicle price from text

PROVIDES: Price extraction and validation for vehicle listings
DEPENDS: Base extractor class and regex patterns
CONSUMED BY: Registry and unified extractor modules
CONTRACT: Extracts and validates price information from vehicle text
TECH CHOICE: Regex patterns with price range validation
RISK: Low - price patterns are relatively consistent across sites

This file contains everything needed to extract the vehicle price.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List, Any
from .base import BaseExtractor, ExtractionResult


class PriceExtractor(BaseExtractor):
    """Price extraction from vehicle text"""
    
    def get_field_name(self) -> str:
        return "price_usd"
    
    def get_patterns(self) -> List[str]:
        return [
            r'\$(\d{1,3}(?:,\d{3})*)',  # $30,500
            r'Price\s*:?\s*\$?(\d{1,3}(?:,\d{3})*)',  # Price: $30,500
            r'Asking\s*:?\s*\$?(\d{1,3}(?:,\d{3})*)',  # Asking: $30,500
            r'Listed\s*:?\s*\$?(\d{1,3}(?:,\d{3})*)',  # Listed: $30,500
            r'(\d{1,3}(?:,\d{3})*)\s*USD',  # 30,500 USD
            r'(\d{1,3}(?:,\d{3})*)\s*dollars',  # 30,500 dollars
        ]
    
    def _process_match(self, match: re.Match, **kwargs) -> Any:
        """Process price match to return integer"""
        try:
            price_str = match.group(1)
            # Remove commas and convert to integer
            price_int = int(price_str.replace(",", ""))
            # Validate reasonable price range ($1,000 - $500,000)
            if 1000 <= price_int <= 500000:
                return price_int
        except (ValueError, AttributeError):
            pass
        return None


# Export the extractor instance
PRICE_EXTRACTOR = PriceExtractor()
