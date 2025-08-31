#!/usr/bin/env python3
"""
Test the universal scraper with real page scraping to verify title selector and other universal aspects work

PROVIDES: Testing of universal scraper with real page scraping
DEPENDS: Universal scraper and Playwright
CONSUMED BY: Development and testing
CONTRACT: Verifies universal scraper functionality with real pages
TECH CHOICE: Playwright with real page testing
RISK: Low - test files don't affect production code

"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'x987'))

def test_universal_scraper_real_page():
    """Test the universal scraper with a real page to see if title selector works"""
    print("=== TESTING UNIVERSAL SCRAPER WITH REAL PAGE ===")
    
    try:
        from x987.scrapers.universal import UniversalVDPScraper
        from x987.scrapers.profiles import get_site_profile
        from playwright.sync_api import sync_playwright
        
        test_url = "https://www.cars.com/vehicledetail/f36525be-f38b-4213-ad98-f5c0af0d0dba/?aff=atempst"
        
        # Get site profile
        profile = get_site_profile(test_url)
        print(f"Site profile: {profile.name}")
        
        # Test selectors
        print(f"Title selector: {profile.get_selector('title')}")
        print(f"Price selector: {profile.get_selector('price')}")
        print(f"Mileage selector: {profile.get_selector('mileage')}")
        print(f"VIN selector: {profile.get_selector('vin')}")
        
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
                page.wait_for_timeout(2000)  # Wait for content to load
                
                # Test title extraction
                title_selector = profile.get_selector("title")
                print(f"\nTesting title extraction with selector: {title_selector}")
                
                title_text = scraper.extract_text_safe(page, title_selector)
                print(f"Title extracted: {title_text}")
                
                if title_text:
                    print("✅ Title selector is working!")
                    
                    # Test title parsing
                    year, model, trim, title_price = scraper._parse_title_enhanced(title_text)
                    print(f"  Parsed year: {year}")
                    print(f"  Parsed model: {model}")
                    print(f"  Parsed trim: {trim}")
                    print(f"  Parsed price: {title_price}")
                else:
                    print("❌ Title selector failed to extract text")
                
                # Test other selectors
                print(f"\nTesting other selectors:")
                
                # Price
                price_text = scraper.extract_text_safe(page, profile.get_selector("price"))
                print(f"  Price: {price_text}")
                
                # Mileage
                mileage_text = scraper.extract_text_safe(page, profile.get_selector("mileage"))
                print(f"  Mileage: {mileage_text}")
                
                # VIN
                vin_text = scraper.extract_text_safe(page, profile.get_selector("vin"))
                print(f"  VIN: {vin_text}")
                
                # Test full scraping
                print(f"\nTesting full scraping...")
                result = scraper.scrape(page, test_url)
                
                if result.success:
                    print("✅ Full scraping successful!")
                    print(f"  Data extracted: {result.data}")
                else:
                    print(f"❌ Full scraping failed: {result.error}")
                
            finally:
                browser.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test the universal scraper with real page scraping"""
    print("Testing universal scraper with real page...")
    print("=" * 60)
    
    success = test_universal_scraper_real_page()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if success:
        print("🎉 Universal scraper is working with real pages!")
        print("The title selector and other universal aspects are functioning correctly.")
    else:
        print("❌ Universal scraper has issues with real page scraping.")
        print("The title selector or other universal aspects may not be working.")

if __name__ == "__main__":
    main()
