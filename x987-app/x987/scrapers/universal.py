"""
Universal VDP scraper for vehicle detail pages

PROVIDES: Single scraping engine that works across multiple sites
DEPENDS: Base scraper, site profiles, schema
CONSUMED BY: Pipeline scraping modules
CONTRACT: Provides consistent data extraction regardless of source
TECH CHOICE: Profile-driven scraping for maintainability
RISK: Medium - site changes require profile updates
"""

import re
import time
from typing import Dict, Any, Optional, List, Union
from playwright.sync_api import Page

from .base import BaseScraper, ScrapingResult
from .profiles import get_site_profile, SiteProfile

# Simple logging for now
import logging
logger = logging.getLogger("scrapers.universal")
from bs4 import BeautifulSoup

class UniversalVDPScraper(BaseScraper):
    """Universal scraper for vehicle detail pages"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger("scrapers.universal")
    
    def scrape(self, page: Page, url: str) -> ScrapingResult:
        """Scrape vehicle data using site-specific profile or fallback to full DOM"""
        try:
            # Setup page for scraping
            self.setup_page(page)
            
            # Get site profile
            profile = get_site_profile(url)
            print(f"Using profile: {profile.name}")
            
            # Wait for content to load using profile-specific wait conditions.
            # If it fails, proceed anyway with HTML-first extraction from the dump.
            if not self._wait_for_profile_content(page, profile):
                print("⚠️  Profile wait conditions failed; proceeding with HTML-first extraction from full DOM dump")
            
            # Extract data using profile (HTML-first strategy)
            data = self._extract_data(page, profile, url)
            
            return ScrapingResult(
                success=True,
                data=data,
                source=profile.name,
                url=url,
                timestamp=time.time()
            )
            
        except Exception as e:
            print(f"Scraping failed for {url}: {e}")
            return ScrapingResult(
                success=False,
                data={},
                error=str(e),
                source="unknown",
                url=url,
                timestamp=time.time()
            )
    
    def _extract_data(self, page: Page, profile: SiteProfile, url: str) -> Dict[str, Any]:
        """Extract raw text data using profile selectors OR entire DOM as fallback"""
        data = {
            "source": profile.name,
            "listing_url": url,
            "raw_dom_text": None,  # Full DOM text
            "raw_html": None,      # Full HTML dump
            "raw_sections": {}      # Raw text from profile section selectors
        }
        
        # Attempt to extract JSON-LD structured data when available
        try:
            json_ld_list = page.locator("script[type='application/ld+json']")
            count = json_ld_list.count()
            ld_merged = {}
            for i in range(min(count, 5)):
                try:
                    raw = json_ld_list.nth(i).inner_text()
                    import json
                    parsed = json.loads(raw)
                    # Flatten simple dicts/arrays conservatively
                    if isinstance(parsed, dict):
                        for k, v in parsed.items():
                            if k not in ld_merged:
                                ld_merged[k] = v
                    elif isinstance(parsed, list) and parsed:
                        for obj in parsed:
                            if isinstance(obj, dict):
                                for k, v in obj.items():
                                    if k not in ld_merged:
                                        ld_merged[k] = v
                except Exception:
                    continue
            if ld_merged:
                data.setdefault("structured_data", ld_merged)
        except Exception:
            pass

        # Capture full HTML dump first (primary artifact)
        try:
            full_html = page.content()
            data["raw_html"] = full_html
            print(f"✅ Captured full HTML dump: {len(full_html)} chars")
        except Exception as e:
            print(f"❌ Failed to capture full HTML: {e}")
            data["raw_html"] = ""
        
        # Parse the full HTML once for HTML-based extraction
        soup: Optional[BeautifulSoup] = None
        if data["raw_html"]:
            try:
                soup = BeautifulSoup(data["raw_html"], "html.parser")
            except Exception as e:
                print(f"⚠️  Failed to parse HTML with BeautifulSoup: {e}")
                soup = None
        
        # Extract raw text from each section using profile selectors (HTML-first strategy)
        section_names = ["page_title", "title_section", "price_section", "basic_section", "features_section", "seller_notes"]
        successful_extractions = 0
        
        for section_name in section_names:
            selector = profile.get_selector(section_name)
            if selector:
                try:
                    raw_text = ""
                    selectors: List[str]
                    if isinstance(selector, list):
                        selectors = selector
                    else:
                        # Split on comma to support multiple selectors in one string
                        selectors = [s.strip() for s in str(selector).split(',') if s.strip()]
                    
                    # HTML-based extraction first
                    if soup is not None:
                        for sel in selectors:
                            try:
                                matches = soup.select(sel)
                                if matches:
                                    # Join all matched text blocks for robustness
                                    text_parts = [m.get_text(" ", strip=True) for m in matches]
                                    raw_text = " \n ".join([t for t in text_parts if t])
                                    if raw_text:
                                        break
                            except Exception:
                                continue
                    
                    # Fallback to live page locator extraction if HTML parse didn't find anything
                    if not raw_text:
                        for sel in selectors:
                            raw_text = self.extract_text_safe(page, sel)
                            if raw_text:
                                break
                    # Avoid "similar cars" or non-primary modules heuristically
                    banned_snippets = [
                        "similar cars", "you may also like", "people also viewed", "sponsored",
                        "related items", "people who viewed", "more items", "shop similar"
                    ]
                    if raw_text and not any(bs in raw_text.lower() for bs in banned_snippets):
                        data["raw_sections"][section_name] = raw_text
                        successful_extractions += 1
                        print(f"✅ Extracted {section_name}: {len(raw_text)} chars")
                    else:
                        print(f"⚠️  {section_name}: selector found but no text extracted")
                except Exception as e:
                    print(f"❌ Failed to extract {section_name}: {e}")
            else:
                print(f"⚠️  No selector defined for {section_name}")
        
        # Always extract full DOM text using innerText for accurate textual content
        try:
            data["raw_dom_text"] = page.evaluate("document.body.innerText")
            print(f"✅ Extracted full DOM text: {len(data['raw_dom_text'])} chars")
        except Exception as e:
            print(f"❌ Failed to extract full DOM text: {e}")
            data["raw_dom_text"] = ""

        # Enrich missing sections using structured data when available
        try:
            sd = data.get("structured_data") or {}
            if isinstance(sd, list):
                # Choose the first dict-like entry
                sd = next((x for x in sd if isinstance(x, dict)), {})

            def set_if_empty(key: str, value: str):
                if value and not data["raw_sections"].get(key):
                    data["raw_sections"][key] = value

            # Title from structured data
            title_candidates = []
            if isinstance(sd, dict):
                title_candidates.append(str(sd.get("name", "")).strip())
                # Common vehicle schema fields
                composed = " ".join([
                    str(sd.get("vehicleModelDate", "")).strip(),
                    str(sd.get("brand", {}).get("name", "") if isinstance(sd.get("brand"), dict) else sd.get("brand", "")).strip(),
                    str(sd.get("model", "")).strip(),
                    str(sd.get("trim", "")).strip(),
                ]).strip()
                title_candidates.append(composed)
            title_value = next((t for t in title_candidates if t), "")
            set_if_empty("title_section", title_value)

            # Price from offers
            price_text = ""
            offers = sd.get("offers") if isinstance(sd, dict) else None
            if isinstance(offers, dict):
                price_text = str(offers.get("price", "")).strip()
            elif isinstance(offers, list) and offers:
                for off in offers:
                    if isinstance(off, dict) and off.get("price"):
                        price_text = str(off.get("price")).strip()
                        break
            if price_text:
                set_if_empty("price_section", f"List price\n\n${price_text}")

            # Basic section assembly from structured data
            basic_parts = []
            for label, val in [
                ("Exterior color", sd.get("color") if isinstance(sd, dict) else None),
                ("Mileage", (sd.get("mileageFromOdometer", {}).get("value") if isinstance(sd.get("mileageFromOdometer"), dict) else sd.get("mileage")) if isinstance(sd, dict) else None),
                ("Transmission", sd.get("vehicleTransmission") if isinstance(sd, dict) else None),
                ("Drivetrain", sd.get("driveWheelConfiguration") if isinstance(sd, dict) else None),
                ("Engine", sd.get("vehicleEngine", {}).get("name") if isinstance(sd.get("vehicleEngine"), dict) else None),
                ("Fuel type", sd.get("fuelType") if isinstance(sd, dict) else None),
            ]:
                if val:
                    basic_parts.append(f"{label}\n{val}")
            if basic_parts:
                set_if_empty("basic_section", "\n".join(basic_parts))
        except Exception as e:
            print(f"⚠️  Structured data enrichment failed: {e}")
        
        # Log extraction summary
        print(f"📊 Data extraction summary: {successful_extractions}/{len(section_names)} sections extracted successfully")
        
        return data
    
    def _wait_for_profile_content(self, page: Page, profile: SiteProfile, timeout: int = 10000) -> bool:
        """Wait for page content using profile-specific wait conditions"""
        try:
            # First wait for basic page load
            page.wait_for_load_state("domcontentloaded", timeout=timeout)
            
            # Track which conditions succeeded and failed
            successful_conditions = []
            failed_conditions = []
            
            # Wait for profile-specific wait conditions with scrolling support
            if profile.wait_conditions:
                for condition in profile.wait_conditions:
                    try:
                        # First try to wait for the selector normally
                        page.wait_for_selector(condition, timeout=5000)
                        print(f"✅ Wait condition met: {condition}")
                        successful_conditions.append(condition)
                    except Exception as e:
                        print(f"⚠️  Wait condition failed: {condition} - {e}")
                        
                        # If normal wait fails, try scrolling to trigger lazy loading
                        print(f"🔄 Attempting to scroll to trigger lazy loading for: {condition}")
                        
                        # Check selector state before scrolling
                        before_state = self._check_selector_presence(page, condition)
                        print(f"📊 Before scrolling - {condition}: {before_state}")
                        
                        try:
                            # Scroll down progressively to trigger lazy loading
                            self._scroll_to_trigger_lazy_loading(page)
                            
                            # Check selector state after scrolling
                            after_state = self._check_selector_presence(page, condition)
                            print(f"📊 After scrolling - {condition}: {after_state}")
                            
                            # Try waiting again after scrolling
                            page.wait_for_selector(condition, timeout=5000)
                            print(f"✅ Wait condition met after scrolling: {condition}")
                            successful_conditions.append(condition)
                        except Exception as scroll_error:
                            print(f"❌ Selector still not found after scrolling: {condition} - {scroll_error}")
                            failed_conditions.append(condition)
                            # Continue with other conditions - don't fail completely
            
            # Log summary of wait conditions
            print(f"📊 Wait conditions summary: {len(successful_conditions)} succeeded, {len(failed_conditions)} failed")
            if successful_conditions:
                print(f"✅ Successful: {', '.join(successful_conditions)}")
            if failed_conditions:
                print(f"❌ Failed: {', '.join(failed_conditions)}")
            
            # Additional wait for dynamic content
            page.wait_for_timeout(2000)  # Wait 2 seconds for JavaScript to render
            
            # Return True if at least one condition succeeded, or if we have no conditions
            # This allows extraction to continue even if some selectors fail
            return len(successful_conditions) > 0 or len(profile.wait_conditions) == 0
            
        except Exception as e:
            print(f"❌ Wait for profile content failed: {e}")
            return False
    
    def _scroll_to_trigger_lazy_loading(self, page: Page) -> None:
        """Scroll page progressively to trigger lazy loading of content"""
        try:
            # Get page dimensions
            vs = page.viewport_size
            viewport_height = (
                vs['height'] if isinstance(vs, dict) and 'height' in vs else 720
            )
            page_height = page.evaluate("document.body.scrollHeight")
            
            print(f"📏 Page height: {page_height}px, Viewport height: {viewport_height}px")
            
            # Scroll down progressively in chunks
            scroll_positions = [
                viewport_height * 0.5,      # Half viewport
                viewport_height * 1.0,      # Full viewport
                viewport_height * 1.5,      # 1.5 viewport
                viewport_height * 2.0,      # 2 viewport
                page_height * 0.5,          # Half page
                page_height * 0.75,         # 3/4 page
                page_height                 # Full page
            ]
            
            for i, scroll_to in enumerate(scroll_positions):
                if scroll_to > page_height:
                    scroll_to = page_height
                
                print(f"📜 Scrolling to position {i+1}/{len(scroll_positions)}: {scroll_to}px")
                
                # Smooth scroll to position
                page.evaluate(f"window.scrollTo({{top: {scroll_to}, behavior: 'smooth'}})")
                
                # Wait for scroll to complete and content to load
                page.wait_for_timeout(1000)
                
                # Check if we've reached the bottom
                if scroll_to >= page_height:
                    break
            
            # Scroll back to top
            print("📜 Scrolling back to top")
            page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
            page.wait_for_timeout(1000)
            
            print("✅ Scrolling completed")
            
        except Exception as e:
            print(f"⚠️  Scrolling failed: {e}")
            # Fallback: simple scroll to bottom and back
            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1000)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(1000)
                print("✅ Fallback scrolling completed")
            except Exception as fallback_error:
                print(f"❌ Fallback scrolling also failed: {fallback_error}")
    
    def extract_text_safe(self, page: Page, selector: str, default: str = "") -> str:
        """Extract text safely from a selector"""
        try:
            if selector == "head title":
                # Special case for page title
                return page.title() or ""
            else:
                # Regular DOM selector
                locator = page.locator(selector)
                count = locator.count()
                
                if count > 0:
                    # Check if element is visible
                    first_element = locator.first
                    is_visible = first_element.is_visible()
                    
                    if is_visible:
                        text = first_element.inner_text().strip()
                        if text:
                            return text
                        else:
                            print(f"⚠️  Selector {selector} found but has no text content")
                    else:
                        print(f"⚠️  Selector {selector} found but element is not visible")
                else:
                    print(f"⚠️  Selector {selector} not found in DOM (count: {count})")
                    
        except Exception as e:
            print(f"❌ Error extracting from {selector}: {e}")
            
        return default
    
    def _check_selector_presence(self, page: Page, selector: str) -> Dict[str, Any]:
        """Check if a selector is present and visible in the DOM"""
        try:
            locator = page.locator(selector)
            count = locator.count()
            
            if count == 0:
                return {"present": False, "count": 0, "visible": False, "text_length": 0}
            
            # Check first element
            first_element = locator.first
            is_visible = first_element.is_visible()
            
            try:
                text = first_element.inner_text().strip()
                text_length = len(text)
            except:
                text_length = 0
            
            return {
                "present": True,
                "count": count,
                "visible": is_visible,
                "text_length": text_length
            }
            
        except Exception as e:
            return {"present": False, "count": 0, "visible": False, "text_length": 0, "error": str(e)}
