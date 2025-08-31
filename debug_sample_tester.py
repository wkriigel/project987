#!/usr/bin/env python3
"""
Debug the sample tester to see what's being returned
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

def debug_sample_tester():
    """Debug what the sample tester is returning"""
    print("=== DEBUGGING SAMPLE TESTER ===")
    
    try:
        from x987.pipeline.sample_tester import SampleTester
        
        # Create sample tester
        tester = SampleTester({})
        
        # Test against cars.com sample
        print("Testing against cars.com sample...")
        results = tester.test_source_sample("cars_com")
        
        if "error" in results:
            print(f"Error: {results['error']}")
            return
        
        print(f"\n=== SAMPLE TESTER RESULTS ===")
        print(f"Source: {results.get('source')}")
        print(f"Sample file: {results.get('sample_file')}")
        
        # Check title extraction
        title_tests = results.get("extraction_tests", {}).get("title", {})
        print(f"\n--- Title Tests ---")
        print(f"Title tests: {title_tests}")
        
        if title_tests.get("best_result"):
            print(f"Best title selector: {title_tests['best_result']}")
            best_selector = title_tests["best_result"]
            title_text = title_tests["techniques"][best_selector]["text"]
            print(f"Title text: '{title_text}'")
            
            # Test our unified extractor
            from x987.utils.extractors import extract_vehicle_info_unified
            year, model, trim, title_price = extract_vehicle_info_unified(title_text)
            print(f"Parsed: Year={year}, Model={model}, Trim={trim}, Price={title_price}")
        
        # Check field extraction
        field_tests = results.get("extraction_tests", {}).get("fields", {})
        print(f"\n--- Field Tests ---")
        
        # Mileage
        mileage_tests = field_tests.get("mileage", {})
        print(f"Mileage: {mileage_tests}")
        
        # VIN
        vin_tests = field_tests.get("vin", {})
        print(f"VIN: {vin_tests}")
        
        # Transmission
        transmission_tests = field_tests.get("transmission", {})
        print(f"Transmission: {transmission_tests}")
        
        # Price
        price_tests = field_tests.get("price", {})
        print(f"Price: {price_tests}")
        
        # Colors
        color_tests = field_tests.get("colors", {})
        print(f"Colors: {color_tests}")
        
        # Overview
        overview_tests = results.get("extraction_tests", {}).get("overview", {})
        print(f"\n--- Overview Tests ---")
        print(f"Overview: {overview_tests}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_sample_tester()
