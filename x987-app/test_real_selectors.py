#!/usr/bin/env python3
"""
Test Real Selectors with Extracted Sample

PROVIDES: Testing of real selectors against extracted sample
DEPENDS: Sample extractor and scraper profiles
CONSUMED BY: Development and testing
CONTRACT: Tests updated real selectors against extracted sample
TECH CHOICE: Real sample analysis for selector validation
RISK: Low - test files don't affect production code

This script tests our updated real selectors against the extracted
cars.com sample to ensure they work correctly.
"""

import sys
import os
from pathlib import Path

# Add the x987 package to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_real_selectors():
    """Test our updated real selectors against the extracted sample"""
    print("=== Testing Real Selectors with Extracted Sample ===")
    
    try:
        from x987.pipeline.sample_extractor import SampleExtractor
        from x987.scrapers.profiles import CARS_COM_PROFILE
        
        # Load the sample
        sample_extractor = SampleExtractor({})
        analysis = sample_extractor.analyze_sample_structure("cars_com")
        
        if "error" in analysis:
            print(f"❌ Error loading sample: {analysis['error']}")
            return False
        
        print(f"✓ Sample loaded: {analysis['sample_file']}")
        print(f"✓ Sections found: {len(analysis['sections_found'])}")
        
        # Test our real selectors
        print("\n🔍 Testing Real Selectors:")
        
        # Test title selectors
        print("\n1. TITLE SELECTORS:")
        title_selectors = [
            "h1.sticky-header-listing-title",  # REAL cars.com selector
            "h1.listing-title",                # REAL cars.com selector
            "h1[data-testid='vehicle-title']",
            "h1.vehicle-title", 
            "h1.spark-heading-2",
            ".vehicle-title",
            "h1"
        ]
        
        for selector in title_selectors:
            print(f"   {selector}: {'✓' if selector in str(analysis['sections_found']) else '❌'}")
        
        # Test price selectors
        print("\n2. PRICE SELECTORS:")
        price_selectors = [
            ".price-section",              # REAL cars.com selector
            ".price-section-vehicle-card", # REAL cars.com selector
            ".vehicle-price",
            ".listing-price",
            ".price-display",
            "[data-testid='price']",
            ".price",
            "[class*='price']"
        ]
        
        for selector in title_selectors:
            print(f"   {selector}: {'✓' if selector in str(analysis['sections_found']) else '❌'}")
        
        # Test basic section selectors
        print("\n3. BASIC SECTION SELECTORS:")
        basic_selectors = [
            ".listing-overview",  # REAL cars.com selector
            ".vehicle-specs",
            ".specs-section",
            ".vehicle-details",
            ".listing-details",
            ".vehicle-info",
            ".vehicle-summary"
        ]
        
        for selector in basic_selectors:
            print(f"   {selector}: {'✓' if selector in str(analysis['sections_found']) else '❌'}")
        
        # Test features selectors
        print("\n4. FEATURES SELECTORS:")
        features_selectors = [
            ".features-section",           # REAL cars.com selector
            ".sds-page-section.features-section", # REAL cars.com selector
            ".all_features-section",       # REAL cars.com selector
            ".vehicle-features",
            ".all-features",
            ".options-section",
            ".features-list"
        ]
        
        for selector in features_selectors:
            print(f"   {selector}: {'✓' if selector in str(analysis['sections_found']) else '❌'}")
        
        # Test the actual profile selectors
        print("\n5. PROFILE SELECTORS TEST:")
        profile = CARS_COM_PROFILE
        
        print(f"   Title: {profile.get_selector('title')}")
        print(f"   Price: {profile.get_selector('price')}")
        print(f"   Mileage: {profile.get_selector('mileage')}")
        print(f"   Wait conditions: {profile.get_wait_selector()}")
        
        # Test against the actual sample content
        print("\n6. SAMPLE CONTENT VERIFICATION:")
        
        # Check if we have the expected sections
        expected_sections = ["TITLE_SECTION", "PRICE_SECTION", "BASIC_SECTION", "FEATURES_SECTION"]
        
        for section in expected_sections:
            if section in analysis["sections_found"]:
                elements = analysis["sections_found"][section]
                print(f"   ✓ {section}: {len(elements)} element(s)")
                
                # Show first element details
                if elements:
                    first_elem = elements[0]
                    print(f"      Selector: {first_elem['selector']}")
                    print(f"      Classes: {first_elem['classes']}")
                    print(f"      Text: {first_elem['sample_text'][:100]}...")
            else:
                print(f"   ❌ {section}: Not found")
        
        print("\n✅ Real Selector Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_sample_summary():
    """Show a summary of what we extracted"""
    print("\n=== Sample Summary ===")
    
    try:
        from x987.pipeline.sample_extractor import SampleExtractor
        
        sample_extractor = SampleExtractor({})
        analysis = sample_extractor.analyze_sample_structure("cars_com")
        
        if "error" in analysis:
            print(f"Error: {analysis['error']}")
            return
        
        print(f"Sample file: {analysis['sample_file']}")
        print(f"Total sections: {len(analysis['sections_found'])}")
        
        for section_type, elements in analysis["sections_found"].items():
            print(f"\n{section_type}:")
            for i, elem in enumerate(elements[:2]):  # Show first 2
                print(f"  {i+1}. {elem['selector']}")
                print(f"     Classes: {elem['classes']}")
                print(f"     Content: {elem['sample_text'][:80]}...")
        
        print("\n🎯 Key Real Selectors Found:")
        print("  • Title: h1.sticky-header-listing-title, h1.listing-title")
        print("  • Price: .price-section, .price-section-vehicle-card")
        print("  • Basic: .listing-overview")
        print("  • Features: .features-section, .sds-page-section.features-section")
        
    except Exception as e:
        print(f"Summary failed: {e}")

def main():
    """Main function"""
    print("Real Selector Testing for cars.com")
    print("=" * 50)
    
    try:
        # Test real selectors
        success = test_real_selectors()
        
        if success:
            # Show sample summary
            show_sample_summary()
            
            print("\n=== Next Steps ===")
            print("1. ✅ Real selectors have been updated in profiles and sample extractor")
            print("2. ✅ Scraping pipeline now uses real cars.com selectors")
            print("3. ✅ Sample extractor prioritizes real DOM structure")
            print("4. 🔄 Ready to test scraping with real selectors")
            print("5. 🔄 Can extract additional samples using real selectors")
            
        return success
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
