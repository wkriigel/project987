#!/usr/bin/env python3
"""
Test edge cases for price and mileage extraction

PROVIDES: Testing of edge cases for data extraction functions
DEPENDS: Standard library regex module
CONSUMED BY: Development and debugging
CONTRACT: Tests extraction patterns against challenging input data
TECH CHOICE: Comprehensive test cases with clear pass/fail output
RISK: Low - test files don't affect production code

"""

import re

def test_edge_cases():
    """Test various edge cases for price and mileage extraction"""
    
    # Test cases for price extraction
    price_test_cases = [
        # Standard cases
        ("$24,000", "24000"),
        ("$24,500", "24500"),
        ("$25,000", "25000"),
        
        # Edge cases that might appear
        ("$24,000 OBO", "24000"),  # With OBO
        ("$24,000*", "24000"),     # With asterisk
        ("$24,000**", "24000"),    # With double asterisk
        ("$24,000+", "24000"),     # With plus
        ("$24,000 - $26,000", "24000"),  # Price range (should get first)
        ("$24,000-$26,000", "24000"),    # Price range no spaces
        ("$24,000 to $26,000", "24000"), # Price range with "to"
        ("$24,000 or best offer", "24000"), # With OBO text
        ("$24,000 obo", "24000"),  # Lowercase OBO
        
        # Different formats
        ("24,000", "24000"),       # No dollar sign
        ("$24k", "24"),            # K format (should fail)
        ("$24K", "24"),            # K format uppercase (should fail)
        ("$24.5k", "24"),          # Decimal K format (should fail)
        
        # Problematic cases
        ("$24,000.00", "24000"),  # With cents
        ("$24,000.50", "24000"),  # With cents
        ("$24,000.99", "24000"),  # With cents
    ]
    
    # Test cases for mileage extraction
    mileage_test_cases = [
        # Standard cases
        ("142,400 mi.", "142400"),
        ("142,400 miles", "142400"),
        ("142,400 mi", "142400"),
        ("142,400", "142400"),     # Just the number
        
        # Edge cases
        ("142,400 mi. (highway)", "142400"),  # With context
        ("142,400 mi. - highway", "142400"),  # With dash context
        ("142,400 mi. city", "142400"),       # With city context
        ("142,400 mi. mixed", "142400"),      # With mixed context
        
        # Different formats
        ("142400 mi.", "142400"),  # No comma
        ("142.4k mi.", "142"),     # K format (should fail)
        ("142.4K mi.", "142"),     # K format uppercase (should fail)
        ("142k mi.", "142"),       # K format (should fail)
        ("142K mi.", "142"),       # K format uppercase (should fail)
        
        # Problematic cases
        ("142,400 mi. (estimated)", "142400"),  # With estimated
        ("142,400 mi. est.", "142400"),         # With est.
        ("~142,400 mi.", "142400"),             # With tilde
        ("~142,400 mi", "142400"),              # With tilde no period
        ("142,400 mi. (odometer)", "142400"),   # With odometer
        ("142,400 mi. odo", "142400"),          # With odo
    ]
    
    print("=== TESTING PRICE EXTRACTION EDGE CASES ===")
    price_pattern = r"\$(\d[\d,]+)"
    
    for test_input, expected in price_test_cases:
        match = re.search(price_pattern, test_input, re.I | re.S)
        actual = match.group(1).replace(",", "") if match else "None"
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")
    
    print("\n=== TESTING MILEAGE EXTRACTION EDGE CASES ===")
    mileage_pattern1 = r"(\d[\d,]+)\s*(?:miles|mi)\b"
    mileage_pattern2 = r"mileage\s*:?\s*(\d[\d,]+)"
    
    for test_input, expected in mileage_test_cases:
        match1 = re.search(mileage_pattern1, test_input, re.I | re.S)
        match2 = re.search(mileage_pattern2, test_input, re.I | re.S)
        
        actual = None
        if match1:
            actual = match1.group(1).replace(",", "")
        elif match2:
            actual = match2.group(1).replace(",", "")
        
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")
    
    print("\n=== TESTING IMPROVED PATTERNS ===")
    
    # Improved price pattern that handles more edge cases
    improved_price_pattern = r"\$(\d[\d,]+(?:\.\d{2})?)"
    
    print("\nImproved price pattern:", improved_price_pattern)
    for test_input, expected in price_test_cases:
        match = re.search(improved_price_pattern, test_input, re.I | re.S)
        actual = match.group(1).replace(",", "").split(".")[0] if match else "None"
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")
    
    # Improved mileage pattern that handles more edge cases
    improved_mileage_pattern = r"(\d[\d,]+)\s*(?:miles?|mi\.?)\b"
    
    print("\nImproved mileage pattern:", improved_mileage_pattern)
    for test_input, expected in mileage_test_cases:
        match = re.search(improved_mileage_pattern, test_input, re.I | re.S)
        actual = match.group(1).replace(",", "") if match else "None"
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")

if __name__ == "__main__":
    test_edge_cases()
