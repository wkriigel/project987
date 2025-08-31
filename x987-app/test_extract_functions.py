#!/usr/bin/env python3
"""
Test the extract_price and extract_mileage functions from base.py

PROVIDES: Testing of price and mileage extraction functions
DEPENDS: Standard library regex module
CONSUMED BY: Development and debugging
CONTRACT: Tests extraction functions with various input formats
TECH CHOICE: Comprehensive test cases with clear pass/fail output
RISK: Low - test files don't affect production code

"""

import re

def extract_price(text: str):
    """Extract price from text - fixed version"""
    if not text:
        return None
    
    # Handle price ranges - take the first price
    if " - " in text or "-" in text or " to " in text:
        # Split on common separators and take first part
        parts = re.split(r"\s*[-–—]\s*|\s+to\s+", text)
        if parts:
            text = parts[0].strip()
    
    # Look for price pattern: $X,XXX or $X,XXX.XX
    match = re.search(r"\$(\d[\d,]+(?:\.\d{2})?)", text)
    if match:
        price_str = match.group(1)
        # Remove commas and convert to int (ignore cents)
        return int(price_str.replace(",", "").split(".")[0])
    
    # Fallback: look for just numbers (no dollar sign)
    match = re.search(r"(\d[\d,]+)", text)
    if match:
        return int(match.group(1).replace(",", ""))
    
    return None

def extract_mileage(text: str):
    """Extract mileage from text - fixed version"""
    if not text:
        return None
    
    # Look for mileage patterns with various units
    patterns = [
        r"(\d[\d,]+)\s*(?:miles?|mi\.?)\b",  # "142,400 mi." or "142,400 miles"
        r"mileage\s*:?\s*(\d[\d,]+)",        # "mileage: 142,400"
        r"(\d[\d,]+)\s*(?:k|K)\s*(?:miles?|mi\.?)\b",  # "142k mi" or "142K mi"
        r"(\d[\d,]+)\s*(?:k|K)\b",           # "142k" or "142K"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value_str = match.group(1)
            value = int(value_str.replace(",", ""))
            
            # Convert k/K to thousands
            if "k" in text.lower():
                value *= 1000
            
            return value
    
    # Fallback: look for just numbers (no units)
    match = re.search(r"(\d[\d,]+)", text)
    if match:
        return int(match.group(1).replace(",", ""))
    
    return None

def test_extract_functions():
    """Test the extract functions to identify issues"""
    
    print("=== TESTING FIXED EXTRACT_PRICE FUNCTION ===")
    
    price_test_cases = [
        ("$24,000", 24000),
        ("$24,500", 24500),
        ("$25,000", 25000),
        ("$24,000 OBO", 24000),
        ("$24,000*", 24000),
        ("$24,000**", 24000),
        ("$24,000+", 24000),
        ("$24,000 - $26,000", 24000),
        ("$24,000-$26,000", 24000),
        ("$24,000 to $26,000", 24000),
        ("$24,000 or best offer", 24000),
        ("$24,000 obo", 24000),
        ("24,000", 24000),
        ("$24k", 24),
        ("$24K", 24),
        ("$24.5k", 24),
        ("$24,000.00", 24000),
        ("$24,000.50", 24000),
        ("$24,000.99", 24000),
    ]
    
    for test_input, expected in price_test_cases:
        actual = extract_price(test_input)
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")
    
    print("\n=== TESTING FIXED EXTRACT_MILEAGE FUNCTION ===")
    
    mileage_test_cases = [
        ("142,400 mi.", 142400),
        ("142,400 miles", 142400),
        ("142,400 mi", 142400),
        ("142,400", 142400),
        ("142,400 mi. (highway)", 142400),
        ("142,400 mi. - highway", 142400),
        ("142,400 mi. city", 142400),
        ("142,400 mi. mixed", 142400),
        ("142400 mi.", 142400),
        ("142.4k mi.", 142400),  # Should convert k to thousands
        ("142.4K mi.", 142400),  # Should convert K to thousands
        ("142k mi.", 142000),    # Should convert k to thousands
        ("142K mi.", 142000),    # Should convert K to thousands
        ("142,400 mi. (estimated)", 142400),
        ("142,400 mi. est.", 142400),
        ("~142,400 mi.", 142400),
        ("~142,400 mi", 142400),
        ("142,400 mi. (odometer)", 142400),
        ("142,400 mi. odo", 142400),
    ]
    
    for test_input, expected in mileage_test_cases:
        actual = extract_mileage(test_input)
        status = "✅" if actual == expected else "❌"
        print(f"{status} Input: '{test_input}' -> Expected: {expected}, Got: {actual}")

if __name__ == "__main__":
    test_extract_functions()
