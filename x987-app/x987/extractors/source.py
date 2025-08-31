"""
Source Extractor - Extracts vehicle listing source from URLs or text

This file contains everything needed to extract the vehicle source.
It's completely self-contained and can be modified independently.
"""

import re
from typing import List, Any
from urllib.parse import urlparse
from .base import BaseExtractor, ExtractionResult


class SourceExtractor(BaseExtractor):
    """Source extraction from URLs or text"""
    
    def get_field_name(self) -> str:
        return "source"
    
    def get_patterns(self) -> List[str]:
        return [
            r'https?://(?:www\.)?([a-zA-Z0-9\-]+)\.com',  # cars.com, truecar.com
            r'https?://(?:www\.)?([a-zA-Z0-9\-]+)\.net',  # autotempest.net
            r'https?://(?:www\.)?([a-zA-Z0-9\-]+)\.org',  # pca.org
            r'Source\s*:?\s*([A-Za-z0-9\-\s]+)',  # Source: Cars.com
            r'From\s*:?\s*([A-Za-z0-9\-\s]+)',  # From: TrueCar
            r'Listed\s+on\s+([A-Za-z0-9\-\s]+)',  # Listed on Carvana
        ]
    
    def _process_match(self, match: re.Match, **kwargs) -> Any:
        """Process source match to return cleaned source string"""
        try:
            source = match.group(1).strip()
            # Clean up the source value
            cleaned_source = self._clean_source(source)
            if cleaned_source:
                return cleaned_source
        except (ValueError, AttributeError):
            pass
        return None
    
    def _clean_source(self, source: str) -> str:
        """Clean and validate source values"""
        if not source:
            return None
        
        s = str(source).strip()
        if len(s) <= 1:
            return None
        
        # Remove common prefixes/suffixes
        s = re.sub(r'^(Source|From|Listed\s+on)\s*:?\s*', '', s, flags=re.IGNORECASE)
        s = s.strip()
        
        return s if len(s) > 1 else None
    
    def extract_from_url(self, url: str) -> str:
        """Extract source from URL"""
        if not url:
            return "unknown"
        
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname.lower()
            
            # Map common hostnames to friendly names
            source_mapping = {
                'cars.com': 'Cars.com',
                'truecar.com': 'TrueCar',
                'carvana.com': 'Carvana',
                'autotempest.com': 'AutoTempest',
                'autotempest.net': 'AutoTempest',
                'pca.org': 'PCA',
                'porsche.com': 'Porsche',
                'cargurus.com': 'CarGurus',
                'autotrader.com': 'AutoTrader',
                'carsdirect.com': 'CarsDirect',
                'edmunds.com': 'Edmunds',
                'kbb.com': 'KBB',
                'nada.com': 'NADA',
                'hemmings.com': 'Hemmings',
                'bringatrailer.com': 'Bring a Trailer',
                'carsandbids.com': 'Cars & Bids',
            }
            
            # Check for exact matches first
            if hostname in source_mapping:
                return source_mapping[hostname]
            
            # Check for partial matches
            for key, value in source_mapping.items():
                if key in hostname:
                    return value
            
            # If no match found, return the hostname
            return hostname.replace('www.', '').title()
            
        except Exception:
            return "unknown"
    
    def extract_from_text(self, text: str) -> str:
        """Extract source from text using patterns"""
        result = self.extract(text)
        if result and result.value:
            return result.value
        return "unknown"


# Export the extractor instance
SOURCE_EXTRACTOR = SourceExtractor()
