#!/usr/bin/env python3
"""
Test script to debug price and mileage extraction from cars.com sample

PROVIDES: Debugging of price and mileage extraction from sample HTML
DEPENDS: Cars.com scraper and regex patterns
CONSUMED BY: Development and debugging
CONTRACT: Tests extraction logic against sample HTML content
TECH CHOICE: Regex pattern testing with sample data
RISK: Low - test files don't affect production code

"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

from cars_com import _find, _text
from playwright.sync_api import sync_playwright
import re

def test_sample_extraction():
    """Test the current extraction logic against the sample HTML"""
    
    # Read the sample HTML
    with open('samples/cars_com/sample.html', 'r', encoding='utf-8') as f:
        sample_html = f.read()
    
    print("=== SAMPLE HTML CONTENT ===")
    print(sample_html[:1000] + "..." if len(sample_html) > 1000 else sample_html)
    print("\n" + "="*50 + "\n")
    
    # Test the current regex patterns
    print("=== TESTING CURRENT REGEX PATTERNS ===")
    
    # Test price extraction
    price_pattern = r"\$(\d[\d,]+)"
    price_match = re.search(price_pattern, sample_html, re.I | re.S)
    print(f"Price pattern: {price_pattern}")
    print(f"Price match: {price_match.group(1) if price_match else 'None'}")
    
    # Test mileage extraction patterns
    miles_pattern1 = r"(\d[\d,]+)\s*(?:miles|mi)\b"
    miles_pattern2 = r"mileage\s*:?\s*(\d[\d,]+)"
    
    miles_match1 = re.search(miles_pattern1, sample_html, re.I | re.S)
    miles_match2 = re.search(miles_pattern2, sample_html, re.I | re.S)
    
    print(f"\nMileage pattern 1: {miles_pattern1}")
    print(f"Mileage match 1: {miles_match1.group(1) if miles_match1 else 'None'}")
    
    print(f"\nMileage pattern 2: {miles_pattern2}")
    print(f"Mileage match 2: {miles_match2.group(2) if miles_match2 else 'None'}")
    
    # Test the _find function
    print("\n=== TESTING _find FUNCTION ===")
    price = _find(r"\$(\d[\d,]+)", sample_html)
    miles = _find(r"(\d[\d,]+)\s*(?:miles|mi)\b", sample_html) or _find(r"mileage\s*:?\s*(\d[\d,]+)", sample_html)
    
    print(f"Price via _find: {price}")
    print(f"Mileage via _find: {miles}")
    
    # Look for all price-like patterns in the HTML
    print("\n=== ALL PRICE-LIKE PATTERNS IN HTML ===")
    all_prices = re.findall(r'\$[\d,]+', sample_html)
    print(f"All price patterns found: {all_prices}")
    
    # Look for all mileage-like patterns in the HTML
    print("\n=== ALL MILEAGE-LIKE PATTERNS IN HTML ===")
    all_mileages = re.findall(r'\d[\d,]*\s*(?:miles?|mi\.?)', sample_html, re.I)
    print(f"All mileage patterns found: {all_mileages}")
    
    # Look for specific mileage in the basics section
    print("\n=== MILEAGE IN BASICS SECTION ===")
    basics_match = re.search(r'<dt>Mileage</dt>\s*<dd>([^<]+)</dd>', sample_html, re.I | re.S)
    if basics_match:
        print(f"Mileage from basics section: {basics_match.group(1).strip()}")
    
    # Look for price in price section
    print("\n=== PRICE IN PRICE SECTION ===")
    price_section_match = re.search(r'<span class="primary-price"[^>]*>\s*\$([^<]+)</span>', sample_html, re.I | re.S)
    if price_section_match:
        print(f"Price from price section: {price_section_match.group(1).strip()}")

if __name__ == "__main__":
    test_sample_extraction()
