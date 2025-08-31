#!/usr/bin/env python3
"""
Debug test for price extraction to see why .primary-price selector isn't working

PROVIDES: Debugging of price extraction selector issues
DEPENDS: Scraping modules and Playwright
CONSUMED BY: Development and debugging
CONTRACT: Identifies why price selectors aren't working
TECH CHOICE: Playwright with detailed element inspection
RISK: Low - test files don't affect production code

"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

def debug_price_extraction():
    """Debug price extraction to see what's happening"""
    print("=== DEBUGGING PRICE EXTRACTION ===")
    
    try:
        from x987.scrapers.universal import UniversalVDPScraper
        from x987.scrapers.profiles import get_site_profile
        from playwright.sync_api import sync_playwright
        
        test_url = "https://www.cars.com/vehicledetail/f36525be-f38b-4213-ad98-f5c0af0d0dba/?aff=atempst"
        
        # Get site profile
        profile = get_site_profile(test_url)
        print(f"Site profile: {profile.name}")
        
        # Test price selector
        price_selector = profile.get_selector("price")
        print(f"Price selector: {price_selector}")
        
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
                
                # Wait for content to load
                print("Waiting for content to load...")
                page.wait_for_timeout(5000)
                
                # Check if price element exists
                print(f"\nChecking if price element exists...")
                
                # Try the price selector
                try:
                    price_elements = page.locator(price_selector)
                    count = price_elements.count()
                    print(f"Price selector '{price_selector}' found {count} elements")
                    
                    if count > 0:
                        for i in range(count):
                            try:
                                text = price_elements.nth(i).inner_text()
                                class_attr = price_elements.nth(i).get_attribute("class")
                                print(f"  Price element {i+1}: class='{class_attr}', text='{text}'")
                            except Exception as e:
                                print(f"  Price element {i+1}: error reading - {e}")
                    else:
                        print("❌ No price elements found")
                        
                except Exception as e:
                    print(f"❌ Error with price selector: {e}")
                
                # Check if we can find any elements with 'price' in the class
                print(f"\nLooking for elements with 'price' in class...")
                price_class_elements = page.locator("[class*='price']")
                price_class_count = price_class_elements.count()
                print(f"Found {price_class_count} elements with 'price' in class")
                
                for i in range(price_class_count):
                    try:
                        text = price_class_elements.nth(i).inner_text()
                        class_attr = price_class_elements.nth(i).get_attribute("class")
                        print(f"  Price class element {i+1}: class='{class_attr}', text='{text}'")
                    except Exception as e:
                        print(f"  Price class element {i+1}: error reading - {e}")
                
                # Check if we can find the specific .primary-price element
                print(f"\nLooking for .primary-price element...")
                primary_price_elements = page.locator(".primary-price")
                primary_price_count = primary_price_elements.count()
                print(f"Found {primary_price_count} .primary-price elements")
                
                for i in range(primary_price_count):
                    try:
                        text = primary_price_elements.nth(i).inner_text()
                        class_attr = primary_price_elements.nth(i).get_attribute("class")
                        print(f"  .primary-price element {i+1}: class='{class_attr}', text='{text}'")
                    except Exception as e:
                        print(f"  .primary-price element {i+1}: error reading - {e}")
                
                # Test the scraper's extract_text_safe method
                print(f"\nTesting scraper's extract_text_safe method...")
                price_text = scraper.extract_text_safe(page, price_selector)
                print(f"extract_text_safe result: '{price_text}'")
                
            finally:
                browser.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Debug price extraction"""
    print("Debugging price extraction...")
    print("=" * 60)
    
    success = debug_price_extraction()
    
    print("\n" + "=" * 60)
    print("DEBUG SUMMARY")
    print("=" * 60)
    if success:
        print("🔍 Price extraction debug completed successfully!")
        print("Check the output above to see what's happening with the price selector.")
    else:
        print("❌ Price extraction debug failed with an exception.")

if __name__ == "__main__":
    main()
