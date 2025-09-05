"""
Unified Extractor - Provides the same interface as current extraction functions

This file provides backward compatibility while using the new modular extraction system.
It can be used as a drop-in replacement for the current transform.py extraction functions.
"""

from typing import Optional, Tuple, Dict, Any
from .registry import EXTRACTORS_REGISTRY


class UnifiedExtractor:
    """Unified interface for all field extraction operations"""
    
    def __init__(self):
        self.registry = EXTRACTORS_REGISTRY
    
    def extract_year(self, text: str) -> Optional[int]:
        """Extract year from text (backward compatibility)"""
        result = self.registry.extract_field("year", text)
        return result.value if result else None
    
    def extract_price(self, text: str) -> Optional[int]:
        """Extract price from text (backward compatibility)"""
        result = self.registry.extract_field("price_usd", text)
        return result.value if result else None
    
    def extract_mileage(self, text: str) -> Optional[int]:
        """Extract mileage from text (backward compatibility)"""
        result = self.registry.extract_field("mileage", text)
        return result.value if result else None
    
    def extract_model_trim(self, text: str) -> Tuple[str, str]:
        """Extract model and trim from text (backward compatibility)"""
        result = self.registry.extract_field("model_trim", text)
        if result and result.value:
            # Use the extractor's method to get separate values
            extractor = self.registry.get_extractor_by_field("model_trim")
            if hasattr(extractor, 'extract_separate'):
                return extractor.extract_separate(text)
        
        return "Unknown", "Base"
    
    def extract_colors(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract colors from text (backward compatibility)"""
        extractor = self.registry.get_extractor_by_field("colors")
        if extractor and hasattr(extractor, 'extract_colors'):
            return extractor.extract_colors(text)
        
        return None, None
    
    def extract_source(self, text: str, url: str = None) -> str:
        """Extract source from text or URL (backward compatibility)"""
        extractor = self.registry.get_extractor_by_field("source")
        if extractor:
            if url:
                return extractor.extract_from_url(url)
            else:
                return extractor.extract_from_text(text)
        
        return "unknown"
    
    
    def extract_all(self, text: str, url: str = None) -> Dict[str, Any]:
        """Extract all available fields from text"""
        results = {}
        
        # Extract basic fields
        results['year'] = self.extract_year(text)
        results['price_usd'] = self.extract_price(text)
        results['mileage'] = self.extract_mileage(text)
        results['model'], results['trim'] = self.extract_model_trim(text)
        ext, intr = self.extract_colors(text)
        results['exterior'], results['interior'] = ext, intr
        results['source'] = self.extract_source(text, url)
        
        return results
    
    def get_extraction_summary(self, text: str, url: str = None) -> Dict[str, Any]:
        """Get detailed extraction summary with confidence and patterns"""
        summary = {}
        
        # Extract all fields with detailed results
        for field_name, extractor in self.registry.get_extractors_by_field().items():
                
            result = extractor.extract(text)
            if result:
                summary[field_name] = {
                    'value': result.value,
                    'confidence': result.confidence,
                    'pattern': result.source_pattern,
                    'raw_match': result.raw_match
                }
        
        # Add source extraction
        source_extractor = self.registry.get_extractor_by_field("source")
        if source_extractor and url:
            source_value = source_extractor.extract_from_url(url)
            summary['source'] = {
                'value': source_value,
                'confidence': 1.0,
                'pattern': 'url_parsing',
                'raw_match': url
            }
        
        return summary


# Export the unified extractor instance
UNIFIED_EXTRACTOR = UnifiedExtractor()

# Backward compatibility functions
def extract_year_from_text(text: str) -> Optional[int]:
    """Extract year from text (backward compatibility)"""
    return UNIFIED_EXTRACTOR.extract_year(text)

def extract_price_from_text(text: str) -> Optional[int]:
    """Extract price from text (backward compatibility)"""
    return UNIFIED_EXTRACTOR.extract_price(text)

def extract_mileage_from_text(text: str) -> Optional[int]:
    """Extract mileage from text (backward compatibility)"""
    return UNIFIED_EXTRACTOR.extract_mileage(text)

def extract_model_trim_from_text(text: str) -> Tuple[str, str]:
    """Extract model and trim from text (backward compatibility)"""
    return UNIFIED_EXTRACTOR.extract_model_trim(text)

def extract_colors_from_text(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract colors from text (backward compatibility)"""
    return UNIFIED_EXTRACTOR.extract_colors(text)

def extract_source_from_text(text: str, url: str = None) -> str:
    """Extract source from text or URL (backward compatibility)"""
    return UNIFIED_EXTRACTOR.extract_source(text, url)

# Deal delta extraction removed in MSRP-only cleanup
