#!/usr/bin/env python3
"""
Test script for enhanced options display with category-based organization

PROVIDES: Testing of enhanced options display system
DEPENDS: Options detector and Rich library
CONSUMED BY: Development and testing
CONTRACT: Tests category-based options organization and display
TECH CHOICE: Rich library for formatted display testing
RISK: Low - test files don't affect production code

This script demonstrates how the new enhanced options display works,
showing options organized by category for better readability.
"""

from x987.options_v2 import OptionsDetector
from x987.schema import NormalizedListing
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def test_enhanced_options_display():
    """Test the enhanced options display with various listing scenarios"""
    
    # Create options detector
    detector = OptionsDetector()
    
    # Test scenarios with different option combinations
    test_scenarios = [
        {
            "name": "Performance-Focused Cayman S",
            "year": 2011,
            "model": "Cayman",
            "trim": "S",
            "text": "This high-performance Cayman S features Sport Chrono Package Plus, PASM adaptive suspension, PSE sport exhaust system, and limited slip differential. Interior includes adaptive sport seats with heating and ventilation.",
            "expected_categories": ["performance", "comfort"]
        },
        {
            "name": "Technology-Rich Base Cayman",
            "year": 2009,
            "model": "Cayman",
            "trim": "Base",
            "text": "Base model with PCM navigation system, BOSE surround sound, bi-xenon headlights with dynamic cornering, 19-inch alloy wheels, and park assist sensors.",
            "expected_categories": ["technology", "appearance", "technology"]
        },
        {
            "name": "Luxury Cayman Black Edition",
            "year": 2012,
            "model": "Cayman",
            "trim": "Black Edition",
            "text": "Black Edition featuring Sport Chrono Package Plus, PASM, Sport Exhaust, adaptive sport seats, heated and ventilated seats, PCM navigation, BOSE audio, bi-xenon lighting, 19-inch wheels, and park assist.",
            "expected_categories": ["performance", "comfort", "technology", "appearance", "technology"]
        },
        {
            "name": "Minimal Options Cayman",
            "year": 2010,
            "model": "Cayman",
            "trim": "Base",
            "text": "Basic model with standard features only.",
            "expected_categories": []
        }
    ]
    
    console.print(Panel("[bold cyan]Enhanced Options Display Test[/bold cyan]", style="cyan"))
    console.print()
    
    for i, scenario in enumerate(test_scenarios, 1):
        console.print(f"[bold blue]Scenario {i}: {scenario['name']}[/bold blue]")
        console.print(f"[dim]Text:[/dim] {scenario['text']}")
        console.print(f"[dim]Trim:[/dim] {scenario['trim']}")
        
        # Detect options
        detected = detector.detect_options(scenario['text'], scenario['trim'])
        summary = detector.get_detailed_options_summary(scenario['text'], scenario['trim'])
        
        # Create a sample listing for display testing
        listing = NormalizedListing(
            timestamp_run_id="test",
            source="test",
            listing_url="https://example.com/test",
            year=scenario['year'],
            model=scenario['model'],
            trim=scenario['trim'],
            raw_options=scenario['text']
        )
        
        # Add options data
        listing.options_summary = summary
        listing.options_detected = summary['all_options']
        listing.options_value = summary['total_value']
        listing.options_by_category = summary['by_category']
        
        # Display results
        if detected:
            console.print(f"[green]Detected {len(detected)} options:[/green]")
            
            # Show by category
            if summary['by_category']:
                console.print(f"[green]By Category:[/green]")
                for category, data in summary['by_category'].items():
                    console.print(f"  [bold]{category.title()}:[/bold] {len(data['options'])} options (${data['value']:,})")
                    for option in data['options']:
                        console.print(f"    • {option}")
            
            console.print(f"[green]Total Value:[/green] ${summary['total_value']:,}")
            
            # Simulate the enhanced display
            console.print(f"\n[bold yellow]Enhanced Display Preview:[/bold yellow]")
            display_text = simulate_enhanced_display(listing)
            console.print(f"  {display_text}")
            
        else:
            console.print("[yellow]No options detected[/yellow]")
        
        console.print()
        console.print("-" * 80)
        console.print()

