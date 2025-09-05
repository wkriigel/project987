"""
Pipeline Runner - Orchestrates the execution of all pipeline steps

This file provides the main interface for running the complete pipeline
using the modular step system.

PROVIDES: Pipeline orchestration and execution management
DEPENDS: x987.pipeline.steps.base:BasePipelineStep, x987.pipeline.steps.registry:PIPELINE_REGISTRY
CONSUMED BY: x987.cli.main:main function and external applications
CONTRACT: Provides pipeline execution with dependency management and result tracking
TECH CHOICE: Modular pipeline with clear separation of concerns
RISK: Medium - pipeline orchestration affects overall system reliability
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import BasePipelineStep, StepResult, StepStatus
from .registry import PIPELINE_REGISTRY


class PipelineRunner:
    """Main pipeline runner that orchestrates all steps"""
    
    def __init__(self):
        self.registry = PIPELINE_REGISTRY
        self.execution_history: List[StepResult] = []
    
    def run_pipeline(self, config: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Run the complete pipeline in the correct order"""
        start_time = datetime.now()
        
        print(f"🚀 Starting pipeline: {start_time:%Y-%m-%d %H:%M:%S}")
        
        # Convert ConfigManager to dictionary if needed
        if hasattr(config, 'config'):
            config_dict = config.config
        else:
            config_dict = config
        
        # Keep startup minimal; detailed config shown only in verbose paths
        
        # Validate pipeline configuration
        validation = self.registry.validate_pipeline()
        if not validation["valid"]:
            print("❌ Pipeline validation failed:")
            for error in validation["errors"]:
                print(f"   - {error}")
            raise ValueError("Pipeline validation failed")
        
        # Get execution order
        execution_order = self.registry.get_execution_order()
        print(f"📋 Order: {' → '.join(execution_order)}\n")
        
        # Execute steps in order
        results = {}
        previous_results = {}
        
        for step_name in execution_order:
            step = self.registry.get_step_by_name(step_name)
            if not step:
                print(f"⚠ Warning: Step '{step_name}' not found, skipping")
                continue
            
            # Keep collection/scraping a bit louder; others summarized post-run
            if step_name in ("collection", "scraping"):
                print(f"▶ {step_name}: {step.get_description()}")
            
            # Execute the step
            step_result = step.execute(config_dict, previous_results, **kwargs)
            results[step_name] = step_result
            previous_results[step_name] = step_result
            
            # Print step result
            if step_result.is_success:
                # Compose tidy summary per step
                dur = f"{(step_result.duration_seconds or 0):.2f}s"
                summary = ""
                data = step_result.data if isinstance(step_result.data, dict) else {}
                if step_name == "transformation":
                    summary = f"processed {data.get('total_listings', 0)}"
                elif step_name == "deduplication":
                    summary = f"retained {data.get('final_count', 0)}/{data.get('original_count', 0)} (removed {data.get('duplicates_removed', 0)})"
                elif step_name == "fair_value":
                    summary = f"skipped (MSRP-only)"
                elif step_name == "ranking":
                    stats = data.get('ranking_stats', {}) if isinstance(data, dict) else {}
                    summary = f"ranked {data.get('total_listings', stats.get('total_listings', 0))}"
                elif step_name == "view":
                    summary = f"displayed {data.get('total_listings', 0)}"
                elif step_name == "collection":
                    # Collection step often returns list; runner summary may be limited
                    if isinstance(step_result.data, list):
                        count = len(step_result.data)
                    else:
                        count = data.get('urls_collected') if 'urls_collected' in data else (
                            data.get('total_urls') if 'total_urls' in data else data.get('count')
                        )
                    summary = f"found {count} URLs" if count != "" else "completed"
                elif step_name == "scraping":
                    # Try to summarize success/fail from data if present (preserve zeros)
                    succ = data.get('successful_scrapes') if 'successful_scrapes' in data else (
                        data.get('successful') if 'successful' in data else data.get('success_count')
                    )
                    fail = data.get('failed_scrapes') if 'failed_scrapes' in data else (
                        data.get('failed') if 'failed' in data else data.get('fail_count')
                    )
                    total = data.get('total_pages_scraped') if 'total_pages_scraped' in data else (
                        data.get('total') if 'total' in data else data.get('total_listings')
                    )
                    if succ is not None or fail is not None:
                        summary = f"scraped {succ or 0} ok, {fail or 0} failed"
                    elif total is not None:
                        summary = f"scraped {total}"
                    else:
                        summary = "completed"
                else:
                    # Default: show that it completed
                    summary = "completed"

                print(f"✓ {step_name:<14} {summary:<40} ({dur})")
            elif step_result.is_failure:
                print(f"   ❌ Failed: {step_result.error}")
                break
            else:
                print(f"   ⏭️ Skipped: {step_result.error}")
            
            print()
        
        # Calculate overall pipeline statistics
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        successful_steps = len([r for r in results.values() if r.is_success])
        failed_steps = len([r for r in results.values() if r.is_failure])
        skipped_steps = len([r for r in results.values() if r.status == StepStatus.SKIPPED])
        
        # Final summary
        print("=" * 60)
        print("📊 Pipeline Summary")
        print("=" * 60)
        print(f"Duration: {total_duration:.2f}s  |  Executed: {successful_steps}  |  Failed: {failed_steps}  |  Skipped: {skipped_steps}")
        
        # Store execution history
        self.execution_history.extend(results.values())
        
        return {
            "pipeline_results": results,
            "execution_summary": {
                "start_time": start_time,
                "end_time": end_time,
                "total_duration_seconds": total_duration,
                "successful_steps": successful_steps,
                "failed_steps": failed_steps,
                "skipped_steps": skipped_steps,
                "success_rate": successful_steps / len(results) if results else 0
            },
            "validation": validation
        }
    
    def run_single_step(self, step_name: str, config: Any, **kwargs) -> Optional[StepResult]:
        """Run a single pipeline step"""
        step = self.registry.get_step_by_name(step_name)
        if not step:
            print(f"❌ Step '{step_name}' not found")
            return None
        
        print(f"🔄 Running single step: {step_name}")
        print(f"   Description: {step.get_description()}")
        
        # Convert ConfigManager to dictionary if needed
        if hasattr(config, 'config'):
            config_dict = config.config
        else:
            config_dict = config
        
        # Execute step (with empty previous results for single step execution)
        result = step.execute(config_dict, {}, **kwargs)
        
        if result.is_success:
            print(f"   ✅ Completed in {result.duration_seconds:.2f}s")
        else:
            print(f"   ❌ Failed: {result.error}")
        
        return result
    
    def get_step(self, step_name: str) -> Optional[BasePipelineStep]:
        """Get a pipeline step by name"""
        return self.registry.get_step_by_name(step_name)
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the pipeline configuration"""
        return {
            "steps": self.registry.get_step_info(),
            "execution_order": self.registry.get_execution_order(),
            "validation": self.registry.validate_pipeline()
        }
    
    def list_steps(self):
        """List all available pipeline steps"""
        self.registry.list_all_steps()
    
    def get_execution_history(self) -> List[StepResult]:
        """Get the execution history of all pipeline runs"""
        return self.execution_history.copy()


# Export the pipeline runner instance
PIPELINE_RUNNER = PipelineRunner()
