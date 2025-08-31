#!/usr/bin/env python3
"""
Direct test of unified extractors with sample HTML
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

def test_direct_extraction():
    """Test unified extractors directly with sample HTML"""
    print("=== DIRECT TEST OF UNIFIED EXTRACTORS ===")
    
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
        
        # Test direct extraction from HTML content
        print("\n--- Testing Direct Extraction ---")
        
        # Test mileage extraction
        mileage_match = re.search(r'<dd>(\d[\d,]+ mi\.)</dd>', sample_html)
        if mileage_match:
            mileage_text = mileage_match.group(1)
            mileage = extract_mileage_unified(mileage_text)
            print(f"✅ Mileage: '{mileage_text}' -> {mileage}")
        
        # Test price extraction
        price_match = re.search(r'<span class="primary-price"[^>]*>\s*\$([^<]+)</span>', sample_html)
        if price_match:
            price_text = f"${price_match.group(1)}"
            price = extract_price_unified(price_text)
            print(f"✅ Price: '{price_text}' -> {price}")
        
        # Test VIN extraction
        vin_match = re.search(r'<dt>VIN</dt>\s*<dd>([^<]+)</dd>', sample_html)
        if vin_match:
            vin_text = vin_match.group(1).strip()
            vin = extract_vin_unified(vin_text)
            print(f"✅ VIN: '{vin_text}' -> {vin}")
        
        # Test transmission extraction
        transmission_match = re.search(r'<dt>Transmission</dt>\s*<dd>\s*([^<]+)\s*</dd>', sample_html)
        if transmission_match:
            transmission_text = transmission_match.group(1).strip()
            transmission = extract_transmission_unified(transmission_text)
            print(f"✅ Transmission: '{transmission_text}' -> {transmission}")
        
        # Test color extraction
        exterior_match = re.search(r'<dt>Exterior color</dt>\s*<dd>\s*([^<]+)\s*</dd>', sample_html)
        if exterior_match:
            exterior_text = exterior_match.group(1).strip()
            exterior_color = extract_color_unified(exterior_text)
            print(f"✅ Exterior: '{exterior_text}' -> {exterior_color}")
        
        interior_match = re.search(r'<dt>Interior color</dt>\s*<dd>\s*([^<]+)</dd>', sample_html)
        if interior_match:
            interior_text = interior_match.group(1).strip()
            interior_color = extract_color_unified(interior_text)
            print(f"✅ Interior: '{interior_text}' -> {interior_color}")
        
        # Test title parsing
        title_match = re.search(r'<title>(.*?)</title>', sample_html)
        if title_match:
            title = title_match.group(1)
            print(f"\n--- Title Parsing ---")
            print(f"Title: {title}")
            
            year, model, trim, title_price = extract_vehicle_info_unified(title)
            print(f"✅ Parsed: Year={year}, Model={model}, Trim={trim}, Price={title_price}")
        
        print("\n✅ Direct extraction test completed!")
        
    except Exception as e:
        print(f"❌ Error in direct extraction test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import re
    test_direct_extraction()
