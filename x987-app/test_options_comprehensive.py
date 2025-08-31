#!/usr/bin/env python3
"""
Comprehensive test script for all required options detection

PROVIDES: Comprehensive testing of all required options detection
DEPENDS: Options detector and Rich library
CONSUMED BY: Development and testing
CONTRACT: Tests detection of all specific options mentioned in requirements
TECH CHOICE: Rich library for comprehensive testing output
RISK: Low - test files don't affect production code

This script tests the detection of all the specific options mentioned in the requirements:
- Sport Chrono Package Plus
- Sport Seats / Adaptive Sport Seats  
- Limited Slip Differential (LSD)
- Sport Exhaust (PSE)
- PCM w/ Navigation
- BOSE Surround Sound
- Bi-Xenon Headlights with Dynamic Cornering
- Heated Seats
- Ventilated Seat
- 18–19" Upgraded Wheels
- Park Assist
"""

from x987.options_v2 import OptionsDetector
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def test_all_required_options():
    """Test detection of all required options with various wordings"""
    
    console.print(Panel("[bold cyan]Comprehensive Options Detection Test[/bold cyan]", style="cyan"))
    console.print()
    
    # Create options detector
    detector = OptionsDetector()
    
    # Test scenarios for each required option
    test_scenarios = [
        {
            "name": "Sport Chrono Package Plus",
            "patterns": [
                "Sport Chrono Package Plus", "Sport Chrono Package", "Sport Chrono Plus", 
                "Chrono Package Plus", "Sport Chrono", "Chrono Package", "Chrono Plus", 
                "Chrono", "sport chrono package plus", "chrono package plus", "sport chrono plus"
            ],
            "expected": "Sport Chrono Package Plus"
        },
        {
            "name": "Sport Seats / Adaptive Sport Seats",
            "patterns": [
                "Sport Seats", "Adaptive Sport Seats", "Sport Bucket Seats", 
                "Adaptive Sport Bucket Seats", "Sport Seating", "Adaptive Sport Seating",
                "Sport Seat Package", "sport seats", "adaptive sport seats", "bucket seats", "shell seats"
            ],
            "expected": "Sport Seats / Adaptive Sport Seats"
        },
        {
            "name": "Limited Slip Differential (LSD)",
            "patterns": [
                "Limited Slip Differential", "Limited Slip Differential LSD", "Limited Slip", 
                "LSD", "Locking Diff", "Self-locking Diff", "Mechanical Limited Slip", 
                "Torque Sensing Differential", "limited slip differential", "limited slip", "lsd", "locking diff"
            ],
            "expected": "Limited Slip Differential (LSD)"
        },
        {
            "name": "Sport Exhaust (PSE)",
            "patterns": [
                "PSE", "Sport Exhaust", "Switchable Exhaust", "Performance Exhaust", 
                "Porsche Sport Exhaust", "Sport Exhaust System", "Switchable Sport Exhaust", 
                "Performance Exhaust System", "Sport Exhaust PSE", "pse", "sport exhaust", "switchable exhaust"
            ],
            "expected": "Sport Exhaust (PSE)"
        },
        {
            "name": "PCM w/ Navigation",
            "patterns": [
                "PCM", "Navigation", "Nav System", "Porsche Communication Management", 
                "PCM Navigation", "PCM with Navigation", "PCM w/ Navigation", 
                "Porsche Communication Management Navigation", "PCM System", "Navigation System", 
                "pcm", "navigation", "nav system"
            ],
            "expected": "PCM w/ Navigation"
        },
        {
            "name": "BOSE Surround Sound",
            "patterns": [
                "BOSE", "BOSE Sound System", "BOSE Audio", "BOSE Surround Sound", 
                "BOSE Premium Sound", "BOSE Sound", "BOSE Audio System", "BOSE Speakers", 
                "bose", "bose sound system", "bose audio", "bose surround sound"
            ],
            "expected": "BOSE Surround Sound"
        },
        {
            "name": "Bi-Xenon Headlights with Dynamic Cornering",
            "patterns": [
                "Bi-Xenon", "Litronic", "Cornering Lights", "Xenon Headlights", 
                "Bi-Xenon Headlights", "Dynamic Cornering Lights", "Xenon Lighting", 
                "Bi-Xenon with Dynamic Cornering", "Dynamic Cornering", "Cornering Light System", 
                "bi-xenon", "litronic", "cornering lights"
            ],
            "expected": "Bi-Xenon Headlights with Dynamic Cornering"
        },
        {
            "name": "Heated Seats",
            "patterns": [
                "Heated Seats", "Seat Heating", "Heated Front Seats", "Heated Seating", 
                "Heated Driver Seat", "Heated Passenger Seat", "Heated Seats Package", 
                "heated seats", "seat heating", "heated front seats"
            ],
            "expected": "Heated Seats"
        },
        {
            "name": "Ventilated Seat",
            "patterns": [
                "Ventilated Seats", "Cooled Seats", "Seat Ventilation", "Ventilated Seating", 
                "Cooled Seating", "Ventilated Front Seats", "Seat Cooling", "Ventilated Seats Package", 
                "ventilated seats", "cooled seats", "seat ventilation"
            ],
            "expected": "Ventilated Seat"
        },
        {
            "name": "18–19\" Upgraded Wheels",
            "patterns": [
                "19\"", "18\"", "235/35R19", "265/35R19", "19 Inch", "18 Inch", 
                "19 Inch Wheels", "18 Inch Wheels", "19\" Wheels", "18\" Wheels", 
                "Upgraded Wheels", "Larger Wheels", "19 Inch Alloy", "18 Inch Alloy", 
                "19\" Alloy Wheels", "18\" Alloy Wheels", "19 inch", "18 inch", "19 inch wheels"
            ],
            "expected": "18–19\" Upgraded Wheels"
        },
        {
            "name": "Park Assist",
            "patterns": [
                "Park Assist", "Parking Assist", "Parking Sensors", "Rear Parking Sensors", 
                "Front Parking Sensors", "Parking Aid", "Parking Assistance", "Parking System", 
                "park assist", "parking assist", "parking sensors"
            ],
            "expected": "Park Assist"
        }
    ]
    
    # Test each option
    results = []
    for scenario in test_scenarios:
        console.print(f"Testing: {scenario['name']}")
        
        success_count = 0
        total_patterns = len(scenario['patterns'])
        
        for pattern in scenario['patterns']:
            detected = detector.detect_options(pattern, "S")
            if detected:
                # Check if any detected option matches the expected
                for display, value, category in detected:
                    if scenario['expected'] in display:
                        console.print(f"  ✓ '{pattern}' → {display}")
                        success_count += 1
                        break
                else:
                    console.print(f"  ✗ '{pattern}' → Not detected")
            else:
                console.print(f"  ✗ '{pattern}' → Not detected")
        
        success_rate = (success_count / total_patterns) * 100
        results.append({
            'name': scenario['name'],
            'success_count': success_count,
            'total_patterns': total_patterns,
            'success_rate': success_rate
        })
        
        console.print(f"  Success Rate: {success_count}/{total_patterns} ({success_rate:.1f}%)")
        console.print()
        console.print("-" * 80)
        console.print()
    
    # Summary table
    console.print(Panel("[bold cyan]Detection Success Summary[/bold cyan]", style="cyan"))
    console.print()
    
    table = Table(title="Options Detection Results", box=box.ROUNDED)
    table.add_column("Option", style="cyan", no_wrap=True)
    table.add_column("Success Rate", style="green")
    table.add_column("Success %", style="yellow")
    
    for result in results:
        table.add_row(
            result['name'],
            f"{result['success_count']}/{result['total_patterns']}",
            f"{result['success_rate']:.1f}%"
        )
    
    console.print(table)
    
    # Overall success rate
    overall_success = sum(r['success_count'] for r in results)
    overall_total = sum(r['total_patterns'] for r in results)
    overall_rate = (overall_success / overall_total) * 100
    
    console.print(f"\nOverall Detection Success Rate: {overall_rate:.1f}%")
    
    # Areas for improvement
    console.print("\nAreas for improvement:")
    for result in results:
        if result['success_rate'] < 80:
            console.print(f"  • {result['name']}: {result['success_rate']:.1f}% success rate")
    
    return results


