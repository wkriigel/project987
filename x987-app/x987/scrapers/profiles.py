"""
Site-specific scraping profiles

PROVIDES: Configuration and selectors for different car listing sites
DEPENDS: Base scraper utilities
CONSUMED BY: Universal scraper
CONTRACT: Provides site-specific scraping rules
TECH CHOICE: Data-driven configuration for maintainability
RISK: Medium - site changes require profile updates
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import re

@dataclass
class SiteProfile:
    """Configuration for scraping a specific site"""
    name: str
    domain: str
    selectors: Dict[str, str | List[str]]
    wait_conditions: List[str]
    color_patterns: List[str]
    trim_patterns: List[str]
    price_patterns: List[str]
    mileage_patterns: List[str]
    transmission_patterns: Dict[str, str]
    
    def get_selector(self, key: str, default: str | List[str] = "") -> str | List[str]:
        """Get selector with fallback"""
        return self.selectors.get(key, default)
    
    def get_wait_selector(self) -> Optional[str]:
        """Get primary wait selector"""
        return self.wait_conditions[0] if self.wait_conditions else None

# Site-specific profiles
CARS_COM_PROFILE = SiteProfile(
    name="Cars.com",
    domain="cars.com",
    selectors={
        # Only extract raw text from the specified sections - no individual field parsing
        "page_title": "head title",  # Page title from head
        "title_section": ".title-section",  # Title section content
        "price_section": ".price-section, .primary-price, [data-qa='primary-price'], .price-display, .vehicle-price",  # Price section content (multiple fallbacks)
        "basic_section": ".basics-section",  # Basic info section content (FIXED: was .basic-section)
        "features_section": ".features-section",  # Features/options section content
        "seller_notes": ".seller-notes"  # Seller notes section content
    },
    wait_conditions=[
        ".title-section",  # Wait for title section to load
        ".basics-section"   # Wait for basic info to load (FIXED: was .basic-section)
    ],
    color_patterns=[],  # Not used in scraping - handled in transformation
    trim_patterns=[],   # Not used in scraping - handled in transformation
    price_patterns=[],  # Not used in scraping - handled in transformation
    mileage_patterns=[], # Not used in scraping - handled in transformation
    transmission_patterns={} # Not used in scraping - handled in transformation
)

TRUECAR_PROFILE = SiteProfile(
    name="TrueCar",
    domain="truecar.com",
    selectors={
        # Standard universal sections to ensure extractor compatibility
        "page_title": "head title",
        # Prefer main/role=main containers to avoid similar/related blocks elsewhere
        "title_section": "main h1, [role='main'] h1, h1.vehicle-title, [data-test*='Header'] h1",
        "price_section": "main [data-test*='Price'], [role='main'] [data-test*='Price'], main .price-display, [role='main'] .price-display, main [class*='price']:not([class*='similar']):not([class*='related'])",
        "basic_section": "main .vehicle-overview, [role='main'] .vehicle-overview, main [data-test*='Overview'], [role='main'] [data-test*='Overview'], main .vdp-fact-list, [role='main'] [class*='facts']",
        "features_section": "main [data-test*='Features'], [role='main'] [data-test*='Features'], main .features, [role='main'] .features, main [class*='feature-list']",
        "seller_notes": "main .seller-notes, [role='main'] .seller-notes, main .vehicle-highlights, [role='main'] .vehicle-highlights, main [data-test*='Highlights']"
    },
    wait_conditions=[
        "main h1, [role='main'] h1, h1.vehicle-title",
        "main [data-test*='Price'], [role='main'] [data-test*='Price'], .price-display"
    ],
    color_patterns=CARS_COM_PROFILE.color_patterns,
    trim_patterns=CARS_COM_PROFILE.trim_patterns,
    price_patterns=CARS_COM_PROFILE.price_patterns,
    mileage_patterns=CARS_COM_PROFILE.mileage_patterns,
    transmission_patterns=CARS_COM_PROFILE.transmission_patterns
)

CARVANA_PROFILE = SiteProfile(
    name="Carvana",
    domain="carvana.com",
    selectors={
        "page_title": "head title",
        "title_section": "main h1, [role='main'] h1, main [data-qa*='title'], main [data-test*='Title'], .vehicle-title",
        "price_section": "main .price, [role='main'] .price, main [data-qa*='price'], [data-test*='Price'], [class*='price-display']",
        "basic_section": "main section:has(h2:has-text('Details')), main section:has(h3:has-text('Details')), main .vehicle-details, [role='main'] .vehicle-details, main .specs, [role='main'] .specs, main [data-test*='Details'], [role='main'] [data-test*='Details'], main [class*='overview']",
        "features_section": "main section:has(h2:has-text('Features')), main section:has(h3:has-text('Features')), main .features, [role='main'] .features, main [data-test*='Features'], [role='main'] [data-test*='Features'], main [class*='feature-list']",
        "seller_notes": "main section:has(h2:has-text('Description')), main section:has(h3:has-text('Description')), main .seller-notes, [role='main'] .seller-notes, main .vehicle-description, [role='main'] .vehicle-description, [data-test*='Description']"
    },
    wait_conditions=[
        "main h1, [role='main'] h1, .vehicle-title",
        "main .price, [role='main'] .price, [data-test*='Price']"
    ],
    color_patterns=CARS_COM_PROFILE.color_patterns,
    trim_patterns=CARS_COM_PROFILE.trim_patterns,
    price_patterns=CARS_COM_PROFILE.price_patterns,
    mileage_patterns=CARS_COM_PROFILE.mileage_patterns,
    transmission_patterns=CARS_COM_PROFILE.transmission_patterns
)

# eBay profile
EBAY_PROFILE = SiteProfile(
    name="eBay",
    domain="ebay.com",
    selectors={
        "page_title": "head title",
        # Constrain to primary item container: #CenterPanel or #mainContent within [role='main']
        "title_section": "[role='main'] #CenterPanel h1#itemTitle, [role='main'] h1.x-item-title__mainTitle, [role='main'] main h1#itemTitle",
        "price_section": "[role='main'] #CenterPanel #prcIsum, [role='main'] #CenterPanel #mm-saleDscPrc, [role='main'] span[itemprop='price'], [role='main'] .x-price-primary, [role='main'] [data-testid*='x-price-primary']",
        "basic_section": "[role='main'] #CenterPanel .itemAttr, [role='main'] div#viTabs, [role='main'] main section:has(h2:has-text('Item specifics')), [role='main'] main section:has(h3:has-text('Item specifics'))",
        "features_section": "[role='main'] main section:has(h2:has-text('Features')), [role='main'] main section:has(h3:has-text('Features')), [role='main'] #viTabs_0_is, [role='main'] .ux-layout-section--features",
        "seller_notes": "[role='main'] main section:has(h2:has-text('Description')), [role='main'] main section:has(h3:has-text('Description')), [role='main'] #viTabs_0_pd, [role='main'] #desc_div, [role='main'] [itemprop='description'], [role='main'] #desc_ifr"
    },
    wait_conditions=[
        "[role='main'] #CenterPanel h1#itemTitle, [role='main'] h1.x-item-title__mainTitle",
        "[role='main'] #CenterPanel #prcIsum, [role='main'] .x-price-primary, [role='main'] span[itemprop='price']"
    ],
    color_patterns=CARS_COM_PROFILE.color_patterns,
    trim_patterns=CARS_COM_PROFILE.trim_patterns,
    price_patterns=CARS_COM_PROFILE.price_patterns,
    mileage_patterns=CARS_COM_PROFILE.mileage_patterns,
    transmission_patterns=CARS_COM_PROFILE.transmission_patterns
)

# Profile registry
SITE_PROFILES = {
    "cars.com": CARS_COM_PROFILE,
    "truecar.com": TRUECAR_PROFILE,
    "carvana.com": CARVANA_PROFILE,
    "ebay.com": EBAY_PROFILE
}

def get_site_profile(url: str) -> SiteProfile:
    """Get site profile based on URL"""
    for domain, profile in SITE_PROFILES.items():
        if domain in url.lower():
            return profile
    
    # Default to Cars.com profile
    return CARS_COM_PROFILE

def get_all_profiles() -> List[SiteProfile]:
    """Get all available site profiles"""
    return list(SITE_PROFILES.values())

def add_site_profile(domain: str, profile: SiteProfile) -> None:
    """Add a new site profile"""
    SITE_PROFILES[domain] = profile
