#!/usr/bin/env python3
"""
Test script for report system with enhanced options display

PROVIDES: Testing of report generation with options detection
DEPENDS: Options detector and report generation modules
CONSUMED BY: Development and testing
CONTRACT: Tests report system with enhanced options display
TECH CHOICE: Options detection integration with reporting
RISK: Low - test files don't affect production code

This script tests the report generation with the new options detection system.
"""

from x987.options_v2 import OptionsDetector
from x987.schema import NormalizedListing
from x987.view.report import generate_report

def create_test_listings():
    """Create test listings with various options"""
    
    detector = OptionsDetector()
    
    listings = [
        NormalizedListing(
            timestamp_run_id="test_001",
            source="cars.com",
            listing_url="https://cars.com/listing/1",
            year=2010,
            model="Cayman",
            trim="S",
            transmission_norm="Automatic",
            mileage=45000,
            price_usd=35000,
            exterior_color="Arctic Silver Metallic",
            interior_color="Black",
            color_ext_bucket="Monochrome",
            color_int_bucket="Monochrome",
            raw_options="Sport Chrono Package Plus, PASM adaptive suspension, PSE sport exhaust system, Limited Slip Differential, Sport Seats, Heated Seats, PCM Navigation, BOSE Sound System, Bi-Xenon Headlights, 19 inch wheels, Park Assist sensors"
        ),
        NormalizedListing(
            timestamp_run_id="test_002",
            source="truecar.com",
            listing_url="https://truecar.com/listing/2",
            year=2011,
            model="Cayman",
            trim="R",
            transmission_norm="Manual",
            mileage=30000,
            price_usd=45000,
            exterior_color="Black",
            interior_color="Red",
            color_ext_bucket="Monochrome",
            color_int_bucket="Color",
            raw_options="Sport Chrono Package, PASM, Sport Exhaust, Sport Seats, PCM Navigation, BOSE Audio, Bi-Xenon with Dynamic Cornering, Park Assist"
        ),
        NormalizedListing(
            timestamp_run_id="test_003",
            source="carvana.com",
            listing_url="https://carvana.com/listing/3",
            year=2009,
            model="Boxster",
            trim="S",
            transmission_norm="Automatic",
            mileage=55000,
            price_usd=32000,
            exterior_color="Guards Red",
            interior_color="Black",
            color_ext_bucket="Color",
            color_int_bucket="Monochrome",
            raw_options="Chrono package, adaptive sport suspension, switchable exhaust, bucket seats, seat heating, pcm navigation, bose speakers, litronic headlights, 19 inch alloy wheels, parking assistance"
        ),
        NormalizedListing(
            timestamp_run_id="test_004",
            source="cars.com",
            listing_url="https://cars.com/listing/4",
            year=2012,
            model="Boxster",
            trim="Base",
            transmission_norm="Manual",
            mileage=40000,
            price_usd=28000,
            exterior_color="White",
            interior_color="Black",
            color_ext_bucket="Monochrome",
            color_int_bucket="Monochrome",
            raw_options="Basic model with standard features, manual transmission"
        )
    ]
    
    # Process options for each listing
    for listing in listings:
        summary = detector.get_detailed_options_summary(listing.raw_options, listing.trim)
        listing.options_summary = summary
        listing.options_detected = summary['all_options']
        listing.options_value = summary['total_value']
        listing.options_by_category = summary['by_category']
        
        # Calculate fair value (simplified)
        base_value = 30500 + (listing.year - 2009) * 500
        if listing.trim and listing.trim.lower() == "s":
            base_value += 7000
        listing.fair_value_usd = base_value + listing.options_value
        
        # Calculate deal delta
        if listing.price_usd and listing.fair_value_usd:
            listing.deal_delta_usd = listing.fair_value_usd - listing.price_usd
    
    return listings

def main():
    """Main test function"""
    try:
        print("Creating test listings with enhanced options...")
        listings = create_test_listings()
        
        print(f"Created {len(listings)} test listings")
        print("\nOptions summary:")
        for i, listing in enumerate(listings, 1):
            print(f"\nListing {i}: {listing.model} {listing.trim}")
            print(f"  Options detected: {len(listing.options_detected)}")
            print(f"  Options value: ${listing.options_value:,}")
            print(f"  Fair value: ${listing.fair_value_usd:,}")
            print(f"  Deal delta: ${listing.deal_delta_usd:,}")
            if listing.options_detected:
                print(f"  Top options: {', '.join(listing.options_detected[:3])}")
        
        print("\nGenerating report...")
        generate_report(listings)
        
        print("\nReport generation completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
