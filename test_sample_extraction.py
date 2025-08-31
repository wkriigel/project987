#!/usr/bin/env python3
"""
Test unified extractors with the actual sample HTML content
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

def test_sample_extraction():
    """Test unified extractors with the cars.com sample HTML"""
    print("=== TESTING UNIFIED EXTRACTORS WITH SAMPLE HTML ===")
    
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
        
        # Load the sample HTML
        sample_path = "samples/cars_com/sample.html"
        if not os.path.exists(sample_path):
            print(f"Sample file not found: {sample_path}")
            return
        
        with open(sample_path, 'r', encoding='utf-8') as f:
            sample_html = f.read()
        
        print(f"Loaded sample HTML ({len(sample_html)} chars)")
        
        # Extract data from the HTML content
        print("\n--- Extracting Data from Sample HTML ---")
        
        # Extract title and parse it
        title_match = re.search(r'<title>(.*?)</title>', sample_html)
        if title_match:
            title = title_match.group(1)
            print(f"Title: {title}")
            
            # Parse vehicle info from title
            year, model, trim, title_price = extract_vehicle_info_unified(title)
            print(f"  Parsed: Year={year}, Model={model}, Trim={trim}, Price={title_price}")
        
        # Extract mileage
        mileage_match = re.search(r'<dd>(\d[\d,]+ mi\.)</dd>', sample_html)
        if mileage_match:
            mileage_text = mileage_match.group(1)
            mileage = extract_mileage_unified(mileage_text)
            print(f"Mileage text: '{mileage_text}' -> {mileage}")
        
        # Extract price
        price_match = re.search(r'<span class="primary-price"[^>]*>\s*\$([^<]+)</span>', sample_html)
        if price_match:
            price_text = f"${price_match.group(1)}"
            price = extract_price_unified(price_text)
            print(f"Price text: '{price_text}' -> {price}")
        
        # Extract colors
        exterior_match = re.search(r'<dt>Exterior color</dt>\s*<dd>\s*([^<]+)\s*</dd>', sample_html)
        if exterior_match:
            exterior_color = extract_color_unified(exterior_match.group(1).strip())
            print(f"Exterior color: '{exterior_match.group(1).strip()}' -> {exterior_color}")
        
        interior_match = re.search(r'<dt>Interior color</dt>\s*<dd>\s*([^<]+)\s*</dd>', sample_html)
        if interior_match:
            interior_color = extract_color_unified(interior_match.group(1).strip())
            print(f"Interior color: '{interior_match.group(1).strip()}' -> {interior_color}")
        
        # Extract transmission
        transmission_match = re.search(r'<dt>Transmission</dt>\s*<dd>\s*([^<]+)\s*</dd>', sample_html)
        if transmission_match:
            transmission = extract_transmission_unified(transmission_match.group(1).strip())
            print(f"Transmission: '{transmission_match.group(1).strip()}' -> {transmission}")
        
        # Extract VIN
        vin_match = re.search(r'<dt>VIN</dt>\s*<dd>([^<]+)</dd>', sample_html)
        if vin_match:
            vin = extract_vin_unified(vin_match.group(1).strip())
            print(f"VIN: '{vin_match.group(1).strip()}' -> {vin}")
        
        # Test with some edge cases found in the HTML
        print("\n--- Testing Edge Cases from HTML ---")
        
        # Test the "7-Speed A/T" transmission format
        test_transmission = "7-Speed A/T"
        result = extract_transmission_unified(test_transmission)
        print(f"Transmission '{test_transmission}' -> {result}")
        
        # Test the "320.0HP 3.4L Flat 6 Cylinder Engine Gasoline Fuel" engine format
        # This should not match any of our extractors
        test_engine = "320.0HP 3.4L Flat 6 Cylinder Engine Gasoline Fuel"
        result = extract_transmission_unified(test_engine)
        print(f"Engine text '{test_engine}' -> {result}")
        
        # Test the "142,400 mi." mileage format
        test_mileage = "142,400 mi."
        result = extract_mileage_unified(test_mileage)
        print(f"Mileage '{test_mileage}' -> {result}")
        
        # Test the "$24,000" price format
        test_price = "$24,000"
        result = extract_price_unified(test_price)
        print(f"Price '{test_price}' -> {result}")
        
        print("\n✅ Sample extraction test completed!")
        
    except Exception as e:
        print(f"❌ Error in sample extraction test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import re
    test_sample_extraction()
