"""
Async Universal VDP scraper for vehicle detail pages

PROVIDES: Single async scraping engine that works across multiple sites
DEPENDS: Base scraper patterns, site profiles, schema
CONSUMED BY: Pipeline scraping modules (async concurrency path)
CONTRACT: Provides consistent data extraction regardless of source
TECH CHOICE: Profile-driven scraping for maintainability
RISK: Medium - site changes require profile updates
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time

from playwright.async_api import Page

from .profiles import get_site_profile, SiteProfile


@dataclass
class AsyncScrapingResult:
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[float] = None


class UniversalVDPScraperAsync:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def setup_page(self, page: Page) -> None:
        await self._install_network_blocking(page)
        await page.set_viewport_size({"width": 1280, "height": 720})

    async def _install_network_blocking(self, page: Page) -> None:
        block_patterns = [
            "googletagmanager.com", "google-analytics.com", "doubleclick.net",
            "facebook.net", "adservice.google", "adsystem", "scorecardresearch",
            "criteo", "hotjar", "optimizely", "segment.io", "newrelic", "snowplow"
        ]

        async def block_route(route):
            req = route.request
            url = req.url
            rtype = getattr(req, 'resource_type', '')
            if any(pat in url for pat in block_patterns):
                return await route.abort()
            if rtype in ["image", "media", "font", "stylesheet"]:
                return await route.abort()
            return await route.continue_()

        await page.route("**/*", block_route)

    async def scrape(self, page: Page, url: str) -> AsyncScrapingResult:
        try:
            await self.setup_page(page)
            profile = get_site_profile(url)

            # Navigate and wait for content
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            except Exception:
                await page.goto(url, wait_until="load", timeout=60000)

            await self._wait_for_profile_content(page, profile)

            data = await self._extract_data(page, profile, url)

            return AsyncScrapingResult(
                success=True,
                data=data,
                source=profile.name,
                url=url,
                timestamp=time.time(),
            )
        except Exception as e:
            return AsyncScrapingResult(
                success=False,
                data={},
                error=str(e),
                source="unknown",
                url=url,
                timestamp=time.time(),
            )

    async def _extract_data(self, page: Page, profile: SiteProfile, url: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "source": profile.name,
            "listing_url": url,
            "raw_dom_text": None,
            "raw_html": None,
            "raw_sections": {},
        }

        capture_raw_html: bool = bool(self.config.get("capture_raw_html", False))
        capture_dom_text: bool = bool(self.config.get("capture_dom_text", False))

        # Capture full HTML (optional, default off)
        if capture_raw_html:
            try:
                full_html = await page.content()
                data["raw_html"] = full_html
            except Exception:
                data["raw_html"] = ""

        # Section extraction (HTML-first when raw_html captured)
        section_names = [
            "page_title",
            "title_section",
            "price_section",
            "basic_section",
            "features_section",
            "seller_notes",
        ]

        # simple soup only if we captured html
        soup = None
        if data.get("raw_html"):
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(data["raw_html"], "html.parser")
            except Exception:
                soup = None

        for section_name in section_names:
            selector = profile.get_selector(section_name)
            if not selector:
                continue
            raw_text = ""
            selectors: List[str] = (
                [s.strip() for s in str(selector).split(',') if s.strip()]
                if not isinstance(selector, list)
                else selector
            )

            # HTML-first if soup is available
            if soup is not None:
                for sel in selectors:
                    try:
                        matches = soup.select(sel)
                        if matches:
                            text_parts = [m.get_text(" ", strip=True) for m in matches]
                            raw_text = " \n ".join([t for t in text_parts if t])
                            if raw_text:
                                break
                    except Exception:
                        continue

            if not raw_text:
                for sel in selectors:
                    text = await self._extract_text_safe(page, sel)
                    if text:
                        raw_text = text
                        break

            # Avoid irrelevant "similar cars" style blocks
            banned_snippets = [
                "similar cars", "you may also like", "people also viewed", "sponsored",
                "related items", "people who viewed", "more items", "shop similar"
            ]
            if raw_text and not any(bs in raw_text.lower() for bs in banned_snippets):
                data["raw_sections"][section_name] = raw_text

        # Full DOM text (optional, default off)
        if capture_dom_text:
            try:
                data["raw_dom_text"] = await page.evaluate("document.body.innerText")
            except Exception:
                data["raw_dom_text"] = ""

        # JSON-LD structured data
        try:
            json_ld_list = page.locator("script[type='application/ld+json']")
            count = await json_ld_list.count()
            ld_merged = {}
            for i in range(min(count, 5)):
                try:
                    raw = await json_ld_list.nth(i).inner_text()
                    import json
                    parsed = json.loads(raw)
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

        # Enrich missing sections from structured data
        try:
            sd = data.get("structured_data") or {}
            if isinstance(sd, list):
                sd = next((x for x in sd if isinstance(x, dict)), {})

            def set_if_empty(key: str, value: str):
                if value and not data["raw_sections"].get(key):
                    data["raw_sections"][key] = value

            title_candidates = []
            if isinstance(sd, dict):
                title_candidates.append(str(sd.get("name", "")).strip())
                composed = " ".join([
                    str(sd.get("vehicleModelDate", "")).strip(),
                    str(sd.get("brand", {}).get("name", "") if isinstance(sd.get("brand"), dict) else sd.get("brand", "")).strip(),
                    str(sd.get("model", "")).strip(),
                    str(sd.get("trim", "")).strip(),
                ]).strip()
                title_candidates.append(composed)
            title_value = next((t for t in title_candidates if t), "")
            set_if_empty("title_section", title_value)

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
        except Exception:
            pass

        return data

    async def _wait_for_profile_content(self, page: Page, profile: SiteProfile, timeout: int = 10000) -> bool:
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=timeout)
            if profile.wait_conditions:
                for condition in profile.wait_conditions:
                    try:
                        await page.wait_for_selector(condition, timeout=5000)
                    except Exception:
                        # light scroll attempt
                        await page.evaluate("window.scrollTo({top: document.body.scrollHeight * 0.5, behavior: 'auto'})")
                        try:
                            await page.wait_for_selector(condition, timeout=3000)
                        except Exception:
                            continue
            await page.wait_for_timeout(500)
            return True
        except Exception:
            return False

    async def _extract_text_safe(self, page: Page, selector: str, default: str = "") -> str:
        try:
            locator = page.locator(selector)
            count = await locator.count()
            if count > 0:
                first = locator.first
                try:
                    text = (await first.inner_text()).strip()
                    if text:
                        return text
                except Exception:
                    pass
                for i in range(1, min(count, 3)):
                    try:
                        text = (await locator.nth(i).inner_text()).strip()
                        if text:
                            return text
                    except Exception:
                        continue
        except Exception:
            pass
        return default


