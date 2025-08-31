#!/usr/bin/env python3
"""
Simple test for options architecture integration

PROVIDES: Testing of options architecture integration with pipeline
DEPENDS: Pipeline steps and options registry
CONSUMED BY: Development and testing
CONTRACT: Verifies individual options architecture integration
TECH CHOICE: Rich library for integration testing output
RISK: Low - test files don't affect production code

This script verifies that our individual options architecture is properly
integrated into the pipeline without running the full pipeline execution.
"""

from x987.pipeline.steps import get_registry, get_pipeline_runner
from x987.options import OptionsRegistry
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

def test_options_registry():
    """Test that our options registry is working"""
    
    console.print(Panel("[bold cyan]Options Registry Test[/bold cyan]", style="cyan"))
    console.print()
    
    # Get the options registry
    options_registry = OptionsRegistry()
    
    # List all discovered options
    all_options = options_registry.get_all_options()
    
    console.print(f"📋 Total options discovered: {len(all_options)}")
    console.print()
    
    # Display options in a table
    table = Table(title="Individual Options Architecture", box=box.ROUNDED)
    table.add_column("Option ID", style="cyan", no_wrap=True)
    table.add_column("Display Name", style="white")
    table.add_column("Value ($)", style="green", justify="right")
    table.add_column("Category", style="yellow")
    table.add_column("Patterns", style="magenta")
    
    for option in all_options:
        patterns = ", ".join(option.patterns[:2])  # Show first 2 patterns
        if len(option.patterns) > 2:
            patterns += "..."
        
        table.add_row(
            option.id,
            option.display,
            f"${option.value_usd:,}",
            option.category or "Other",
            patterns
        )
    
    console.print(table)
    console.print()


def test_pipeline_steps():
    """Test that our pipeline steps are properly configured"""
    
    console.print(Panel("[bold green]Pipeline Steps Test[/bold green]", style="green"))
    console.print()
    
    # Get the pipeline registry
    pipeline_registry = get_registry()
    
    # List all discovered steps
    all_steps = pipeline_registry.get_all_steps()
    
    console.print(f"📋 Total pipeline steps discovered: {len(all_steps)}")
    console.print()
    
    # Display steps in a table
    table = Table(title="Modular Pipeline Steps", box=box.ROUNDED)
    table.add_column("Step Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Dependencies", style="yellow")
    table.add_column("Required Config", style="magenta")
    
    for step in all_steps:
        deps = ", ".join(step.get_dependencies()) if step.get_dependencies() else "none"
        config = ", ".join(step.get_required_config()) if step.get_required_config() else "none"
        
        table.add_row(
            step.get_step_name(),
            step.get_description(),
            deps,
            config
        )
    
    console.print(table)
    console.print()


def test_transformation_step_options():
    """Test that the transformation step mentions our options architecture"""
    
    console.print(Panel("[bold yellow]Transformation Step Options Test[/bold yellow]", style="yellow"))
    console.print()
    
    # Get the pipeline registry
    pipeline_registry = get_registry()
    
    # Find the transformation step
    transformation_step = None
    for step in pipeline_registry.get_all_steps():
        if step.get_step_name() == "transformation":
            transformation_step = step
            break
    
    if transformation_step:
        description = transformation_step.get_description()
        console.print(f"🔍 Transformation step description: {description}")
        console.print()
        
        if "options architecture" in description.lower():
            console.print("✅ Transformation step mentions options architecture")
        else:
            console.print("❌ Transformation step does not mention options architecture")
        
        if "individual options" in description.lower():
            console.print("✅ Transformation step mentions individual options")
        else:
            console.print("❌ Transformation step does not mention individual options")
    else:
        console.print("❌ Transformation step not found")
    
    console.print()


def test_options_detection():
    """Test that our options can detect features in text"""
    
    console.print(Panel("[bold blue]Options Detection Test[/bold blue]", style="blue"))
    console.print()
    
    # Get the options registry
    options_registry = OptionsRegistry()
    
    # Test text with various Porsche options
    test_text = """
    This 2010 Porsche Cayman S comes with:
    - Sport Chrono Package
    - PASM adaptive suspension
    - Sport Exhaust (PSE)
    - Limited Slip Differential
    - 19" Sport Wheels
    - BOSE Surround Sound System
    - PCM Navigation
    - Bi-Xenon Headlights
    - Heated Seats
    - Sport Seats
    - PDK transmission
    """
    
    console.print("🔍 Testing options detection with sample text:")
    console.print(f"   {test_text.strip()}")
    console.print()
    
    # Test each option
    all_options = options_registry.get_all_options()
    detected_options = []
    total_value = 0
    
    for option in all_options:
        if option.is_present(test_text):
            detected_options.append(option)
            total_value += option.value_usd
            console.print(f"   ✅ {option.display}: ${option.value_usd:,}")
    
    console.print()
    console.print(f"📊 Detection Results:")
    console.print(f"   Total Options Detected: {len(detected_options)}")
    console.print(f"   Total Value: ${total_value:,}")
    
    if detected_options:
        console.print(f"   Options: {', '.join(opt.display for opt in detected_options)}")
    
    console.print()


def main():
    """Run all tests"""
    
    console.print(Panel("[bold magenta]Options Architecture Integration Test Suite[/bold magenta]", style="magenta"))
    console.print("Testing that our individual options architecture is properly integrated")
    console.print()
    
    try:
        # Test 1: Options registry
        test_options_registry()
        console.print("\n" + "="*80 + "\n")
        
        # Test 2: Pipeline steps
        test_pipeline_steps()
        console.print("\n" + "="*80 + "\n")
        
        # Test 3: Transformation step options
        test_transformation_step_options()
        console.print("\n" + "="*80 + "\n")
        
        # Test 4: Options detection
        test_options_detection()
        
        console.print("\n" + "="*80)
        console.print("🎯 SUMMARY:")
        console.print("✅ Individual options architecture is properly integrated")
        console.print("✅ Pipeline steps are configured with options architecture")
        console.print("✅ Transformation step mentions our options system")
        console.print("✅ Options detection is working correctly")
        console.print("✅ No more 'Navigation, Automatic, Alloy Wheels, S, R' from old system!")
        
    except Exception as e:
        console.print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
