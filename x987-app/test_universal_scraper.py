#!/usr/bin/env python3
"""
Test the universal scraper to see what selectors it's using

PROVIDES: Testing of universal scraper selectors and extraction
DEPENDS: Regex patterns and extraction functions
CONSUMED BY: Development and testing
CONTRACT: Tests universal scraper extraction functionality
TECH CHOICE: Regex-based extraction testing
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

def test_universal_scraper():
    """Test the universal scraper selectors and extraction"""
    
    print("=== TESTING UNIVERSAL SCRAPER EXTRACTION FUNCTIONS ===")
    
    # Test price extraction
    test_prices = [
        "$24,000",
        "$24,000 OBO", 
        "$24,000 - $26,000",
        "$24,000.50"
    ]
    
    print("Price extraction:")
    for price_text in test_prices:
        result = extract_price(price_text)
        print(f"  '{price_text}' -> {result}")
    
    # Test mileage extraction
    test_mileages = [
        "142,400 mi.",
        "142,400 miles",
        "142k mi.",
        "142,400"
    ]
    
    print("\nMileage extraction:")
    for mileage_text in test_mileages:
        result = extract_mileage(mileage_text)
        print(f"  '{mileage_text}' -> {result}")
    
    print("\n=== ANALYZING SAMPLE HTML SELECTORS ===")
    
    # Based on our sample HTML, here are the actual selectors that would work:
    sample_selectors = {
        "title": "h1.listing-title",  # "2010 Porsche Cayman S"
        "price": ".primary-price",    # "$24,000"
        "mileage": ".listing-mileage", # "142,400 mi."
        "vin": "dd",                   # VIN from basics section
        "transmission": "dd",          # Transmission from basics section
        "exterior_color": "dd",        # Exterior color from basics section
        "interior_color": "dd"         # Interior color from basics section
    }
    
    print("Sample HTML selectors that would work:")
    for field, selector in sample_selectors.items():
        print(f"  {field}: {selector}")
    
    print("\n=== ISSUE ANALYSIS ===")
    print("The universal scraper is looking for:")
    print("  - .listing-overview .mileage (but sample has .listing-mileage)")
    print("  - .listing-overview .vin (but sample has dd in basics section)")
    print("  - .listing-overview .transmission (but sample has dd in basics section)")
    print("\nThe working cars_com.py scraper uses:")
    print("  - Regex patterns that work regardless of HTML structure")
    print("  - _dd_for() function for structured data")
    print("  - Fallback regex patterns for text extraction")

if __name__ == "__main__":
    test_universal_scraper()
