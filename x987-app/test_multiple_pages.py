#!/usr/bin/env python3
"""
Test multiple cars.com pages to identify any specific issues

PROVIDES: Testing of multiple cars.com pages for issue identification
DEPENDS: Cars.com scraper module and test data
CONSUMED BY: Development and debugging
CONTRACT: Tests scraper against multiple real URLs for validation
TECH CHOICE: Multiple page testing with polite delays
RISK: Low - test files don't affect production code

"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

from cars_com import scrape_cars_com
import time

def test_multiple_pages():
    """Test multiple cars.com pages to identify issues"""
    
    # Test URLs - these should be real cars.com Porsche listings
    test_urls = [
        # URL from our sample
        "https://www.cars.com/vehicledetail/f36525be-f38b-4213-ad98-f5c0af0d0dba/?aff=atempst",
        
        # Add more real cars.com Porsche URLs here
        # "https://www.cars.com/vehicledetail/ANOTHER_ID/",
        # "https://www.cars.com/vehicledetail/YET_ANOTHER_ID/",
    ]
    
    config = {
        "polite_delay_ms": 2000,  # Be more polite for multiple pages
        "debug": True,
        "network": {
            "block_images": True,
            "block_media": True,
            "block_fonts": True,
            "block_stylesheets": True,
            "block_analytics": True
        }
    }
    
    print(f"Testing {len(test_urls)} cars.com pages")
    print("=" * 60)
    
    all_results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n--- Testing Page {i}/{len(test_urls)} ---")
        print(f"URL: {url}")
        
        try:
            start_time = time.time()
            results = scrape_cars_com([url], config)
            end_time = time.time()
            
            if results and len(results) > 0:
                result = results[0]
                
                if "error" in result:
                    print(f"❌ ERROR: {result['error']}")
                    all_results.append({"url": url, "error": result['error']})
                else:
                    print(f"✅ SUCCESS in {end_time - start_time:.1f}s")
                    print(f"  Price: ${result.get('price_usd', 'N/A')}")
                    print(f"  Mileage: {result.get('mileage', 'N/A')}")
                    print(f"  Year: {result.get('year', 'N/A')}")
                    print(f"  Model: {result.get('model', 'N/A')}")
                    print(f"  Trim: {result.get('trim', 'N/A')}")
                    print(f"  Transmission: {result.get('transmission_raw', 'N/A')}")
                    print(f"  Exterior Color: {result.get('exterior_color', 'N/A')}")
                    print(f"  Interior Color: {result.get('interior_color', 'N/A')}")
                    print(f"  VIN: {result.get('vin', 'N/A')}")
                    
                    # Check for any missing critical data
                    missing_fields = []
                    if not result.get('price_usd'):
                        missing_fields.append('price')
                    if not result.get('mileage'):
                        missing_fields.append('mileage')
                    if not result.get('year'):
                        missing_fields.append('year')
                    if not result.get('model'):
                        missing_fields.append('model')
                    
                    if missing_fields:
                        print(f"  ⚠️  Missing fields: {', '.join(missing_fields)}")
                    
                    all_results.append({
                        "url": url,
                        "success": True,
                        "data": result,
                        "missing_fields": missing_fields
                    })
            else:
                print("❌ No results returned")
                all_results.append({"url": url, "error": "No results returned"})
                
        except Exception as e:
            print(f"❌ Exception occurred: {e}")
            import traceback
            traceback.print_exc()
            all_results.append({"url": url, "error": str(e)})
        
        # Be polite between requests
        if i < len(test_urls):
            print("Waiting 3 seconds before next request...")
            time.sleep(3)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for r in all_results if r.get("success"))
    total = len(all_results)
    
    print(f"Total pages tested: {total}")
    print(f"Successful extractions: {successful}")
    print(f"Failed extractions: {total - successful}")
    print(f"Success rate: {successful/total*100:.1f}%")
    
    if successful < total:
        print("\nFailed extractions:")
        for result in all_results:
            if not result.get("success"):
                print(f"  ❌ {result['url']}: {result.get('error', 'Unknown error')}")
    
    # Check for common issues
    print("\nData quality analysis:")
    for result in all_results:
        if result.get("success"):
            data = result["data"]
            missing = result.get("missing_fields", [])
            if missing:
                print(f"  ⚠️  {result['url']}: Missing {', '.join(missing)}")
            else:
                print(f"  ✅ {result['url']}: All fields present")

if __name__ == "__main__":
    test_multiple_pages()
