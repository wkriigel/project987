"""
Options Registry - Automatically discovers and aggregates all individual option files

This registry automatically finds all option files and creates a unified interface.
Each option file is completely self-contained and can be modified independently.
"""

import os
import importlib
from typing import List, Dict, Any


class OptionsRegistry:
    """Registry that automatically discovers all available options from individual files"""
    
    def __init__(self):
        self.all_options = []
        self._discover_options()
    
    def _discover_options(self):
        """Automatically discover all option files in this directory"""
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Find all Python files (excluding __init__.py, base.py, detector.py, registry.py)
        excluded_files = {'__init__.py', 'base.py', 'detector.py', 'registry.py'}
        
        for filename in os.listdir(current_dir):
            if filename.endswith('.py') and filename not in excluded_files:
                # Extract module name (remove .py extension)
                module_name = filename[:-3]
                
                try:
                    # Import the module
                    module = importlib.import_module(f'.{module_name}', package='x987.options')
                    
                    # Look for option instances (files export OPTION_NAME_OPTION)
                    for attr_name in dir(module):
                        if attr_name.endswith('_OPTION') and hasattr(module, attr_name):
                            option_instance = getattr(module, attr_name)
                            
                            # Verify it has the required methods
                            if hasattr(option_instance, 'is_present') and \
                               hasattr(option_instance, 'get_value') and \
                               hasattr(option_instance, 'get_display') and \
                               hasattr(option_instance, 'get_category'):
                                
                                self.all_options.append(option_instance)
                                print(f"✓ Discovered option: {option_instance.get_display()}")
                
                except Exception as e:
                    print(f"⚠ Warning: Could not load option from {filename}: {e}")
        
        print(f"\n📋 Total options discovered: {len(self.all_options)}")
    
    def get_all_options(self):
        """Get all discovered options"""
        return self.all_options
    
    def get_options_by_category(self, category: str):
        """Get options filtered by category"""
        return [opt for opt in self.all_options if opt.get_category() == category]
    
    def get_option_by_id(self, option_id: str):
        """Get a specific option by ID"""
        for opt in self.all_options:
            if opt.get_id() == option_id:
                return opt
        return None
    
    def get_total_options_count(self) -> int:
        """Get total number of available options"""
        return len(self.all_options)
    
    def list_all_options(self):
        """List all discovered options with their details"""
        print("\n📋 All Discovered Options:")
        print("=" * 60)
        
        for i, option in enumerate(self.all_options, 1):
            print(f"{i:2d}. {option.get_display():<35} [${option.get_value('test'):>4,}] ({option.get_category()})")
        
        print("=" * 60)
        print(f"Total: {len(self.all_options)} options")


# Global registry instance
OPTIONS_REGISTRY = OptionsRegistry()

# Print discovery summary
if __name__ == "__main__":
    OPTIONS_REGISTRY.list_all_options()
