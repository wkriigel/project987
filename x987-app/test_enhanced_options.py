#!/usr/bin/env python3
"""
Test script for enhanced options detection system

PROVIDES: Testing of enhanced options detection system
DEPENDS: Options detector and Rich library
CONSUMED BY: Development and testing
CONTRACT: Tests options detection with various text patterns
TECH CHOICE: Rich library for formatted testing output
RISK: Low - test files don't affect production code

This script demonstrates how the new options detection system works with various
text patterns and shows the categorized output.
"""

from x987.options_v2 import OptionsDetector, DEFAULT_OPTIONS
from x987.schema import NormalizedListing
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def test_options_detection():
    """Test the options detection with various text patterns"""
    
    # Create options detector
    detector = OptionsDetector()
    
    # Test cases with different wordings
    test_cases = [
        {
            "name": "Sport Chrono + PASM + PSE",
            "text": "This Porsche features Sport Chrono Package Plus, PASM adaptive suspension, and PSE sport exhaust system. Also includes heated seats and BOSE audio.",
            "trim": "S"
        },
        {
            "name": "LSD + Sport Seats + Navigation",
            "text": "Limited Slip Differential, Adaptive Sport Seats, PCM with Navigation, Bi-Xenon headlights with dynamic cornering, 19 inch wheels",
            "trim": "Base"
        },
        {
            "name": "Cayman R (LSD and 19\" wheels standard)",
            "text": "Cayman R with Sport Chrono, PASM, Sport Exhaust, BOSE sound system, Heated and Ventilated seats, Park Assist sensors",
            "trim": "R"
        },
        {
            "name": "Mixed terminology",
            "text": "Features include: chrono package, adaptive sport suspension, switchable exhaust, locking differential, bucket seats, seat heating, pcm navigation, bose speakers, litronic headlights, 19 inch alloy wheels, parking assistance",
            "trim": "S"
        },
        {
            "name": "Minimal options",
            "text": "Basic model with standard features",
            "trim": "Base"
        }
    ]
    
    console.print(Panel("[bold cyan]Enhanced Options Detection Test[/bold cyan]", style="cyan"))
    console.print()
    
    for i, test_case in enumerate(test_cases, 1):
        console.print(f"[bold blue]Test Case {i}: {test_case['name']}[/bold blue]")
        console.print(f"[dim]Text:[/dim] {test_case['text']}")
        console.print(f"[dim]Trim:[/dim] {test_case['trim']}")
        
        # Detect options
        detected = detector.detect_options(test_case['text'], test_case['trim'])
        summary = detector.get_detailed_options_summary(test_case['text'], test_case['trim'])
        
        # Display results
        if detected:
            console.print(f"[green]Detected {len(detected)} options:[/green]")
            for display, value, category in detected:
                console.print(f"  • {display} (${value:,}) [{category}]")
            
            console.print(f"[green]Total Value:[/green] ${summary['total_value']:,}")
            
            # Show by category
            if summary['by_category']:
                console.print(f"[green]By Category:[/green]")
                for category, data in summary['by_category'].items():
                    console.print(f"  {category.title()}: {len(data['options'])} options (${data['value']:,})")
        else:
            console.print("[yellow]No options detected[/yellow]")
        
        console.print()
        console.print("-" * 80)
        console.print()

def test_with_sample_listings():
    """Test with sample listing data"""
    
    console.print(Panel("[bold cyan]Sample Listings Options Analysis[/bold cyan]", style="cyan"))
    console.print()
    
    # Create sample listings
    sample_listings = [
        NormalizedListing(
            timestamp_run_id="test",
            source="test",
            listing_url="https://example.com/1",
            year=2010,
            model="Cayman",
            trim="S",
            transmission_norm="Automatic",
            mileage=45000,
            price_usd=35000,
            exterior_color="Arctic Silver",
            interior_color="Black",
            raw_options="Sport Chrono Package Plus, PASM, PSE Sport Exhaust, Limited Slip Differential, Sport Seats, Heated Seats, PCM Navigation, BOSE Sound System, Bi-Xenon Headlights, 19 inch wheels, Park Assist"
        ),
        NormalizedListing(
            timestamp_run_id="test",
            source="test",
            listing_url="https://example.com/2",
            year=2011,
            model="Cayman",
            trim="R",
            transmission_norm="Manual",
            mileage=30000,
            price_usd=45000,
            exterior_color="Black",
            interior_color="Red",
            raw_options="Sport Chrono, PASM, Sport Exhaust, Sport Seats, PCM Navigation, BOSE Audio, Bi-Xenon with Dynamic Cornering, Park Assist"
        )
    ]
    
    detector = OptionsDetector()
    
    # Process each listing
    for i, listing in enumerate(sample_listings, 1):
        console.print(f"[bold blue]Listing {i}: {listing.model} {listing.trim}[/bold blue]")
        
        # Get options summary
        summary = detector.get_detailed_options_summary(listing.raw_options, listing.trim)
        
        # Update listing with options data
        listing.options_summary = summary
        listing.options_detected = summary['all_options']
        listing.options_value = summary['total_value']
        listing.options_by_category = summary['by_category']
        
        # Display options
        if summary['all_options']:
            console.print(f"[green]Detected Options ({summary['total_options']}):[/green]")
            for option in summary['all_options']:
                console.print(f"  • {option}")
            
            console.print(f"[green]Total Options Value:[/green] ${summary['total_value']:,}")
            
            # Show by category
            if summary['by_category']:
                console.print(f"[green]By Category:[/green]")
                for category, data in summary['by_category'].items():
                    console.print(f"  {category.title()}: {', '.join(data['options'])} (${data['value']:,})")
        else:
            console.print("[yellow]No options detected[/yellow]")
        
        console.print()
        console.print("-" * 80)
        console.print()

def main():
    """Main test function"""
    try:
        test_options_detection()
        test_with_sample_listings()
        
        console.print(Panel("[bold green]All tests completed successfully![/bold green]", style="green"))
        
    except Exception as e:
        console.print(f"[red]Error during testing: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
