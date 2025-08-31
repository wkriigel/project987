#!/usr/bin/env python3
"""
Test the current scraper against a real cars.com URL

PROVIDES: Testing of current scraper functionality
DEPENDS: Cars.com scraper module
CONSUMED BY: Development and debugging
CONTRACT: Tests scraper against real URLs for validation
TECH CHOICE: Direct testing with real data sources
RISK: Low - test files don't affect production code

"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

from cars_com import scrape_cars_com

def test_current_scraper():
    """Test the current scraper with a real URL"""
    
    # Test URL from the sample
    test_url = "https://www.cars.com/vehicledetail/f36525be-f38b-4213-ad98-f5c0af0d0dba/?aff=atempst"
    
    config = {
        "polite_delay_ms": 1000,
        "debug": True,
        "network": {
            "block_images": True,
            "block_media": True,
            "block_fonts": True,
            "block_stylesheets": True,
            "block_analytics": True
        }
    }
    
    print(f"Testing scraper with URL: {test_url}")
    print("=" * 60)
    
    try:
        results = scrape_cars_com([test_url], config)
        
        if results and len(results) > 0:
            result = results[0]
            
            if "error" in result:
                print(f"ERROR: {result['error']}")
            else:
                print("SUCCESS! Extracted data:")
                print(f"  Price: ${result.get('price_usd', 'N/A')}")
                print(f"  Mileage: {result.get('mileage', 'N/A')}")
                print(f"  Year: {result.get('year', 'N/A')}")
                print(f"  Model: {result.get('model', 'N/A')}")
                print(f"  Trim: {result.get('trim', 'N/A')}")
                print(f"  Transmission: {result.get('transmission_raw', 'N/A')}")
                print(f"  Exterior Color: {result.get('exterior_color', 'N/A')}")
                print(f"  Interior Color: {result.get('interior_color', 'N/A')}")
                print(f"  VIN: {result.get('vin', 'N/A')}")
                
                if result.get('debug'):
                    print(f"\nDebug info:")
                    print(f"  Trim title: {result.get('_trim_title', 'N/A')}")
                    print(f"  Has 2.9L: {result.get('_has_29L', 'N/A')}")
                    print(f"  Has 3.4L: {result.get('_has_34L', 'N/A')}")
        else:
            print("No results returned")
            
    except Exception as e:
        print(f"Exception occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_current_scraper()
