"""
Web scraping modules for View-from-CSV

PROVIDES: Vehicle detail page scraping from multiple sources
DEPENDS: playwright, settings, schema
CONSUMED BY: Pipeline scraping modules and collection step
CONTRACT: Provides consistent scraping interfaces across sources
TECH CHOICE: Playwright with site-specific profiles
RISK: Medium - site changes can break scraping
"""

from .base import BaseScraper, ScrapingResult
from .profiles import SiteProfile, get_site_profile
from .universal import UniversalVDPScraper

__all__ = [
    "BaseScraper",
    "ScrapingResult", 
    "SiteProfile",
    "get_site_profile",
    "UniversalVDPScraper"
]
