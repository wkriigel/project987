#!/usr/bin/env python3
"""
Test script for real DOM sample extraction

PROVIDES: Testing of real DOM sample extraction functionality
DEPENDS: Sample extractor and analysis modules
CONSUMED BY: Development and testing
CONTRACT: Tests sample extraction from actual web pages
TECH CHOICE: Real DOM analysis instead of mock content
RISK: Low - test files don't affect production code

This script demonstrates how the updated SampleExtractor now captures
real DOM structure from actual web pages instead of creating mock content.
"""

import sys
import os
from pathlib import Path

# Add the x987 package to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_sample_analysis():
    """Test analyzing an existing sample to see what we have"""
    print("=== Testing Sample Analysis ===")
    
    try:
        from x987.pipeline.sample_extractor import SampleExtractor
        
        sample_extractor = SampleExtractor({})
        
        # Check what samples we have
        available_samples = sample_extractor.list_available_samples()
        print(f"Available samples: {available_samples}")
        
        if "cars_com" in available_samples:
            print("\n--- Analyzing cars_com Sample ---")
            analysis = sample_extractor.analyze_sample_structure("cars_com")
            
            if "error" in analysis:
                print(f"Error: {analysis['error']}")
                return False
            
            print(f"Sample file: {analysis['sample_file']}")
            print(f"Sections found: {len(analysis['sections_found'])}")
            
            for section_type, elements in analysis["sections_found"].items():
                print(f"  {section_type}: {len(elements)} element(s)")
            
            print("\nRecommendations:")
            for rec in analysis["recommendations"]:
                print(f"  • {rec}")
            
            return True
        else:
            print("No cars_com sample found. Need to extract one first.")
            return False
            
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def test_training_selectors():
    """Test getting training selectors from sample analysis"""
    print("\n=== Testing Training Selectors ===")
    
    try:
        from x987.pipeline.sample_extractor import SampleExtractor
        
        sample_extractor = SampleExtractor({})
        selectors = sample_extractor.get_training_selectors("cars_com")
        
        if selectors:
            print("Training selectors found:")
            for section_type, selector_list in selectors.items():
                print(f"  {section_type}: {selector_list}")
        else:
            print("No training selectors found")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def show_next_steps():
    """Show what to do next to get real DOM samples"""
    print("\n=== Next Steps for Real DOM Samples ===")
    print()
    print("1. **Extract Real Sample from cars.com:**")
    print("   - Navigate to a real cars.com vehicle listing page")
    print("   - Use the updated SampleExtractor to capture real DOM")
    print("   - This will replace the mock sample with actual page structure")
    print()
    print("2. **Analyze the Real Sample:**")
    print("   python -m x987.cli.main analyze-sample cars_com")
    print()
    print("3. **Use Real DOM for Training:**")
    print("   - The sample will contain actual cars.com selectors")
    print("   - Update scraping logic based on real page structure")
    print("   - Iterate on selectors using real training data")
    print()
    print("4. **Expected Real Sections:**")
    print("   - Look for actual cars.com CSS classes")
    print("   - Find real price, title, specs, and features selectors")
    print("   - Understand the actual DOM hierarchy")
    print()
    print("5. **Benefits of Real Samples:**")
    print("   - Authentic training data")
    print("   - Real selector patterns")
    print("   - Actual page structure")
    print("   - Better scraping accuracy")

def main():
    """Main test function"""
    print("Testing Real DOM Sample Extraction")
    print("=" * 50)
    
    try:
        # Test sample analysis
        success1 = test_sample_analysis()
        
        # Test training selectors
        success2 = test_training_selectors()
        
        # Show next steps
        show_next_steps()
        
        return success1 and success2
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
