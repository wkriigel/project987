#!/usr/bin/env python3
"""
Test both scrapers to verify they're working correctly

PROVIDES: Testing and validation of scraper functionality
DEPENDS: Scraper modules and test data
CONSUMED BY: Development and debugging
CONTRACT: Tests scraper performance and data extraction accuracy
TECH CHOICE: Direct testing with clear pass/fail output
RISK: Low - test files don't affect production code

"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

def test_cars_com_scraper():
    """Test the cars_com.py scraper"""
    print("=== TESTING CARS_COM.PY SCRAPER ===")
    
    try:
        from cars_com import scrape_cars_com
        
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
        
        print(f"Testing URL: {test_url}")
        results = scrape_cars_com([test_url], config)
        
        if results and len(results) > 0:
            result = results[0]
            
            if "error" in result:
                print(f"❌ ERROR: {result['error']}")
                return False
            else:
                print("✅ SUCCESS! Extracted data:")
                print(f"  Price: ${result.get('price_usd', 'N/A')}")
                print(f"  Mileage: {result.get('mileage', 'N/A')}")
                print(f"  Year: {result.get('year', 'N/A')}")
                print(f"  Model: {result.get('model', 'N/A')}")
                print(f"  Trim: {result.get('trim', 'N/A')}")
                print(f"  Transmission: {result.get('transmission_raw', 'N/A')}")
                print(f"  Exterior Color: {result.get('exterior_color', 'N/A')}")
                print(f"  Interior Color: {result.get('interior_color', 'N/A')}")
                print(f"  VIN: {result.get('vin', 'N/A')}")
                return True
        else:
            print("❌ No results returned")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_universal_scraper():
    """Test the updated universal scraper"""
    print("\n=== TESTING UPDATED UNIVERSAL SCRAPER ===")
    
    try:
        from scrapers.universal import UniversalVDPScraper
        from scrapers.profiles import get_site_profile
        
        test_url = "https://www.cars.com/vehicledetail/f36525be-f38b-4213-ad98-f5c0af0d0dba/?aff=atempst"
        
        # Get site profile
        profile = get_site_profile(test_url)
        print(f"Site profile: {profile.name}")
        
        # Test selectors
        print(f"Price selector: {profile.get_selector('price')}")
        print(f"Mileage selector: {profile.get_selector('mileage')}")
        print(f"VIN selector: {profile.get_selector('vin')}")
        print(f"Transmission selector: {profile.get_selector('transmission')}")
        
        # Test extraction functions
        from scrapers.base import extract_price, extract_mileage
        
        test_price = "$24,000 OBO"
        test_mileage = "142,400 mi."
        
        price_result = extract_price(test_price)
        mileage_result = extract_mileage(test_mileage)
        
        print(f"\nExtraction test:")
        print(f"  Price '{test_price}' -> {price_result}")
        print(f"  Mileage '{test_mileage}' -> {mileage_result}")
        
        if price_result == 24000 and mileage_result == 142400:
            print("✅ Extraction functions working correctly")
            return True
        else:
            print("❌ Extraction functions have issues")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test both scrapers"""
    print("Testing both scraper implementations...")
    print("=" * 60)
    
    # Test cars_com.py scraper
    cars_com_success = test_cars_com_scraper()
    
    # Test universal scraper
    universal_success = test_universal_scraper()
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Cars.com scraper: {'✅ WORKING' if cars_com_success else '❌ BROKEN'}")
    print(f"Universal scraper: {'✅ WORKING' if universal_success else '❌ BROKEN'}")
    
    if cars_com_success and universal_success:
        print("\n🎉 Both scrapers are now working correctly!")
        print("The mileage and price extraction issues have been resolved.")
    elif cars_com_success:
        print("\n⚠️  Only the cars_com.py scraper is working.")
        print("The universal scraper still has issues.")
    else:
        print("\n❌ Both scrapers have issues.")
        print("The mileage and price extraction problems persist.")

if __name__ == "__main__":
    main()
