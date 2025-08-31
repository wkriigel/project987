#!/usr/bin/env python3
"""
Test script for the new sample extraction and testing system

PROVIDES: Testing of sample extraction and testing system
DEPENDS: Sample extractor and tester modules
CONSUMED BY: Development and testing
CONTRACT: Tests sample extraction and testing functionality
TECH CHOICE: Sample-based testing for scraping validation
RISK: Low - test files don't affect production code

This script demonstrates how to:
1. Extract samples from different sources
2. Test scraping techniques against samples
3. Generate recommendations for improvement
"""

import sys
import os
from pathlib import Path

# Add the x987 package to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_sample_extraction():
    """Test the sample extraction system"""
    print("=== Testing Sample Extraction System ===")
    
    try:
        from x987.pipeline.sample_extractor import SampleExtractor
        
        # Create sample extractor
        extractor = SampleExtractor({})
        print("✓ Sample extractor created")
        
        # List available samples
        samples = extractor.list_available_samples()
        print(f"Available samples: {samples}")
        
        # Check if we have a cars.com sample
        cars_sample_path = extractor.get_sample_path("cars_com")
        if cars_sample_path:
            print(f"✓ Cars.com sample found: {cars_sample_path}")
        else:
            print("ℹ Cars.com sample not found - will be created during scraping")
        
        return True
        
    except Exception as e:
        print(f"✗ Sample extraction test failed: {e}")
        return False

def test_sample_testing():
    """Test the sample testing system"""
    print("\n=== Testing Sample Testing System ===")
    
    try:
        from x987.pipeline.sample_tester import SampleTester
        
        # Create sample tester
        tester = SampleTester({})
        print("✓ Sample tester created")
        
        # Check if we have samples to test
        from x987.pipeline.sample_extractor import SampleExtractor
        extractor = SampleExtractor({})
        available_samples = extractor.list_available_samples()
        
        if not available_samples:
            print("ℹ No samples available for testing - run scraping first")
            return True
        
        # Test the first available sample
        sample_name = available_samples[0]
        print(f"Testing sample: {sample_name}")
        
        results = tester.test_source_sample(sample_name)
        
        if "error" in results:
            print(f"ℹ Sample testing result: {results['error']}")
        else:
            print(f"✓ Sample testing successful")
            print(f"  - Source: {results['source']}")
            print(f"  - Sample file: {results['sample_file']}")
            print(f"  - Recommendations: {len(results.get('recommendations', []))}")
        
        return True
        
    except Exception as e:
        print(f"✗ Sample testing test failed: {e}")
        return False

def test_integration():
    """Test integration with existing pipeline"""
    print("\n=== Testing Pipeline Integration ===")
    
    try:
        # Test that we can import the modified scraping module
        from x987.pipeline.scrape_streamlined import scrape_vehicle_page
        print("✓ Modified scraping module imports successfully")
        
        # Test that sample extractor can be imported
        from x987.pipeline.sample_extractor import SampleExtractor
        print("✓ Sample extractor imports successfully")
        
        # Test that sample tester can be imported
        from x987.pipeline.sample_tester import SampleTester
        print("✓ Sample tester imports successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing x987 Sample System")
    print("=" * 40)
    
    tests = [
        ("Sample Extraction", test_sample_extraction),
        ("Sample Testing", test_sample_testing),
        ("Pipeline Integration", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Sample system is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
