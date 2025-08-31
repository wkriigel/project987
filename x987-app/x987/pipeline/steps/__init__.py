"""
Pipeline Steps Package - Modular pipeline step system

PROVIDES: Modular pipeline step system with automatic discovery
DEPENDS: Base pipeline step classes and registry system
CONSUMED BY: Pipeline runner and main application
CONTRACT: Provides standardized pipeline step execution interface
TECH CHOICE: Single-purpose modules with registry-based discovery
RISK: Medium - pipeline steps must maintain consistent interfaces

Each pipeline step has its own file with execution logic.
The PipelineRegistry automatically discovers all step definitions.
"""

from .base import BasePipelineStep, StepResult, StepStatus

# Lazy import to avoid circular dependencies
def get_registry():
    from .registry import PIPELINE_REGISTRY
    return PIPELINE_REGISTRY

def get_pipeline_runner():
    from .runner import PipelineRunner
    return PipelineRunner()

__all__ = [
    'BasePipelineStep',
    'StepResult', 
    'StepStatus',
    'get_registry',
    'get_pipeline_runner'
]
