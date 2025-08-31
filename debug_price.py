#!/usr/bin/env python3
"""
Debug price extraction regex

PROVIDES: Debugging and testing of price extraction patterns
DEPENDS: Standard library regex module
CONSUMED BY: Development and debugging
CONTRACT: Tests and validates price extraction regex patterns
TECH CHOICE: Direct regex testing with clear output
RISK: Low - debug files don't affect production code

"""

import re

def debug_price_regex():
    """Debug the price extraction regex pattern"""
    text = "$24,000"
    pattern = r"\$(\d[\d,]+(?:\.\d{2})?)"
    
    print(f"Text: '{text}'")
    print(f"Pattern: '{pattern}'")
    
    match = re.search(pattern, text)
    print(f"Match: {match}")
    
    if match:
        print(f"Group 1: '{match.group(1)}'")
        print(f"Full match: '{match.group(0)}'")
    else:
        print("No match found")
    
    # Test all patterns from extract_price_unified
    patterns = [
        r"price\s*:?\s*\$?(\d[\d,]+)",
        r"asking\s*:?\s*\$?(\d[\d,]+)",
        r"asking\s+(\d[\d,]+)",
        r"\$(\d+(?:\.\d+)?)\s*(?:k|K)",
        r"(\d+(?:\.\d+)?)\s*(?:k|K)\s*dollars?",
        r"(\d+(?:\.\d+)?)\s*(?:k|K)\s*(?:USD|usd)",
        r"\$(\d[\d,]+(?:\.\d{2})?)",
        r"(\d[\d,]+)\s*(?:dollars?|USD|usd)",
        r"(\d[\d,]+)(?=\s*(?:dollars?|USD|usd|$))",
    ]
    
    print(f"\nTesting all patterns:")
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            print(f"  Pattern {i+1}: MATCH - '{match.group(1)}'")
        else:
            print(f"  Pattern {i+1}: NO MATCH")

if __name__ == "__main__":
    debug_price_regex()
