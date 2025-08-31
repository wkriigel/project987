#!/usr/bin/env python3
"""
Debug test for the universal scraper to see why title extraction isn't working

PROVIDES: Debugging of universal scraper title extraction
DEPENDS: Universal scraper and Playwright
CONSUMED BY: Development and debugging
CONTRACT: Identifies title extraction issues in universal scraper
TECH CHOICE: Playwright with detailed element inspection
RISK: Low - test files don't affect production code

"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

def debug_universal_scraper():
    """Debug the universal scraper to see what's happening with title extraction"""
    print("=== DEBUGGING UNIVERSAL SCRAPER TITLE EXTRACTION ===")
    
    try:
        from x987.scrapers.universal import UniversalVDPScraper
        from x987.scrapers.profiles import get_site_profile
        from playwright.sync_api import sync_playwright
        
        test_url = "https://www.cars.com/vehicledetail/f36525be-f38b-4213-ad98-f5c0af0d0dba/?aff=atempst"
        
        # Get site profile
        profile = get_site_profile(test_url)
        print(f"Site profile: {profile.name}")
        
        # Test selectors
        title_selector = profile.get_selector("title")
        print(f"Title selector: {title_selector}")
        
        # Create scraper instance
        config = {
            "polite_delay_ms": 1000,
            "debug": True,
            "network": {
                "block_images": True,
                "block_media": True,
                "block_fonts": True,
                "block_stylesheets": True,
                "block_analytics": True
            }
        }
        
        scraper = UniversalVDPScraper(config)
        
        # Test with real page
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(ignore_https_errors=True)
            context.set_default_timeout(10_000)
            page = context.new_page()
            
            try:
                print(f"\nNavigating to: {test_url}")
                page.goto(test_url, wait_until="domcontentloaded")
                
                # Wait longer for content to load
                print("Waiting for content to load...")
                page.wait_for_timeout(5000)
                
                # Check if title element exists
                print(f"\nChecking if title element exists...")
                
                # Try individual selectors
                selectors_to_test = [
                    "h1.sticky-header-listing-title",
                    "h1.listing-title", 
                    "h1[data-testid='vehicle-title']",
                    "h1.vehicle-title",
                    "h1.spark-heading-2",
                    ".vehicle-title",
                    "h1"
                ]
                
                for selector in selectors_to_test:
                    try:
                        element = page.locator(selector)
                        count = element.count()
                        if count > 0:
                            text = element.first.inner_text()
                            print(f"✅ Selector '{selector}' found {count} elements, text: '{text}'")
                        else:
                            print(f"❌ Selector '{selector}' found 0 elements")
                    except Exception as e:
                        print(f"❌ Selector '{selector}' error: {e}")
                
                # Check page title
                print(f"\nPage title: {page.title()}")
                
                # Check if we can find any h1 elements
                print(f"\nAll h1 elements on page:")
                h1_elements = page.locator("h1")
                h1_count = h1_elements.count()
                print(f"Found {h1_count} h1 elements")
                
                for i in range(h1_count):
                    try:
                        h1_text = h1_elements.nth(i).inner_text()
                        h1_class = h1_elements.nth(i).get_attribute("class")
                        print(f"  H1 {i+1}: class='{h1_class}', text='{h1_text}'")
                    except Exception as e:
                        print(f"  H1 {i+1}: error reading - {e}")
                
                # Check if the page has loaded the content we expect
                print(f"\nChecking for expected content...")
                
                # Look for the title section
                title_section = page.locator(".title-section")
                if title_section.count() > 0:
                    print("✅ .title-section found")
                    title_section_text = title_section.inner_text()
                    print(f"  Content: {title_section_text}")
                else:
                    print("❌ .title-section not found")
                
                # Look for basics section
                basics_section = page.locator(".basics-section")
                if basics_section.count() > 0:
                    print("✅ .basics-section found")
                else:
                    print("❌ .basics-section not found")
                
                # Look for price section
                price_section = page.locator(".price-section")
                if price_section.count() > 0:
                    print("✅ .price-section found")
                    price_section_text = price_section.inner_text()
                    print(f"  Content: {price_section_text}")
                else:
                    print("❌ .price-section not found")
                
            finally:
                browser.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Debug the universal scraper"""
    print("Debugging universal scraper title extraction...")
    print("=" * 60)
    
    success = debug_universal_scraper()
    
    print("\n" + "=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    if success:
        print("🔍 Debug completed successfully!")
        print("Check the output above to see what's happening with the selectors.")
    else:
        print("❌ Debug failed with an exception.")

if __name__ == "__main__":
    main()