def simulate_enhanced_display(listing):
    """Simulate the enhanced options display logic"""
    
    # Check if we have options summary data
    if hasattr(listing, 'options_summary') and listing.options_summary:
        summary = listing.options_summary
        if 'by_category' in summary and summary['by_category']:
            # Show options by category for better organization
            category_display = []
            for category, data in summary['by_category'].items():
                if data['options']:
                    # Limit options per category to avoid overwhelming display
                    options_list = data['options'][:3]  # Show max 3 per category
                    if len(data['options']) > 3:
                        options_list.append("...")
                    category_display.append(f"{category.title()}: {', '.join(options_list)}")
            
            if category_display:
                # Limit total categories shown
                if len(category_display) > 3:
                    category_display = category_display[:2] + ["..."]
                
                return " | ".join(category_display)
    
    # Fallback to simple options display
    if hasattr(listing, 'options_detected') and listing.options_detected:
        options_str = ", ".join(listing.options_detected[:5])  # Limit to 5 options
        if len(listing.options_detected) > 5:
            options_str += "..."
        return options_str
    
    return "N/A"

def test_options_summary_panel():
    """Test the options summary panel creation"""
    
    console.print(Panel("[bold cyan]Options Summary Panel Test[/bold cyan]", style="cyan"))
    console.print()
    
    # Create sample listings with options
    sample_listings = [
        NormalizedListing(
            timestamp_run_id="test1",
            source="test",
            listing_url="https://example.com/1",
            year=2011,
            model="Cayman",
            trim="S",
            raw_options="Sport Chrono Package Plus, PASM, PSE Sport Exhaust, Limited Slip Differential, Sport Seats, Heated Seats, PCM Navigation, BOSE Sound System, Bi-Xenon Headlights, 19 inch wheels, Park Assist"
        ),
        NormalizedListing(
            timestamp_run_id="test2",
            source="test",
            listing_url="https://example.com/2",
            year=2010,
            model="Cayman",
            trim="Base",
            raw_options="Sport Seats, PCM Navigation, BOSE Audio, 18 inch wheels"
        )
    ]
    
    detector = OptionsDetector()
    
    # Process each listing
    for i, listing in enumerate(sample_listings, 1):
        console.print(f"[bold blue]Processing Listing {i}:[/bold blue]")
        
        # Get options summary
        summary = detector.get_detailed_options_summary(listing.raw_options, listing.trim)
        
        # Update listing with options data
        listing.options_summary = summary
        listing.options_detected = summary['all_options']
        listing.options_value = summary['total_value']
        listing.options_by_category = summary['by_category']
        
        console.print(f"  Options detected: {len(summary['all_options'])}")
        console.print(f"  Total value: ${summary['total_value']:,}")
        console.print(f"  Categories: {list(summary['by_category'].keys())}")
        
        # Show enhanced display
        display_text = simulate_enhanced_display(listing)
        console.print(f"  Enhanced display: {display_text}")
        console.print()
    
    # Create summary statistics
    total_options = sum(len(l.options_detected) for l in sample_listings)
    total_value = sum(l.options_value for l in sample_listings)
    
    console.print(f"[bold green]Summary:[/bold green]")
    console.print(f"  Total listings: {len(sample_listings)}")
    console.print(f"  Total options detected: {total_options}")
    console.print(f"  Total options value: ${total_value:,}")

def main():
    """Main test function"""
    try:
        # Test enhanced options display
        test_enhanced_options_display()
        
        # Test options summary panel
        test_options_summary_panel()
        
        console.print(Panel("[bold green]All enhanced display tests completed![/bold green]", style="green"))
        
    except Exception as e:
        console.print(f"[red]Error during testing: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
