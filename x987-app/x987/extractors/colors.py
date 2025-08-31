"""
Colors Extractor - Extracts vehicle exterior and interior colors from text

PROVIDES: Color extraction for exterior and interior vehicle colors
DEPENDS: Base extractor class and regex patterns
CONSUMED BY: Registry and unified extractor modules
CONTRACT: Extracts and cleans color information from vehicle text
TECH CHOICE: Regex patterns with fallback color detection
RISK: Medium - color patterns may vary across different sites

This file contains everything needed to extract the vehicle colors.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List, Any, Tuple
from .base import BaseExtractor, ExtractionResult


class ColorsExtractor(BaseExtractor):
    """Color extraction from vehicle text"""
    
    def get_field_name(self) -> str:
        return "colors"
    
    def get_patterns(self) -> List[str]:
        # Limit captures to a single line to avoid pulling in subsequent labels
        # e.g., "Exterior color\nBlack\nInterior color..." should capture only "Black"
        return [
            r'Exterior\s*color\s*:?[ \t]*([^\r\n]+)',  # Exterior color: Arctic Silver
            r'Interior\s*color\s*:?[ \t]*([^\r\n]+)',  # Interior color: Black
            r'Color\s*:?[ \t]*([^\r\n]+)',              # Color: White
            r'Paint\s*:?[ \t]*([^\r\n]+)',              # Paint: Guards Red
            r'Upholstery\s*:?[ \t]*([^\r\n]+)',         # Upholstery: Beige
            r'Seats\s*:?[ \t]*([^\r\n]+)',              # Seats: Tan
        ]
    
    def _process_match(self, match: re.Match, **kwargs) -> Any:
        """Process color match to return cleaned color string"""
        try:
            color = match.group(1).strip()
            # Clean up the color value
            cleaned_color = self._clean_color(color)
            if cleaned_color:
                return cleaned_color
        except (ValueError, AttributeError):
            pass
        return None
    
    def _clean_color(self, color: str) -> str:
        """Clean and validate color values"""
        if not color:
            return None
        
        s = str(color).strip()
        # Keep only the first segment up to a newline or double space separation
        s = re.split(r'[\r\n]|\s{2,}', s)[0].strip()
        if len(s) <= 2:
            return None
        
        # Remove common prefixes/suffixes
        s = re.sub(r'^(Color|Paint|Upholstery|Seats)\s*:?\s*', '', s, flags=re.IGNORECASE)
        # Remove material descriptors for interior to standardize display
        s = re.sub(r'\bLeather\b', '', s, flags=re.IGNORECASE)
        s = s.strip()
        
        return s if len(s) > 2 else None
    
    def extract_colors(self, text: str) -> Tuple[str, str]:
        """Extract both exterior and interior colors"""
        exterior_color = None
        interior_color = None
        
        # Look for labeled color patterns
        ext_match = re.search(r'Exterior\s*color\s*:?\s*([A-Za-z\s\-]+)', text, re.I)
        int_match = re.search(r'Interior\s*color\s*:?\s*([A-Za-z\s\-]+)', text, re.I)
        
        if ext_match:
            exterior_color = self._clean_color(ext_match.group(1))
        if int_match:
            interior_color = self._clean_color(int_match.group(1))
        
        # Fallback: look for unlabeled colors
        if not exterior_color:
            # Look for common exterior color patterns
            ext_patterns = [
                r'\b(White|Black|Gray|Silver|Red|Blue|Green|Yellow|Orange|Purple|Brown|Tan|Beige|Gold|Pink)\b',
                r'\b(Arctic\s+Silver|Guards\s+Red|Miami\s+Blue|Racing\s+Yellow|GT\s+Silver|Basalt\s+Black)\b'
            ]
            for pattern in ext_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    exterior_color = self._clean_color(match.group(1))
                    break
        
        if not interior_color:
            # Look for common interior color patterns
            int_patterns = [
                r'\b(Black|Beige|Tan|Brown|Gray|White|Red|Blue|Green|Yellow|Orange|Purple|Pink|Gold)\b',
                r'\b(Black\s+Leather|Beige\s+Leather|Tan\s+Leather|Brown\s+Leather)\b'
            ]
            for pattern in int_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    interior_color = self._clean_color(match.group(1))
                    break
        
        return exterior_color, interior_color


# Export the extractor instance
COLORS_EXTRACTOR = ColorsExtractor()
