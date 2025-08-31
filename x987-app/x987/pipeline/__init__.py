"""
Pipeline modules for View-from-CSV

PROVIDES: Data processing pipeline components and orchestration
DEPENDS: x987.pipeline.steps modules and x987.utils.log:get_logger
CONSUMED BY: x987.cli.main:main function and external applications
CONTRACT: Provides data transformation and processing steps with modular architecture
TECH CHOICE: Modular pipeline with clear interfaces and dependency management
RISK: Medium - pipeline changes affect data flow
"""

# New modular pipeline steps (preferred)
from .steps import get_pipeline_runner, get_registry

__all__ = [
    # New modular pipeline
    "get_pipeline_runner",
    "get_registry"
]

def run_pipeline_modular(config, **kwargs):
    """Run the complete pipeline using our new modular pipeline steps"""
    from ..utils.log import get_logger
    logger = get_logger("pipeline.modular")
    
    logger.info("Running pipeline using new modular pipeline steps")
    
    # Get the modular pipeline runner
    runner = get_pipeline_runner()
    
    # Run the complete pipeline
    result = runner.run_pipeline(config, **kwargs)
    
    logger.info("✓ Modular pipeline completed successfully")
    return result

# Legacy compatibility - redirect to new system
def run_pipeline(config, **kwargs):
    """Legacy function that redirects to the new modular pipeline"""
    return run_pipeline_modular(config, **kwargs)
