"""
Base scraper interface and common functionality

PROVIDES: Abstract base class and common utilities for all scrapers
DEPENDS: Standard library only
CONSUMED BY: Site-specific scrapers
CONTRACT: Defines common scraping interface and utilities
TECH CHOICE: ABC for interface consistency
RISK: Low - base interface is stable
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import re
import time
from playwright.sync_api import Page
from ..utils.extractors import (
    extract_mileage_unified, extract_price_unified, extract_color_unified,
    extract_colors_unified, extract_transmission_unified, extract_vin_unified,
    extract_vehicle_info_unified, clean_text_unified, none_if_na_unified
)

@dataclass
class ScrapingResult:
    """Result of a scraping operation"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[float] = None

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = None  # Will be set by subclasses
        
    @abstractmethod
    def scrape(self, page: Page, url: str) -> ScrapingResult:
        """Scrape data from a page"""
        pass
    
    def setup_page(self, page: Page) -> None:
        """Setup page for scraping (blocking, etc.)"""
        self._install_network_blocking(page)
        self._set_viewport(page)
    
    def _install_network_blocking(self, page: Page) -> None:
        """Install network blocking for better performance"""
        # Block common analytics and media
        block_patterns = [
            "googletagmanager.com", "google-analytics.com", "doubleclick.net",
            "facebook.net", "adservice.google", "adsystem", "scorecardresearch",
            "criteo", "hotjar", "optimizely", "segment.io", "newrelic", "snowplow"
        ]
        
        def block_route(route):
            req = route.request
            if any(pattern in req.url for pattern in block_patterns):
                return route.abort()
            if req.resource_type in ["image", "media", "font", "stylesheet"]:
                return route.abort()
            return route.continue_()
        
        page.route("**/*", block_route)
    
    def _set_viewport(self, page: Page) -> None:
        """Set consistent viewport for reliable scraping"""
        page.set_viewport_size({"width": 1280, "height": 720})
    
    def wait_for_content(self, page: Page, timeout: int = 10000) -> bool:
        """Wait for page content to load"""
        try:
            # Wait for body to be present
            page.wait_for_selector("body", timeout=timeout)
            
            # Wait for any dynamic content
            page.wait_for_load_state("networkidle", timeout=timeout)
            return True
        except Exception:
            return False
    
    def extract_text_safe(self, page: Page, selector: str, default: str = "") -> str:
        """Safely extract text from a selector"""
        try:
            elements = page.locator(selector)
            count = elements.count()
            if count > 0:
                # Try first element first
                first_text = elements.first.inner_text().strip()
                if first_text:
                    return first_text
                
                # If first element has no text, try other elements
                for i in range(1, count):
                    try:
                        text = elements.nth(i).inner_text().strip()
                        if text:
                            return text
                    except Exception:
                        continue
        except Exception:
            pass
        return default
    
    def extract_attribute_safe(self, page: Page, selector: str, attribute: str, default: str = "") -> str:
        """Safely extract attribute from a selector"""
        try:
            element = page.locator(selector).first
            if element.count() > 0:
                return element.get_attribute(attribute) or default
        except Exception:
            pass
        return default

# Common text processing utilities
def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    return re.sub(r"\s+", " ", str(text)).strip()

def extract_number(text: str) -> Optional[int]:
    """Extract number from text - now uses unified extractor"""
    if not text:
        return None
    # Try mileage first, then price, then generic number
    mileage = extract_mileage_unified(text)
    if mileage:
        return mileage
    
    price = extract_price_unified(text)
    if price:
        return price
    
    # Fallback to generic number extraction
    match = re.search(r"(\d+(?:,\d+)*)", str(text))
    if match:
        return int(match.group(1).replace(",", ""))
    return None

def extract_price(text: str) -> Optional[int]:
    """Extract price from text - now uses unified extractor"""
    return extract_price_unified(text)

def extract_mileage(text: str) -> Optional[int]:
    """Extract mileage from text - now uses unified extractor"""
    return extract_mileage_unified(text)
