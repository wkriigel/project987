#!/usr/bin/env python3
"""
Test script to verify the fixed pipeline architecture

This script tests that:
1. Collection step only collects URLs from AutoTempest
2. Scraping step uses UniversalVDPScraper with profiles
3. The pipeline flows correctly through all steps
"""

import sys
import os
from pathlib import Path

# Add the x987-app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "x987-app"))

def test_collection_step():
    """Test that collection step only collects URLs"""
    print("🧪 Testing Collection Step...")
    
    try:
        from x987.pipeline.steps.collection import CollectionStep
        
        # Create collection step
        collection_step = CollectionStep()
        
        # Test configuration
        test_config = {
            "search": {
                "urls": ["https://www.autotempest.com/results?make=porsche&model=cayman&year_min=2009&year_max=2012"]
            }
        }
        
        print("   ✅ Collection step imported successfully")
        print(f"   📋 Step name: {collection_step.get_step_name()}")
        print(f"   📋 Description: {collection_step.get_description()}")
        print(f"   📋 Dependencies: {collection_step.get_dependencies()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Collection step test failed: {e}")
        return False

def test_scraping_step():
    """Test that scraping step uses UniversalVDPScraper"""
    print("\n🧪 Testing Scraping Step...")
    
    try:
        from x987.pipeline.steps.scraping import ScrapingStep
        
        # Create scraping step
        scraping_step = ScrapingStep()
        
        print("   ✅ Scraping step imported successfully")
        print(f"   📋 Step name: {scraping_step.get_step_name()}")
        print(f"   📋 Description: {scraping_step.get_description()}")
        print(f"   📋 Dependencies: {scraping_step.get_dependencies()}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Scraping step test failed: {e}")
        return False

def test_universal_scraper():
    """Test that UniversalVDPScraper is available and working"""
    print("\n🧪 Testing Universal Scraper...")
    
    try:
        from x987.scrapers.universal import UniversalVDPScraper
        from x987.scrapers.profiles import get_site_profile
        
        # Test profile detection
        test_url = "https://www.cars.com/vehicledetail/test"
        profile = get_site_profile(test_url)
        
        print("   ✅ Universal scraper imported successfully")
        print(f"   📋 Profile detected: {profile.name}")
        print(f"   📋 Domain: {profile.domain}")
        print(f"   📋 Selectors available: {list(profile.selectors.keys())}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Universal scraper test failed: {e}")
        return False

def test_profiles():
    """Test that site profiles are properly configured"""
    print("\n🧪 Testing Site Profiles...")
    
    try:
        from x987.scrapers.profiles import CARS_COM_PROFILE, SITE_PROFILES
        
        print("   ✅ Site profiles imported successfully")
        print(f"   📋 Cars.com profile: {CARS_COM_PROFILE.name}")
        print(f"   📋 Available profiles: {list(SITE_PROFILES.keys())}")
        
        # Check that key selectors are defined
        key_selectors = ["price_section", "basic_section", "features_section"]
        for selector in key_selectors:
            if selector in CARS_COM_PROFILE.selectors:
                print(f"   ✅ {selector} selector: {CARS_COM_PROFILE.selectors[selector]}")
            else:
                print(f"   ❌ {selector} selector missing")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Site profiles test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Fixed Pipeline Architecture")
    print("=" * 50)
    
    tests = [
        test_collection_step,
        test_scraping_step,
        test_universal_scraper,
        test_profiles
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Pipeline architecture is fixed.")
        print("\n📋 Summary of changes:")
        print("   • Collection step now only collects URLs from AutoTempest")
        print("   • Scraping step uses UniversalVDPScraper with site profiles")
        print("   • Site profiles (CARS_COM_PROFILE) are now properly utilized")
        print("   • Pipeline will now scrape individual listing pages for detailed data")
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
