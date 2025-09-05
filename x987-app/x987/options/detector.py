"""
Options Detector - Main detection engine that uses the modular options registry
"""

from typing import List, Dict, Tuple, Optional
from .registry import OPTIONS_REGISTRY
from .value_overrides import get_override_value
from x987.config import get_config


class OptionsDetector:
    """Enhanced options detector using the modular options registry"""
    
    def __init__(self, options_registry=None):
        self.registry = options_registry or OPTIONS_REGISTRY
    
    def detect_options(self, text: str, trim: str = None, *, model: Optional[str] = None, year: Optional[int] = None) -> List[Tuple[str, int, str]]:
        """
        Detect options in text using the modular options system
        
        Args:
            text: Raw text to search for options
            trim: Vehicle trim (e.g., "S", "R") for standard-on logic
            
        Returns:
            List of tuples: (display_name, value_usd, category)
        """
        if not text:
            return []
        
        detected_options = []
        # Load MSRP catalog and pricing mode
        cfg = get_config()
        options_cfg = cfg.get_options_config() or {}
        msrp_catalog = (options_cfg.get('msrp_catalog') or {}) if isinstance(options_cfg, dict) else {}
        msrp_catalog_norm = {str(k): int(v) for k, v in msrp_catalog.items() if v is not None}
        
        # Check each option in the registry
        for option in self.registry.get_all_options():
            if option.is_present(text, trim):
                # Compute MSRP per option using per-generation override first, then catalog, else default 494
                opt_id = getattr(option, 'get_id')() if hasattr(option, 'get_id') else ''
                override = get_override_value(opt_id, model, year)
                if override is not None:
                    value = int(override)
                else:
                    value = int(msrp_catalog_norm.get(str(opt_id), 494))
                detected_options.append((
                    option.get_display(),
                    value,
                    option.get_category()
                ))
        
        # Sort by value (descending), then by display name
        detected_options.sort(key=lambda x: (-x[1], x[0].lower()))
        return detected_options
    
    def get_detailed_options_summary(self, text: str, trim: str = None, *, model: Optional[str] = None, year: Optional[int] = None) -> Dict:
        """
        Get detailed options summary with categorization
        
        Args:
            text: Raw text to search for options
            trim: Vehicle trim for standard-on logic
            
        Returns:
            Dictionary with options summary
        """
        detected = self.detect_options(text, trim, model=model, year=year)
        
        # Group by category
        by_category = {}
        total_value = 0
        
        for display, value, category in detected:
            if category not in by_category:
                by_category[category] = {
                    'options': [],
                    'count': 0,
                    'value': 0
                }
            
            by_category[category]['options'].append(display)
            by_category[category]['count'] += 1
            by_category[category]['value'] += value
            total_value += value
        
        # Sort categories by total value
        sorted_categories = sorted(
            by_category.items(),
            key=lambda x: x[1]['value'],
            reverse=True
        )
        
        return {
            'total_count': len(detected),
            'total_value': total_value,
            'by_category': dict(sorted_categories),
            'all_options': [opt[0] for opt in detected],
            'all_values': [opt[1] for opt in detected]
        }
    
    def get_options_value(self, text: str, trim: str = None, *, model: Optional[str] = None, year: Optional[int] = None) -> int:
        """Get total value of detected options"""
        detected = self.detect_options(text, trim, model=model, year=year)
        return sum(value for _, value, _ in detected)
    
    def get_options_display(self, text: str, trim: str = None, *, model: Optional[str] = None, year: Optional[int] = None) -> str:
        """Get comma-separated display string of detected options"""
        detected = self.detect_options(text, trim, model=model, year=year)
        return ", ".join(display for display, _, _ in detected)
    
    def get_options_by_category(self, text: str, trim: str = None, *, model: Optional[str] = None, year: Optional[int] = None) -> Dict[str, List[str]]:
        """Get options grouped by category"""
        detected = self.detect_options(text, trim, model=model, year=year)
        categorized = {}
        for display, _, category in detected:
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(display)
        return categorized
    
    def get_total_available_options(self) -> int:
        """Get total number of available options in the registry"""
        return self.registry.get_total_options_count()
    
    def get_options_by_category_from_registry(self, category: str):
        """Get all available options of a specific category from the registry"""
        return self.registry.get_options_by_category(category)
