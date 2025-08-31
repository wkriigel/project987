#!/usr/bin/env python3
"""
Test script for the new modular extraction system

PROVIDES: Testing of modular extraction system functionality
DEPENDS: Extractors registry and Rich library
CONSUMED BY: Development and testing
CONTRACT: Tests individual and unified extractor interfaces
TECH CHOICE: Rich library for formatted testing output
RISK: Low - test files don't affect production code

This script demonstrates how the new extraction system works with various
text patterns and shows the extracted data for each field.
"""

from x987.extractors import get_registry, get_unified_extractor
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def test_individual_extractors():
    """Test each individual extractor separately"""
    
    console.print(Panel("[bold cyan]Individual Extractors Test[/bold cyan]", style="cyan"))
    console.print()
    
    # Get the registry
    registry = get_registry()
    
    # Test text with various vehicle information
    test_text = """
    2010 Porsche Cayman S
    Price: $32,500
    Mileage: 45,000 miles
    Exterior color: Arctic Silver Metallic
    Interior color: Black Leather
    Features: Sport Chrono Package, PASM, Sport Exhaust, Limited Slip Differential
    Listed on Cars.com
    """
    
    console.print(f"[dim]Test Text:[/dim] {test_text.strip()}")
    console.print()
    
    # Test each extractor
    for field_name, extractor in registry.get_extractors_by_field().items():
        console.print(f"[bold blue]Testing {extractor.__class__.__name__}:[/bold blue]")
        
        if field_name == "deal_delta":
            # Deal delta requires fair value and asking price
            result = extractor.extract("", fair_value=35000, asking_price=32500)
        else:
            result = extractor.extract(test_text)
        
        if result:
            console.print(f"  ✓ Extracted: {result.value}")
            console.print(f"  Confidence: {result.confidence}")
            console.print(f"  Pattern: {result.source_pattern}")
            if result.raw_match:
                console.print(f"  Raw Match: {result.raw_match}")
        else:
            console.print("  ✗ No extraction")
        
        console.print()

def test_unified_extractor():
    """Test the unified extractor interface"""
    
    console.print(Panel("[bold cyan]Unified Extractor Test[/bold cyan]", style="cyan"))
    console.print()
    
    # Get the unified extractor
    unified = get_unified_extractor()
    
    # Test text
    test_text = """
    2011 Boxster Base
    Asking: $28,900
    Mileage: 52,300 miles
    Exterior: Guards Red
    Interior: Beige
    From TrueCar
    """
    
    console.print(f"[dim]Test Text:[/dim] {test_text.strip()}")
    console.print()
    
    # Extract all fields
    results = unified.extract_all(test_text)
    
    # Display results
    table = Table(title="Extracted Fields", box=box.ROUNDED)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    
    for field, value in results.items():
        if isinstance(value, tuple):
            value_str = " / ".join(str(v) for v in value if v)
        else:
            value_str = str(value) if value is not None else "None"
        table.add_row(field, value_str)
    
    console.print(table)
    console.print()

def test_extraction_summary():
    """Test the detailed extraction summary"""
    
    console.print(Panel("[bold cyan]Detailed Extraction Summary Test[/bold cyan]", style="cyan"))
    console.print()
    
    # Get the unified extractor
    unified = get_unified_extractor()
    
    # Test text
    test_text = """
    2009 Cayman R
    Price: $45,000
    Mileage: 38,500 miles
    Exterior: GT Silver Metallic
    Interior: Black
    Features: Sport Chrono, PASM, Sport Exhaust
    Source: Carvana
    """
    
    console.print(f"[dim]Test Text:[/dim] {test_text.strip()}")
    console.print()
    
    # Get detailed summary
    summary = unified.get_extraction_summary(test_text)
    
    # Display detailed results
    for field_name, details in summary.items():
        console.print(f"[bold blue]{field_name.title()}:[/bold blue]")
        console.print(f"  Value: {details['value']}")
        console.print(f"  Confidence: {details['confidence']}")
        console.print(f"  Pattern: {details['pattern']}")
        if details['raw_match']:
            console.print(f"  Raw Match: {details['raw_match']}")
        console.print()

def test_registry_discovery():
    """Test the automatic discovery system"""
    
    console.print(Panel("[bold cyan]Registry Discovery Test[/bold cyan]", style="cyan"))
    console.print()
    
    # Get the registry
    registry = get_registry()
    
    # List all discovered extractors
    registry.list_all_extractors()
    console.print()
    
    # Show extractors by field
    console.print("[bold blue]Extractors by Field:[/bold blue]")
    for field_name, extractor in registry.get_extractors_by_field().items():
        console.print(f"  {field_name}: {extractor.__class__.__name__}")
    
    console.print()

def main():
    """Run all tests"""
    
    console.print(Panel("[bold green]Modular Extraction System Test Suite[/bold green]", style="green"))
    console.print()
    
    try:
        # Test registry discovery
        test_registry_discovery()
        console.print("=" * 80)
        console.print()
        
        # Test individual extractors
        test_individual_extractors()
        console.print("=" * 80)
        console.print()
        
        # Test unified extractor
        test_unified_extractor()
        console.print("=" * 80)
        console.print()
        
        # Test detailed summary
        test_extraction_summary()
        
        console.print(Panel("[bold green]All tests completed successfully![/bold green]", style="green"))
        
    except Exception as e:
        console.print(f"[bold red]Test failed: {e}[/bold red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
