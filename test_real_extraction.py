#!/usr/bin/env python3
"""
Test unified extractors with real sample HTML content
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

def test_real_extraction():
    """Test unified extractors with the cars.com sample HTML"""
    print("=== TESTING UNIFIED EXTRACTORS WITH REAL SAMPLE HTML ===")
    
    try:
        from x987.utils.extractors import (
            extract_mileage_unified,
            extract_price_unified,
            extract_color_unified,
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
        
        # Extract and test data from the HTML content
        print("\n--- Testing Data Extraction from Sample HTML ---")
        
        # Test title parsing
        title_match = re.search(r'<title>(.*?)</title>', sample_html)
        if title_match:
            title = title_match.group(1)
            print(f"Title: {title}")
            
            # Parse vehicle info from title
            year, model, trim, title_price = extract_vehicle_info_unified(title)
            print(f"  Parsed: Year={year}, Model={model}, Trim={trim}, Price={title_price}")
        
        # Test mileage extraction
        mileage_match = re.search(r'<dd>(\d[\d,]+ mi\.)</dd>', sample_html)
        if mileage_match:
            mileage_text = mileage_match.group(1)
            mileage = extract_mileage_unified(mileage_text)
            print(f"Mileage text: '{mileage_text}' -> {mileage}")
        
        # Test price extraction
        price_match = re.search(r'<span class="primary-price"[^>]*>\s*\$([^<]+)</span>', sample_html)
        if price_match:
            price_text = f"${price_match.group(1)}"
            price = extract_price_unified(price_text)
            print(f"Price text: '{price_text}' -> {price}")
        
        # Test color extraction
        exterior_match = re.search(r'<dt>Exterior color</dt>\s*<dd>\s*([^<]+)\s*</dd>', sample_html)
        if exterior_match:
            exterior_color = extract_color_unified(exterior_match.group(1).strip())
            print(f"Exterior color: '{exterior_match.group(1).strip()}' -> {exterior_color}")
        
        interior_match = re.search(r'<dt>Interior color</dt>\s*<dd>\s*([^<]+)\s*</dd>', sample_html)
        if interior_match:
            interior_color = extract_color_unified(interior_match.group(1).strip())
            print(f"Interior color: '{interior_match.group(1).strip()}' -> {interior_color}")
        
        # Test transmission extraction
        transmission_match = re.search(r'<dt>Transmission</dt>\s*<dd>\s*([^<]+)\s*</dd>', sample_html)
        if transmission_match:
            transmission = extract_transmission_unified(transmission_match.group(1).strip())
            print(f"Transmission: '{transmission_match.group(1).strip()}' -> {transmission}")
        
        # Test VIN extraction
        vin_match = re.search(r'<dt>VIN</dt>\s*<dd>([^<]+)</dd>', sample_html)
        if vin_match:
            vin = extract_vin_unified(vin_match.group(1).strip())
            print(f"VIN: '{vin_match.group(1).strip()}' -> {vin}")
        
        # Test with specific text patterns found in the HTML
        print("\n--- Testing Specific Patterns from HTML ---")
        
        # Test the "7-Speed A/T" transmission format
        test_transmission = "7-Speed A/T"
        result = extract_transmission_unified(test_transmission)
        print(f"Transmission '{test_transmission}' -> {result}")
        
        # Test the mileage format from the HTML
        test_mileage = "142,400 mi."
        result = extract_mileage_unified(test_mileage)
        print(f"Mileage '{test_mileage}' -> {result}")
        
        # Test the price format from the HTML
        test_price = "$24,000"
        result = extract_price_unified(test_price)
        print(f"Price '{test_price}' -> {result}")
        
        # Test the colors from the HTML
        test_exterior = "Gray"
        result = extract_color_unified(test_exterior)
        print(f"Exterior color '{test_exterior}' -> {result}")
        
        test_interior = "Black"
        result = extract_color_unified(test_interior)
        print(f"Interior color '{test_interior}' -> {result}")
        
        print("\n✅ Real extraction test completed!")
        
    except Exception as e:
        print(f"❌ Error in real extraction test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import re
    test_real_extraction()
