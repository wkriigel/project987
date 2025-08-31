#!/usr/bin/env python3
"""
Test script for the new modular pipeline system

PROVIDES: Testing and demonstration of modular pipeline system
DEPENDS: Pipeline modules and Rich library
CONSUMED BY: Development and debugging
CONTRACT: Tests pipeline discovery, execution, and validation
TECH CHOICE: Rich library for formatted output and testing
RISK: Low - test files don't affect production code

This script demonstrates how the new pipeline system works with individual
step files and shows the pipeline execution flow.
"""

from x987.pipeline.steps import get_registry, get_pipeline_runner
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def test_pipeline_discovery():
    """Test the automatic discovery of pipeline steps"""
    
    console.print(Panel("[bold cyan]Pipeline Steps Discovery Test[/bold cyan]", style="cyan"))
    console.print()
    
    # Get the registry
    registry = get_registry()
    
    # List all discovered steps
    registry.list_all_steps()
    
    # Get pipeline information
    pipeline_info = registry.get_step_info()
    
    console.print("\n📋 Pipeline Configuration:")
    console.print(f"   Total Steps: {len(pipeline_info)}")
    console.print(f"   Execution Order: {' → '.join(registry.get_execution_order())}")
    
    # Validate pipeline
    validation = registry.validate_pipeline()
    if validation["valid"]:
        console.print("   ✅ Pipeline validation: PASSED")
    else:
        console.print("   ❌ Pipeline validation: FAILED")
        for error in validation["errors"]:
            console.print(f"      - {error}")


def test_pipeline_info():
    """Test getting detailed pipeline information"""
    
    console.print(Panel("[bold green]Pipeline Information Test[/bold green]", style="green"))
    console.print()
    
    # Get the pipeline runner
    runner = get_pipeline_runner()
    
    # Get pipeline info
    info = runner.get_pipeline_info()
    
    # Display step details
    table = Table(title="Pipeline Steps Details", box=box.ROUNDED)
    table.add_column("Step Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Dependencies", style="yellow")
    table.add_column("Required Config", style="magenta")
    
    for step_name, step_info in info["steps"].items():
        deps = ", ".join(step_info["dependencies"]) if step_info["dependencies"] else "none"
        config = ", ".join(step_info["required_config"]) if step_info["required_config"] else "none"
        
        table.add_row(
            step_name,
            step_info["description"],
            deps,
            config
        )
    
    console.print(table)


def test_single_step_execution():
    """Test running a single pipeline step"""
    
    console.print(Panel("[bold yellow]Single Step Execution Test[/bold yellow]", style="yellow"))
    console.print()
    
    # Get the pipeline runner
    runner = get_pipeline_runner()
    
    # Test configuration (minimal for testing)
    test_config = {
        "search": {
            "urls": ["https://example.com/test"]
        },
        "scraping": {
            "concurrency": 1,
            "polite_delay_ms": 100,
            "cap_listings": 5
        },
        "fair_value": {
            "base_value_usd": 30000,
            "year_step_usd": 500,
            "s_premium_usd": 7000
        }
    }
    
    console.print("🔍 Testing single step execution...")
    console.print("   Note: This will fail due to missing dependencies, but shows the system working")
    console.print()
    
    # Try to run the collection step (should work)
    try:
        result = runner.run_single_step("collection", test_config)
        if result:
            console.print(f"   ✅ Collection step completed: {result.status.value}")
        else:
            console.print("   ❌ Collection step failed to run")
    except Exception as e:
        console.print(f"   ⚠️ Collection step error (expected): {e}")
    
    console.print()


def test_pipeline_validation():
    """Test pipeline validation and dependency checking"""
    
    console.print(Panel("[bold blue]Pipeline Validation Test[/bold blue]", style="blue"))
    console.print()
    
    # Get the registry
    registry = get_registry()
    
    # Run validation
    validation = registry.validate_pipeline()
    
    console.print("🔍 Pipeline Validation Results:")
    console.print(f"   Valid: {validation['valid']}")
    console.print(f"   Step Count: {validation['step_count']}")
    console.print(f"   Execution Order: {' → '.join(validation['execution_order'])}")
    
    if validation["errors"]:
        console.print("\n   ❌ Errors:")
        for error in validation["errors"]:
            console.print(f"      - {error}")
    
    if validation["warnings"]:
        console.print("\n   ⚠️ Warnings:")
        for warning in validation["warnings"]:
            console.print(f"      - {warning}")
    
    if validation["valid"]:
        console.print("\n   ✅ Pipeline is properly configured and ready to run!")


def main():
    """Run all tests"""
    
    console.print(Panel("[bold magenta]Modular Pipeline System Test Suite[/bold magenta]", style="magenta"))
    console.print("Testing the new 'one file per pipeline step' architecture")
    console.print()
    
    try:
        # Test 1: Pipeline discovery
        test_pipeline_discovery()
        console.print("\n" + "="*80 + "\n")
        
        # Test 2: Pipeline information
        test_pipeline_info()
        console.print("\n" + "="*80 + "\n")
        
        # Test 3: Single step execution
        test_single_step_execution()
        console.print("\n" + "="*80 + "\n")
        
        # Test 4: Pipeline validation
        test_pipeline_validation()
        
    except Exception as e:
        console.print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
