"""
Test enhanced color extraction capabilities

PROVIDES: Testing of enhanced color extraction system
DEPENDS: Text utility modules and regex patterns
CONSUMED BY: Development and debugging
CONTRACT: Tests comprehensive color extraction with fallback strategies
TECH CHOICE: Multiple extraction strategies with comprehensive test cases
RISK: Low - test files don't affect production code

This test demonstrates the comprehensive color extraction system
implemented from idea.txt, showing multiple fallback strategies
and advanced color pattern matching.
"""

import re
from x987.utils.text import (
    clean_color, none_if_na, normalize_color_phrase, 
    extract_colors_from_text, normalize_color
)

# Test data representing various color extraction scenarios
TEST_CASES = [
    # Basic color extraction
    {
        "name": "Basic labeled colors",
        "text": "Exterior color: Arctic Silver Metallic\nInterior color: Black",
        "expected": ("Arctic Silver Metallic", "Black")
    },
    
    # Complex color phrases
    {
        "name": "Complex color phrases",
        "text": "Exterior: Guards Red\nInterior: Carrera White",
        "expected": ("Guards Red", "Carrera White")
    },
    
    # N/A and invalid values
    {
        "name": "N/A and invalid values",
        "text": "Exterior color: N/A\nInterior color: -",
        "expected": (None, None)
    },
    
    # Pattern matching scenarios
    {
        "name": "Exterior + Interior pattern",
        "text": "Arctic Silver Metallic Exterior Black Interior",
        "expected": ("Arctic Silver Metallic", "Black")
    },
    
    # On/over patterns
    {
        "name": "On/over pattern",
        "text": "Guards Red on Black",
        "expected": ("Guards Red", "Black")
    },
    
    # Mixed strategies
    {
        "name": "Mixed extraction strategies",
        "text": "Exterior color: Meteor Gray\nMeteor Gray Exterior Black Interior",
        "expected": ("Meteor Gray", "Black")
    },
    
    # Porsche-specific colors
    {
        "name": "Porsche-specific colors",
        "text": "Exterior: Basalt Black Metallic\nInterior: Macadamia",
        "expected": ("Basalt Black Metallic", "Macadamia")
    }
]

def test_color_cleaning():
    """Test color cleaning functionality"""
    print("Testing color cleaning...")
    
    # Test valid colors
    assert clean_color("Arctic Silver Metallic") == "Arctic Silver Metallic"
    assert clean_color("  Black  ") == "Black"
    
    # Test invalid colors
    assert clean_color("") == None
    assert clean_color("a") == None
    assert clean_color("ab") == None
    assert clean_color("abc") == "abc"
    
    print("✅ Color cleaning tests passed")

def test_na_detection():
    """Test N/A detection functionality"""
    print("Testing N/A detection...")
    
    # Test N/A variants
    assert none_if_na("N/A") == None
    assert none_if_na("na") == None
    assert none_if_na("notspecified") == None
    assert none_if_na("-") == None
    assert none_if_na("–") == None
    assert none_if_na("—") == None
    
    # Test valid values
    assert none_if_na("Black") == "Black"
    assert none_if_na("  White  ") == "White"
    
    print("✅ N/A detection tests passed")

def test_color_phrase_normalization():
    """Test color phrase normalization"""
    print("Testing color phrase normalization...")
    
    # Test valid color phrases
    assert normalize_color_phrase("Arctic Silver Metallic") == "Arctic Silver Metallic"
    assert normalize_color_phrase("Guards Red") == "Guards Red"
    assert normalize_color_phrase("Basalt Black Metallic") == "Basalt Black Metallic"
    assert normalize_color_phrase("Macadamia") == "Macadamia"
    
    # Test invalid phrases
    assert normalize_color_phrase("") == None
    assert normalize_color_phrase("Random Text") == None
    assert normalize_color_phrase("123") == None
    
    print("✅ Color phrase normalization tests passed")

def test_comprehensive_color_extraction():
    """Test comprehensive color extraction from text"""
    print("Testing comprehensive color extraction...")
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"  Test {i}: {test_case['name']}")
        
        ext_color, int_color = extract_colors_from_text(test_case['text'])
        expected_ext, expected_int = test_case['expected']
        
        # Check exterior color
        if expected_ext:
            assert ext_color == expected_ext, f"Exterior color mismatch: got '{ext_color}', expected '{expected_ext}'"
        else:
            assert ext_color is None, f"Expected no exterior color, got '{ext_color}'"
        
        # Check interior color
        if expected_int:
            assert int_color == expected_int, f"Interior color mismatch: got '{int_color}', expected '{expected_int}'"
        else:
            assert int_color is None, f"Expected no interior color, got '{int_color}'"
        
        print(f"    ✅ Passed")
    
    print("✅ Comprehensive color extraction tests passed")

def test_color_categorization():
    """Test color categorization (Monochrome vs Color)"""
    print("Testing color categorization...")
    
    # Test monochrome colors
    assert normalize_color("Black") == "Monochrome"
    assert normalize_color("White") == "Monochrome"
    assert normalize_color("Gray") == "Monochrome"
    assert normalize_color("Silver") == "Monochrome"
    
    # Test color colors
    assert normalize_color("Red") == "Color"
    assert normalize_color("Blue") == "Color"
    assert normalize_color("Arctic Silver Metallic") == "Monochrome"  # Silver is monochrome
    assert normalize_color("Guards Red") == "Color"  # Red is color
    
    # Test edge cases
    assert normalize_color("") == "Unknown"
    assert normalize_color(None) == "Unknown"
    
    print("✅ Color categorization tests passed")

def run_demo():
    """Run a demonstration of the enhanced color extraction"""
    print("🎨 Enhanced Color Extraction Demo")
    print("=" * 50)
    
    # Sample text with various color patterns
    sample_text = """
    Vehicle Details:
    Exterior color: Arctic Silver Metallic
    Interior color: Black
    Transmission: Manual
    Mileage: 45,000
    
    Additional Info:
    This beautiful Arctic Silver Metallic Exterior Black Interior Porsche
    features Guards Red on Black accents throughout the interior.
    """
    
    print("Sample text:")
    print(sample_text)
    
    # Extract colors using multiple strategies
    ext_color, int_color = extract_colors_from_text(sample_text)
    
    print(f"\nExtracted colors:")
    print(f"  Exterior: {ext_color or 'Not found'}")
    print(f"  Interior: {int_color or 'Not found'}")
    
    # Show categorization
    if ext_color:
        ext_category = normalize_color(ext_color)
        print(f"  Exterior category: {ext_category}")
    
    if int_color:
        int_category = normalize_color(int_color)
        print(f"  Interior category: {int_category}")
    
    print("\n" + "=" * 50)

def main():
    """Run all tests and demo"""
    try:
        print("🚀 Starting Enhanced Color Extraction Tests\n")
        
        # Run individual test functions
        test_color_cleaning()
        test_na_detection()
        test_color_phrase_normalization()
        test_comprehensive_color_extraction()
        test_color_categorization()
        
        print("\n🎉 All tests passed successfully!")
        
        # Run demo
        print("\n" + "=" * 60)
        run_demo()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
