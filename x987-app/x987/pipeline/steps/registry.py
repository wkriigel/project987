"""
Pipeline Steps Registry - Automatically discovers and aggregates all individual pipeline step modules

This registry automatically finds all step files and creates a unified interface.
Each step file is completely self-contained and can be modified independently.

PROVIDES: Pipeline step discovery and dependency management
DEPENDS: x987.pipeline.steps.base:BasePipelineStep and dynamic module loading
CONSUMED BY: x987.pipeline.steps.runner:PipelineRunner
CONTRACT: Provides step discovery with dependency resolution and execution ordering
TECH CHOICE: Dynamic module loading with dependency graph calculation
RISK: Medium - dynamic loading can fail, dependency resolution must be correct
"""

import os
import importlib
from typing import List, Dict, Any, Optional
from .base import BasePipelineStep, StepResult


class PipelineStepsRegistry:
    """Registry that automatically discovers all available pipeline steps from individual files"""
    
    def __init__(self):
        self.all_steps = []
        self.steps_by_name = {}
        self.execution_order = []
        self._discover_steps()
        self._calculate_execution_order()
    
    def _discover_steps(self):
        """Automatically discover all step files in this directory"""
        # Get the directory where this file is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Find all Python files (excluding __init__.py, base.py, registry.py, runner.py)
        excluded_files = {'__init__.py', 'base.py', 'registry.py', 'runner.py'}
        
        for filename in os.listdir(current_dir):
            if filename.endswith('.py') and filename not in excluded_files:
                # Extract module name (remove .py extension)
                module_name = filename[:-3]
                
                try:
                    # Import the module
                    module = importlib.import_module(f'.{module_name}', package='x987.pipeline.steps')
                    
                    # Look for step instances (files export STEP_NAME_STEP)
                    for attr_name in dir(module):
                        if attr_name.endswith('_STEP') and hasattr(module, attr_name):
                            step_instance = getattr(module, attr_name)
                            
                            # Verify it has the required methods
                            if hasattr(step_instance, 'execute') and \
                               hasattr(step_instance, 'get_step_name') and \
                               hasattr(step_instance, 'get_dependencies'):
                                
                                self.all_steps.append(step_instance)
                                step_name = step_instance.get_step_name()
                                self.steps_by_name[step_name] = step_instance
                                if os.environ.get('X987_REGISTRY_VERBOSE'):
                                    print(f"✓ Discovered pipeline step: {step_instance.get_description()}")
                
                except Exception as e:
                    if os.environ.get('X987_REGISTRY_VERBOSE'):
                        print(f"⚠ Warning: Could not load step from {filename}: {e}")
        
        if os.environ.get('X987_REGISTRY_VERBOSE'):
            print(f"\n📋 Total pipeline steps discovered: {len(self.all_steps)}")
    
    def _calculate_execution_order(self):
        """Calculate the correct execution order based on dependencies"""
        # Start with steps that have no dependencies
        remaining_steps = set(self.steps_by_name.keys())
        self.execution_order = []
        
        while remaining_steps:
            # Find steps that can be executed (all dependencies are satisfied)
            executable_steps = []
            for step_name in remaining_steps:
                step = self.steps_by_name[step_name]
                if all(dep in self.execution_order for dep in step.get_dependencies()):
                    executable_steps.append(step_name)
            
            if not executable_steps:
                # Circular dependency or missing step
                if os.environ.get('X987_REGISTRY_VERBOSE'):
                    print(f"⚠ Warning: Cannot resolve dependencies for remaining steps: {remaining_steps}")
                break
            
            # Add executable steps to order
            for step_name in executable_steps:
                self.execution_order.append(step_name)
                remaining_steps.remove(step_name)
        
        if os.environ.get('X987_REGISTRY_VERBOSE'):
            print(f"📋 Pipeline execution order: {' → '.join(self.execution_order)}")
    
    def get_all_steps(self) -> List[BasePipelineStep]:
        """Get all discovered steps"""
        return self.all_steps
    
    def get_step_by_name(self, step_name: str) -> Optional[BasePipelineStep]:
        """Get a specific step by name"""
        return self.steps_by_name.get(step_name)
    
    def get_steps_by_name(self) -> Dict[str, BasePipelineStep]:
        """Get all steps organized by name"""
        return self.steps_by_name.copy()
    
    def get_execution_order(self) -> List[str]:
        """Get the correct execution order for pipeline steps"""
        return self.execution_order.copy()
    
    def get_step_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all steps"""
        info = {}
        for step_name, step in self.steps_by_name.items():
            info[step_name] = step.get_step_info()
        return info
    
    def validate_pipeline(self) -> Dict[str, Any]:
        """Validate that the pipeline is properly configured"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "step_count": len(self.all_steps),
            "execution_order": self.execution_order
        }
        
        # Check for missing dependencies
        for step_name, step in self.steps_by_name.items():
            for dep in step.get_dependencies():
                if dep not in self.steps_by_name:
                    validation_result["valid"] = False
                    validation_result["errors"].append(f"Step '{step_name}' depends on missing step '{dep}'")
        
        # Check for circular dependencies
        if len(self.execution_order) != len(self.all_steps):
            validation_result["valid"] = False
            validation_result["errors"].append("Circular dependencies detected in pipeline")
        
        return validation_result
    
    def list_all_steps(self):
        """List all discovered steps with their details"""
        print("\n📋 All Discovered Pipeline Steps:")
        print("=" * 80)
        
        for i, step_name in enumerate(self.execution_order, 1):
            step = self.steps_by_name[step_name]
            deps = ", ".join(step.get_dependencies()) if step.get_dependencies() else "none"
            config = ", ".join(step.get_required_config()) if step.get_required_config() else "none"
            
            print(f"{i:2d}. {step_name:<20} [Deps: {deps:<15}] [Config: {config:<20}]")
            print(f"     {step.get_description()}")
        
        print("=" * 80)
        print(f"Total: {len(self.all_steps)} steps")


# Global registry instance
PIPELINE_REGISTRY = PipelineStepsRegistry()

# Print discovery summary
if __name__ == "__main__":
    PIPELINE_REGISTRY.list_all_steps()
