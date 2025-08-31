#!/usr/bin/env python3
"""
Test Single Option File

PROVIDES: Testing of single option file functionality
DEPENDS: Sport chrono option module
CONSUMED BY: Development and testing
CONTRACT: Tests individual option file behavior
TECH CHOICE: Direct option testing with clear output
RISK: Low - test files don't affect production code

This script demonstrates how a single option file works when its option is found.
"""

from x987.options.sport_chrono import SPORT_CHRONO_OPTION

def test_sport_chrono_option():
    """Test the Sport Chrono option file"""
    
    print("=== SPORT CHRONO OPTION FILE OUTPUT ===")
    print(f"File: sport_chrono.py")
    print(f"ID: {SPORT_CHRONO_OPTION.get_id()}")
    print(f"Display: {SPORT_CHRONO_OPTION.get_display()}")
    print(f"Category: {SPORT_CHRONO_OPTION.get_category()}")
    print(f"Base Value: ${SPORT_CHRONO_OPTION.get_value('test')}")
    print()
    
    print("Testing with different text:")
    
    # Test 1: Option is present
    test_text1 = "Sport Chrono Package Plus"
    is_present1 = SPORT_CHRONO_OPTION.is_present(test_text1)
    value1 = SPORT_CHRONO_OPTION.get_value(test_text1)
    print(f'"{test_text1}" -> Is Present: {is_present1} -> Value: ${value1}')
    
    # Test 2: Option is present (different wording)
    test_text2 = "Chrono Package"
    is_present2 = SPORT_CHRONO_OPTION.is_present(test_text2)
    value2 = SPORT_CHRONO_OPTION.get_value(test_text2)
    print(f'"{test_text2}" -> Is Present: {is_present2} -> Value: ${value2}')
    
    # Test 3: Option is not present
    test_text3 = "Just some text"
    is_present3 = SPORT_CHRONO_OPTION.is_present(test_text3)
    value3 = SPORT_CHRONO_OPTION.get_value(test_text3)
    print(f'"{test_text3}" -> Is Present: {is_present3} -> Value: ${value3}')
    
    print()
    print("Patterns this option looks for:")
    for i, pattern in enumerate(SPORT_CHRONO_OPTION.patterns, 1):
        print(f"  {i}. {pattern}")

if __name__ == "__main__":
    test_sport_chrono_option()