def test_real_world_scenarios():
    """Test with realistic car listing scenarios"""
    
    console.print(Panel("[bold cyan]Real-World Scenarios Test[/bold cyan]", style="cyan"))
    console.print()
    
    detector = OptionsDetector()
    
    # Test scenarios
    scenarios = [
        {
            "name": "High-End Cayman S",
            "text": """This 2011 Porsche Cayman S features the coveted Sport Chrono Package Plus, PASM adaptive suspension, 
and PSE sport exhaust system. Interior includes adaptive sport seats with heating and ventilation, PCM 
navigation system, BOSE surround sound, and bi-xenon headlights with dynamic cornering. Performance upgrades 
include limited slip differential and 19-inch alloy wheels. Convenience features include park assist 
sensors.""",
            "trim": "S"
        },
        {
            "name": "Base Cayman with Options",
            "text": """2009 Porsche Cayman base model with sport seats, heated front seats, PCM with navigation, BOSE audio 
system, xenon headlights, 18-inch wheels, and parking assistance.""",
            "trim": "Base"
        },
        {
            "name": "Cayman R (Standard Features)",
            "text": """2012 Porsche Cayman R - Limited slip differential and 19-inch wheels come standard. Additional options 
include Sport Chrono, PASM, Sport Exhaust, adaptive sport seats, PCM navigation, BOSE sound, bi-xenon 
lighting, and park assist.""",
            "trim": "R"
        }
    ]
    
    for scenario in scenarios:
        console.print(f"Scenario: {scenario['name']}")
        console.print(f"Text: {scenario['text']}")
        console.print(f"Trim: {scenario['trim']}")
        
        detected = detector.detect_options(scenario['text'], scenario['trim'])
        summary = detector.get_detailed_options_summary(scenario['text'], scenario['trim'])
        
        if detected:
            console.print(f"Detected {len(detected)} options:")
            for display, value, category in detected:
                console.print(f"  • {display} (${value:,})")
            
            console.print(f"Total Value: ${summary['total_value']:,}")
        else:
            console.print("No options detected")
        
        console.print()
        console.print("-" * 80)
        console.print()
    
    console.print(Panel("[bold green]All comprehensive tests completed![/bold green]", style="green"))


if __name__ == "__main__":
    # Test individual options
    results = test_all_required_options()
    
    # Test real-world scenarios
    test_real_world_scenarios()
