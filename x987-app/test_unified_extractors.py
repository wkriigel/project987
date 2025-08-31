"""
Test unified data extractors

PROVIDES: Comprehensive testing of all unified extraction functions
DEPENDS: utils.extractors module
CONSUMED BY: Development and debugging
CONTRACT: Ensures extraction functions work correctly
TECH CHOICE: Comprehensive test cases with clear pass/fail output
RISK: Low - test files don't affect production code

"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

from x987.utils.extractors import (
    extract_mileage_unified, extract_price_unified, extract_color_unified,
    extract_colors_unified, extract_transmission_unified, extract_vin_unified,
    extract_vehicle_info_unified, clean_text_unified, none_if_na_unified
)

def test_mileage_extraction():
    """Test unified mileage extraction"""
    print("=== TESTING UNIFIED MILEAGE EXTRACTION ===")
    
    test_cases = [
        # Standard formats
        ("142,400 mi.", 142400),
        ("142,400 miles", 142400),
        ("142,400 mi", 142400),
        ("142,400", 142400),
        ("142,400 mi. (highway)", 142400),
        ("142,400 mi. - highway", 142400),
        ("142,400 mi. city", 142400),
        ("142,400 mi. mixed", 142400),
        ("142400 mi.", 142400),
        
        # k/K formats
        ("142.4k mi.", 142400),
        ("142.4K mi.", 142400),
        ("142k mi.", 142000),
        ("142K mi.", 142000),
        ("142k", 142000),
        ("142K", 142000),
        
        # ODO formats
        ("142,400 ODO", 142400),
        ("142,400 odo", 142400),
        ("142,400 mi. (odometer)", 142400),
        ("142,400 mi. odo", 142400),
        
        # Labeled formats
        ("mileage: 142,400", 142400),
        ("Mileage: 142,400", 142400),
        ("odometer: 142,400", 142400),
        ("Odometer: 142,400", 142400),
        
        # Edge cases
        ("~142,400 mi.", 142400),
        ("~142,400 mi", 142400),
        ("142,400 mi. (estimated)", 142400),
        ("142,400 mi. est.", 142400),
        ("142,400 mi. (odometer)", 142400),
        
        # Invalid cases
        ("", None),
        ("No mileage", None),
        ("Unknown", None),
        ("TBD", None),
        ("9999999 mi.", None),  # Too high
        ("-1000 mi.", None),    # Negative
    ]
    
    for test_input, expected in test_cases:
        actual = extract_mileage_unified(test_input)
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")

def test_price_extraction():
    """Test unified price extraction"""
    print("\n=== TESTING UNIFIED PRICE EXTRACTION ===")
    
    test_cases = [
        # Standard formats
        ("$24,000", 24000),
        ("$24,500", 24500),
        ("$25,000", 25000),
        ("$24,000 OBO", 24000),
        ("$24,000*", 24000),
        ("$24,000**", 24000),
        ("$24,000+", 24000),
        ("$24,000.00", 24000),
        ("$24,000.50", 24000),
        ("$24,000.99", 24000),
        
        # k/K formats
        ("$24k", 24000),
        ("$24K", 24000),
        ("$24.5k", 24500),
        ("$24.5K", 24500),
        ("24k dollars", 24000),
        ("24.5K USD", 24500),
        
        # Labeled formats
        ("Price: $24,000", 24000),
        ("price: $24,000", 24000),
        ("Asking: $24,000", 24000),
        ("asking: $24,000", 24000),
        
        # Price ranges (should take first)
        ("$24,000 - $26,000", 24000),
        ("$24,000-$26,000", 24000),
        ("$24,000 to $26,000", 24000),
        ("$24,000 or best offer", 24000),
        ("$24,000 obo", 24000),
        
        # No dollar sign
        ("24,000", 24000),
        ("24,000 dollars", 24000),
        ("24,000 USD", 24000),
        
        # Invalid cases
        ("", None),
        ("No price", None),
        ("Contact for price", None),
        ("TBD", None),
        ("$9999999", None),  # Too high
        ("$-1000", None),    # Negative
    ]
    
    for test_input, expected in test_cases:
        actual = extract_price_unified(test_input)
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")

def test_color_extraction():
    """Test unified color extraction"""
    print("\n=== TESTING UNIFIED COLOR EXTRACTION ===")
    
    test_cases = [
        # Basic colors
        ("Black", "Black"),
        ("White", "White"),
        ("Red", "Red"),
        ("Blue", "Blue"),
        ("Silver", "Silver"),
        
        # Advanced colors
        ("Arctic White", "Arctic White"),
        ("Black Metallic", "Black Metallic"),
        ("Carrara White", "Carrara White"),
        ("Macadamia", "Macadamia"),
        ("Cognac", "Cognac"),
        
        # Special cases
        ("", None),
        ("Unknown", None),
        ("TBD", None),
        ("N/A", None),
    ]
    
    for test_input, expected in test_cases:
        actual = extract_color_unified(test_input)
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")

def test_colors_extraction():
    """Test unified colors extraction (exterior + interior)"""
    print("\n=== TESTING UNIFIED COLORS EXTRACTION ===")
    
    test_cases = [
        # Labeled formats
        ("Exterior Color: Arctic White Interior Color: Black", ("Arctic White", "Black")),
        ("exterior color: Black Metallic interior color: Macadamia", ("Black Metallic", "Macadamia")),
        
        # Combined formats
        ("Arctic White Exterior Black Interior", ("Arctic White", "Black")),
        ("Black Metallic Exterior Macadamia Interior", ("Black Metallic", "Macadamia")),
        
        # On/over formats
        ("Arctic White on Black", ("Arctic White", "Black")),
        ("Black Metallic over Macadamia", ("Black Metallic", "Macadamia")),
        
        # Edge cases
        ("", (None, None)),
        ("No colors", (None, None)),
    ]
    
    for test_input, expected in test_cases:
        actual = extract_colors_unified(test_input)
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")

def test_transmission_extraction():
    """Test unified transmission extraction"""
    print("\n=== TESTING UNIFIED TRANSMISSION EXTRACTION ===")
    
    test_cases = [
        # Porsche-specific
        ("PDK", "PDK"),
        ("pdk", "PDK"),
        ("Tiptronic", "Tiptronic"),
        ("tiptronic", "Tiptronic"),
        
        # Standard
        ("Automatic", "Automatic"),
        ("automatic", "Automatic"),
        ("Auto", "Automatic"),
        ("auto", "Automatic"),
        ("Manual", "Manual"),
        ("manual", "Manual"),
        
        # Edge cases
        ("", None),
        ("Unknown", None),
        ("TBD", None),
    ]
    
    for test_input, expected in test_cases:
        actual = extract_transmission_unified(test_input)
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")

def test_vin_extraction():
    """Test unified VIN extraction"""
    print("\n=== TESTING UNIFIED VIN EXTRACTION ===")
    
    test_cases = [
        # Labeled formats
        ("VIN: WP0AB2A91FS123456", "WP0AB2A91FS123456"),
        ("vin: WP0AB2A91FS123456", "WP0AB2A91FS123456"),
        
        # Standalone
        ("WP0AB2A91FS123456", "WP0AB2A91FS123456"),
        ("WP0AB2A91FS123456 is the VIN", "WP0AB2A91FS123456"),
        
        # Edge cases
        ("", None),
        ("No VIN", None),
        ("Unknown", None),
        ("WP0AB2A91FS123456789", None),  # Too long
        ("WP0AB2A91FS12345", None),     # Too short
    ]
    
    for test_input, expected in test_cases:
        actual = extract_vin_unified(test_input)
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")

def test_vehicle_info_extraction():
    """Test unified vehicle info extraction"""
    print("\n=== TESTING UNIFIED VEHICLE INFO EXTRACTION ===")
    
    test_cases = [
        # Standard formats
        ("2015 Porsche Cayman", (2015, "Cayman", "Base")),
        ("2016 Porsche Boxster", (2016, "Boxster", "Base")),
        ("2017 Porsche Cayman S", (2017, "Cayman", "S")),
        ("2018 Porsche Boxster S", (2018, "Boxster", "S")),
        
        # Special trims
        ("2019 Porsche Cayman R", (2019, "Cayman", "R")),
        ("2020 Porsche Boxster Spyder", (2020, "Boxster", "Spyder")),
        ("2021 Porsche Cayman Black Edition", (2021, "Cayman", "Black Edition")),
        
        # Edge cases
        ("", (None, None, None)),
        ("Porsche Cayman", (None, "Cayman", "Base")),
        ("2015 Porsche", (2015, None, None)),
    ]
    
    for test_input, expected in test_cases:
        actual = extract_vehicle_info_unified(test_input)
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")

def test_utility_functions():
    """Test utility functions"""
    print("\n=== TESTING UTILITY FUNCTIONS ===")
    
    # Test clean_text_unified
    print("Testing clean_text_unified:")
    test_input = "  Multiple    spaces   and\ttabs  "
    expected = "Multiple spaces and tabs"
    actual = clean_text_unified(test_input)
    status = "✅" if actual == expected else "❌"
    print(f"{status} Input: '{test_input}' -> Expected: '{expected}', Got: '{actual}'")
    
    # Test none_if_na_unified
    print("Testing none_if_na_unified:")
    test_cases = [
        ("N/A", None),
        ("na", None),
        ("Unknown", None),
        ("TBD", None),
        ("Valid text", "Valid text"),
        ("", None),
    ]
    
    for test_input, expected in test_cases:
        actual = none_if_na_unified(test_input)
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")

def main():
    """Run all tests"""
    print("🧪 TESTING UNIFIED DATA EXTRACTORS")
    print("=" * 50)
    
    test_mileage_extraction()
    test_price_extraction()
    test_color_extraction()
    test_colors_extraction()
    test_transmission_extraction()
    test_vin_extraction()
    test_vehicle_info_extraction()
    test_utility_functions()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
