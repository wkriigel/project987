#!/usr/bin/env python3
"""
Test unified extractors with real sample HTML files
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

def test_unified_extractors_with_real_samples():
    """Test all unified extractors with real sample HTML files"""
    print("=== TESTING UNIFIED EXTRACTORS WITH REAL SAMPLES ===")
    
    try:
        from x987.utils.extractors import (
            extract_mileage_unified,
            extract_price_unified,
            extract_color_unified,
            extract_colors_unified,
            extract_transmission_unified,
            extract_vin_unified,
            extract_vehicle_info_unified
        )
        
        # Test with cars.com sample
        print("\n--- Testing with cars.com sample ---")
        cars_com_sample_path = "samples/cars_com/sample.html"
        
        if os.path.exists(cars_com_sample_path):
            with open(cars_com_sample_path, 'r', encoding='utf-8') as f:
                cars_com_html = f.read()
            
            print(f"Loaded cars.com sample ({len(cars_com_html)} chars)")
            
            # Test mileage extraction
            print("\nTesting mileage extraction:")
            mileage_test_cases = [
                "142,400 mi.",
                "45k miles",
                "12,500 ODO",
                "mileage: 89,000",
                "23.5k mi"
            ]
            
            for test_case in mileage_test_cases:
                result = extract_mileage_unified(test_case)
                print(f"  '{test_case}' -> {result}")
            
            # Test price extraction
            print("\nTesting price extraction:")
            price_test_cases = [
                "$24,000",
                "Asking: $24,000",
                "$24.5k",
                "24.5K USD",
                "Price: $18,500"
            ]
            
            for test_case in price_test_cases:
                result = extract_price_unified(test_case)
                print(f"  '{test_case}' -> {result}")
            
            # Test color extraction
            print("\nTesting color extraction:")
            color_test_cases = [
                "Black",
                "Arctic White",
                "Carrara White",
                "Macadamia Metallic",
                "Guards Red"
            ]
            
            for test_case in color_test_cases:
                result = extract_color_unified(test_case)
                print(f"  '{test_case}' -> {result}")
            
            # Test transmission extraction
            print("\nTesting transmission extraction:")
            transmission_test_cases = [
                "Manual",
                "Automatic",
                "PDK",
                "8-speed automatic",
                "6-speed manual"
            ]
            
            for test_case in transmission_test_cases:
                result = extract_transmission_unified(test_case)
                print(f"  '{test_case}' -> {result}")
            
            # Test VIN extraction
            print("\nTesting VIN extraction:")
            vin_test_cases = [
                "WP0AB2A91FS123456",
                "VIN: WP0AB2A91FS123456",
                "WP0AB2A91FS123456789",
                "Invalid VIN: ABC123"
            ]
            
            for test_case in vin_test_cases:
                result = extract_vin_unified(test_case)
                print(f"  '{test_case}' -> {result}")
            
            # Test vehicle info extraction
            print("\nTesting vehicle info extraction:")
            vehicle_test_cases = [
                "2018 Porsche 911 Carrera S",
                "2020 Porsche 911 Carrera 4S",
                "2019 Porsche 911 GT3 RS",
                "2021 Porsche 911 Turbo S"
            ]
            
            for test_case in vehicle_test_cases:
                year, model, trim = extract_vehicle_info_unified(test_case)
                print(f"  '{test_case}' -> Year: {year}, Model: {model}, Trim: {trim}")
            
            # Test with actual HTML content
            print("\n--- Testing with actual HTML content ---")
            
            # Look for specific patterns in the HTML
            import re
            
            # Find mileage patterns
            mileage_matches = re.findall(r'(\d[\d,]+)\s*(?:miles?|mi\.?|ODO|odo)', cars_com_html, re.IGNORECASE)
            if mileage_matches:
                print(f"Found mileage patterns in HTML: {mileage_matches[:5]}")
                for match in mileage_matches[:3]:
                    result = extract_mileage_unified(match)
                    print(f"  Extracted from '{match}': {result}")
            
            # Find price patterns
            price_matches = re.findall(r'\$(\d[\d,]+)', cars_com_html)
            if price_matches:
                print(f"Found price patterns in HTML: {price_matches[:5]}")
                for match in price_matches[:3]:
                    result = extract_price_unified(f"${match}")
                    print(f"  Extracted from '${match}': {result}")
            
            # Find color patterns
            color_matches = re.findall(r'\b(?:Black|White|Gray|Grey|Silver|Red|Blue|Green|Tan|Beige|Brown|Gold|Purple|Burgundy|Yellow|Orange|Ivory|Cream|Pearl|Metallic)\b', cars_com_html, re.IGNORECASE)
            if color_matches:
                print(f"Found color patterns in HTML: {color_matches[:5]}")
                for match in color_matches[:3]:
                    result = extract_color_unified(match)
                    print(f"  Extracted from '{match}': {result}")
            
        else:
            print(f"cars.com sample not found at {cars_com_sample_path}")
        
        # Test with other samples
        other_samples = ["carvana", "truecar", "carscom"]
        
        for sample_name in other_samples:
            sample_path = f"samples/{sample_name}/sample.html"
            if os.path.exists(sample_path):
                print(f"\n--- Testing with {sample_name} sample ---")
                with open(sample_path, 'r', encoding='utf-8') as f:
                    sample_html = f.read()
                
                print(f"Loaded {sample_name} sample ({len(sample_html)} chars)")
                
                # Quick test of key extractors
                mileage_matches = re.findall(r'(\d[\d,]+)\s*(?:miles?|mi\.?|ODO|odo)', sample_html, re.IGNORECASE)
                if mileage_matches:
                    print(f"  Found mileage: {mileage_matches[0] if mileage_matches else 'None'}")
                
                price_matches = re.findall(r'\$(\d[\d,]+)', sample_html)
                if price_matches:
                    print(f"  Found price: ${price_matches[0] if price_matches else 'None'}")
        
        print("\n✅ All unified extractor tests completed!")
        
    except Exception as e:
        print(f"❌ Error testing unified extractors: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unified_extractors_with_real_samples()
