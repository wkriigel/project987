"""
Extractors Registry - Automatically discovers and aggregates all individual extraction modules

PROVIDES: Automatic discovery and management of field extractors
DEPENDS: Base extractor classes and dynamic module loading
CONSUMED BY: Pipeline and unified extractor modules
CONTRACT: Provides centralized access to all available extractors
TECH CHOICE: Dynamic module discovery with reflection for maintainability
RISK: Medium - dynamic loading can fail if extractor files are malformed

This registry automatically finds all extractor files and creates a unified interface.
Each extractor file is completely self-contained and can be modified independently.
"""

import os
import importlib
from typing import List, Dict, Any, Optional
from .base import BaseExtractor, ExtractionResult


class ExtractorsRegistry:
    """Registry that automatically discovers all available extractors from individual files"""
    
    def __init__(self):
        self.all_extractors = []
        self.extractors_by_field = {}
        self._discover_extractors()
    
    def _discover_extractors(self):
        """Automatically discover all extractor files in this directory"""
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Find all Python files (excluding __init__.py, base.py, registry.py)
        excluded_files = {'__init__.py', 'base.py', 'registry.py'}
        
        for filename in os.listdir(current_dir):
            if filename.endswith('.py') and filename not in excluded_files:
                # Extract module name (remove .py extension)
                module_name = filename[:-3]
                
                try:
                    # Import the module
                    module = importlib.import_module(f'.{module_name}', package='x987.extractors')
                    
                    # Look for extractor instances (files export EXTRACTOR_NAME_EXTRACTOR)
                    for attr_name in dir(module):
                        if attr_name.endswith('_EXTRACTOR') and hasattr(module, attr_name):
                            extractor_instance = getattr(module, attr_name)
                            
                            # Verify it has the required methods
                            if hasattr(extractor_instance, 'extract') and \
                               hasattr(extractor_instance, 'get_field_name') and \
                               hasattr(extractor_instance, 'get_patterns'):
                                
                                self.all_extractors.append(extractor_instance)
                                field_name = extractor_instance.get_field_name()
                                self.extractors_by_field[field_name] = extractor_instance
                                print(f"✓ Discovered extractor: {extractor_instance.__class__.__name__} for field '{field_name}'")
                
                except Exception as e:
                    print(f"⚠ Warning: Could not load extractor from {filename}: {e}")
        
        print(f"\n📋 Total extractors discovered: {len(self.all_extractors)}")
    
    def get_all_extractors(self) -> List[BaseExtractor]:
        """Get all discovered extractors"""
        return self.all_extractors
    
    def get_extractor_by_field(self, field_name: str) -> Optional[BaseExtractor]:
        """Get a specific extractor by field name"""
        return self.extractors_by_field.get(field_name)
    
    def get_extractors_by_field(self) -> Dict[str, BaseExtractor]:
        """Get all extractors organized by field name"""
        return self.extractors_by_field.copy()
    
    def extract_field(self, field_name: str, text: str, **kwargs) -> Optional[ExtractionResult]:
        """Extract a specific field using the appropriate extractor"""
        extractor = self.get_extractor_by_field(field_name)
        if extractor:
            return extractor.extract(text, **kwargs)
        return None
    
    def extract_all_fields(self, text: str, **kwargs) -> Dict[str, ExtractionResult]:
        """Extract all available fields from text"""
        results = {}
        for field_name, extractor in self.extractors_by_field.items():
            result = extractor.extract(text, **kwargs)
            if result:
                results[field_name] = result
        return results
    
    def get_total_extractors_count(self) -> int:
        """Get total number of available extractors"""
        return len(self.all_extractors)
    
    def list_all_extractors(self):
        """List all discovered extractors with their details"""
        print("\n📋 All Discovered Extractors:")
        print("=" * 60)
        
        for i, extractor in enumerate(self.all_extractors, 1):
            field_name = extractor.get_field_name()
            patterns_count = len(extractor.get_patterns())
            print(f"{i:2d}. {extractor.__class__.__name__:<25} [Field: {field_name:<15}] ({patterns_count} patterns)")
        
        print("=" * 60)
        print(f"Total: {len(self.all_extractors)} extractors")


# Global registry instance
EXTRACTORS_REGISTRY = ExtractorsRegistry()

# Print discovery summary
if __name__ == "__main__":
    EXTRACTORS_REGISTRY.list_all_extractors()
