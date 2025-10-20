"""
Scraping Step - Extracts vehicle data from collected URLs

This step implements the modular separation strategy for web scraping with
high-quality standardized process output and exceptional maintainability.

PROVIDES: Vehicle data extraction from collected listing URLs
DEPENDS: x987.pipeline.steps.collection:CollectionStep and x987.config:get_config
CONSUMED BY: x987.pipeline.steps.transformation:TransformationStep
CONTRACT: Provides raw scraped data for transformation with validation and quality scoring
TECH CHOICE: Modular scraping with clear separation of concerns
RISK: Medium - web scraping can be fragile, depends on collection step data quality
"""

import time
import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BasePipelineStep, StepResult
from ..seen_registry import canonicalize_url
from ..listing_cache import ListingCache
from ...db.integration import record_scraping, is_sqlite_enabled
from ...db.core import get_connection as db_get_connection, ensure_db as db_ensure_db
from ...db.api import cache_get as db_cache_get, cache_save as db_cache_save
    
    def _should_skip_db_cache(self, conn, canonical_url: str, ttl_days: int = 3) -> tuple[bool, str, dict | None]:
        """DB-backed cache check mirroring ListingCache.should_skip."""
        try:
            rec = db_cache_get(conn, canonical_url)
            if not rec:
                return False, "miss:no_record", None
            if not rec.get('data_blob'):
                return False, "miss:no_payload", None
            # Completeness check via extractors (optional)
            try:
                from x987.utils.extractors import (
                    extract_price_unified,
                    extract_mileage_unified,
                    extract_vehicle_info_unified,
                    clean_text_unified,
                )
            except Exception:
                extract_price_unified = extract_mileage_unified = extract_vehicle_info_unified = None  # type: ignore
                clean_text_unified = None  # type: ignore
            try:
                blob = rec.get('data_blob') or {}
                raw_text = ""
                if isinstance(blob, dict):
                    dom = blob.get("raw_dom_text") or ""
                    sections = blob.get("raw_sections") or {}
                    joined = " \n ".join([str(v) for v in sections.values() if v]) if isinstance(sections, dict) else ""
                    raw_text = str(dom or joined or "")
                if clean_text_unified:
                    raw_text = clean_text_unified(raw_text)  # type: ignore
                has_price = extract_price_unified(raw_text) is not None if extract_price_unified else True
                has_miles = extract_mileage_unified(raw_text) is not None if extract_mileage_unified else True
                y_m_t = extract_vehicle_info_unified(raw_text) if extract_vehicle_info_unified else (None, None, None)
                year_val = y_m_t[0] if isinstance(y_m_t, tuple) and len(y_m_t) >= 1 else None
                if not (has_price and has_miles and year_val is not None):
                    return False, "miss:incomplete_fields", rec
            except Exception:
                pass
            # TTL check
            try:
                last = rec.get('last_scraped_at')
                if last:
                    from datetime import datetime, timedelta
                    t = datetime.fromisoformat(last)
                    if datetime.now() - t > timedelta(days=max(0, int(ttl_days))):
                        return False, "miss:ttl_expired", rec
            except Exception:
                return False, "miss:bad_timestamp", rec
            return True, "hit:ttl_valid", rec
        except Exception:
            return False, "miss:error", None


class ScrapingStep(BasePipelineStep):
    """Scraping step implementing modular separation strategy"""
    
    def get_step_name(self) -> str:
        return "scraping"
    
    def get_description(self) -> str:
        return "Scrapes vehicle data from collected listing URLs"
    
    def get_dependencies(self) -> List[str]:
        return ["collection"]  # Depends on collection step
    
    def get_required_config(self) -> List[str]:
        return ["scraping"]
    
    def run_step(self, config: Dict[str, Any], previous_results: Dict[str, StepResult], **kwargs) -> Any:
        """Execute the scraping step with high-quality process output"""
        verbose = bool(kwargs.get('verbose'))
        import builtins
        _orig_print = builtins.print
        if not verbose:
            builtins.print = lambda *a, **k: None
        try:
            def _run():
                print("🕷️  Starting web scraping process...")
                print(f"📁 Working directory: {Path.cwd()}")
                print(f"⏰ Scraping started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                # Get collection results
                if "collection" in previous_results:
                    collection_result = previous_results["collection"]
                    if not collection_result.is_success:
                        print("❌ Collection step must complete successfully before scraping")
                        raise ValueError("Collection step must complete successfully before scraping")
                    collection_data = collection_result.data.get("collection_data", [])
                else:
                    print("❌ No collection results found - collection step must run first")
                    raise ValueError("Collection step must complete successfully before scraping")

                if not collection_data:
                    print("❌ No URLs to scrape")
                    return {
                        "total_pages_scraped": 0,
                        "scraping_data": [],
                        "successful_scrapes": 0,
                        "failed_scrapes": 0,
                        "scraping_timestamp": datetime.now().isoformat()
                    }

                print(f"📊 Found {len(collection_data)} URLs to scrape")

                # Get scraping configuration
                scraping_config = config.get("scraping", {})
                concurrency = scraping_config.get("concurrency", 1)
                polite_delay = scraping_config.get("polite_delay_ms", 1000) / 1000.0
                headful = kwargs.get('headful', scraping_config.get('headful', True))

                print(f"⚙️  Scraping configuration:")
                print(f"   • Concurrency: {concurrency}")
                print(f"   • Polite delay: {polite_delay:.1f}s")
                print(f"   • Headful mode: {'Yes' if headful else 'No'}")
                print()

                # Step 1: Prepare URLs
                print("🔍 Step 1: Preparing URLs for scraping...")
                prepared_urls = self._prepare_urls_for_scraping(collection_data)

                # Step 2: Scrape data
                print("🕷️  Step 2: Scraping data from URLs...")
                kwargs_without_headful = {k: v for k, v in kwargs.items() if k != 'headful'}
                if max(1, int(scraping_config.get('concurrency', 1))) > 1:
                    scraped_data = self._scrape_urls_concurrent(prepared_urls, scraping_config, headful, **kwargs_without_headful)
                else:
                    scraped_data = self._scrape_urls(prepared_urls, scraping_config, headful, **kwargs_without_headful)

                # Step 3: Process and validate scraped data
                print("🔍 Step 3: Processing scraped data...")
                processed_data = self._process_scraped_data(scraped_data)

                # Step 4: Save results
                print("📄 Step 4: Saving scraping results...")
                saved_files = self._save_scraping_results(processed_data, config)

                # Also persist scrapes to SQLite when enabled
                try:
                    if is_sqlite_enabled(config):
                        record_scraping(processed_data, config)
                except Exception as e:
                    print(f"⚠️  SQLite save skipped: {e}")

                # Step 5: Summary
                print("📊 Step 5: Generating scraping summary...")
                scraping_summary = self._generate_scraping_summary(collection_data, processed_data, saved_files)

                print("✅ Web scraping completed successfully!")
                print(f"📊 Processed {len(collection_data)} URLs")
                print(f"✅ Successfully scraped {len([d for d in processed_data if not d.get('error')])} pages")
                print(f"❌ Failed to scrape {len([d for d in processed_data if d.get('error')])} pages")
                print(f"📄 Saved results to {len(saved_files)} files")

                return scraping_summary

            return _run()
        finally:
            builtins.print = _orig_print
    
    def _prepare_urls_for_scraping(self, collection_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare URLs for scraping with metadata"""
        print("     🔍 Preparing URLs and metadata...")
        
        prepared_urls = []
        for i, url_data in enumerate(collection_data):
            prepared_url = {
                'scraping_id': i + 1,
                'source_url': url_data.get('source_url', ''),
                'listing_url': url_data.get('listing_url', ''),
                'canonical_url': url_data.get('canonical_url', ''),
                'title': url_data.get('title', ''),
                'price': url_data.get('price', ''),
                'mileage': url_data.get('mileage', ''),
                'year': url_data.get('year', ''),
                'model': url_data.get('model', ''),
                'collection_timestamp': url_data.get('collection_timestamp', ''),
                'is_new': url_data.get('is_new', ''),
                'first_seen_at': url_data.get('first_seen_at', ''),
                'preparation_timestamp': datetime.now().isoformat(),
                'scraping_status': 'pending'
            }
            prepared_urls.append(prepared_url)
        
        print(f"       ✅ Prepared {len(prepared_urls)} URLs for scraping")
        return prepared_urls
    
    def _scrape_urls(self, prepared_urls: List[Dict[str, Any]], scraping_config: Dict[str, Any], headful: bool, **kwargs) -> List[Dict[str, Any]]:
        """Scrape data from URLs using the universal scraper with profiles"""
        print("     🕷️  Starting URL scraping with universal scraper...")
        
        try:
            from playwright.sync_api import sync_playwright
            from ...scrapers.universal import UniversalVDPScraper
            
            # Initialize the universal scraper
            scraper = UniversalVDPScraper(scraping_config)
            
            scraped_data = []
            successful_count = 0
            failed_count = 0
            
            with sync_playwright() as p:
                # Launch browser
                print(f"     🌐 Launching Chromium - headful: {headful}")
                browser = p.chromium.launch(
                    headless=not headful,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                # Global context-level route blocking to reduce overhead
                try:
                    context = browser.new_context()
                    block_patterns = [
                        "googletagmanager.com", "google-analytics.com", "doubleclick.net",
                        "facebook.net", "adservice.google", "adsystem", "scorecardresearch",
                        "criteo", "hotjar", "optimizely", "segment.io", "newrelic", "snowplow"
                    ]
                    def _block_route(route):
                        req = route.request
                        url = req.url
                        rtype = getattr(req, 'resource_type', '')
                        if any(pat in url for pat in block_patterns):
                            return route.abort()
                        if rtype in ["image", "media", "font", "stylesheet"]:
                            return route.abort()
                        return route.continue_()
                    context.route("**/*", _block_route)
                except Exception:
                    context = browser.new_context()
                
                # Optional: warm URL→VIN index from recent CSVs
                try:
                    if bool(scraping_config.get('warm_index_on_start', True)):
                        from ..backfill_url_vin import backfill as _warm_backfill
                        _warm_backfill(Path('x987-data/results'), limit=5)
                except Exception:
                    pass

                # Prepare cache and enrichment shortcuts
                cache_cfg = (scraping_config.get('cache') or {}) if isinstance(scraping_config, dict) else {}
                cache_enabled = bool(cache_cfg.get('enabled', True))
                ttl_days = int(cache_cfg.get('ttl_days', 3))
                # Place cache adjacent to results directory for legacy JSON fallback
                output_dir = Path('x987-data/results')
                cache_dir = output_dir.parent if output_dir.name == 'results' else output_dir.parent
                cache_path = cache_dir / 'listing_cache.json'
                listing_cache = ListingCache(cache_path)
                # Optional DB cache connection
                use_db_cache = is_sqlite_enabled({'storage': scraping_config.get('storage')} if isinstance(scraping_config, dict) else {'storage': {}})
                try:
                    use_db_cache = is_sqlite_enabled(config)
                except Exception:
                    pass
                db_conn = None
                if use_db_cache:
                    try:
                        db_ensure_db(config)
                        db_conn = db_get_connection(config)
                    except Exception:
                        db_conn = None

                # Load URL→VIN index and VIN-enriched store for fast-shortcuts
                skip_if_enriched = bool(scraping_config.get('skip_vdp_if_enriched', True))
                url_vin_map = {}
                vin_store = {}
                if skip_if_enriched:
                    try:
                        from ..url_vin_index import load_index as load_url_vin_index
                        url_vin_map = load_url_vin_index() or {}
                    except Exception:
                        url_vin_map = {}
                    try:
                        vin_path = Path('x987-data/metadata/vin_enriched.json')
                        if vin_path.exists():
                            raw = json.loads(vin_path.read_text(encoding='utf-8'))
                            vin_store = raw.get('entries') if isinstance(raw, dict) and 'entries' in raw else raw
                            if not isinstance(vin_store, dict):
                                vin_store = {}
                    except Exception:
                        vin_store = {}

                # Process URLs with polite delays
                for i, url_data in enumerate(prepared_urls):
                    try:
                        listing_url = url_data.get('listing_url')
                        if not listing_url:
                            print(f"        ⚠️  Skipping URL {i+1}: No listing URL found")
                            continue
                        
                        print(f"        🕷️  Scraping {i+1}/{len(prepared_urls)}: {self._get_short_url(listing_url)}")
                        
                        # Cache decision / enriched-shortcut
                        canonical = url_data.get('canonical_url') or canonicalize_url(listing_url)
                        if skip_if_enriched and canonical in url_vin_map:
                            vin = str(url_vin_map.get(canonical) or '').strip().upper()
                            enr = vin_store.get(vin) if vin else None
                            if enr:
                                # Produce a synthetic result using enriched data and current search price/mileage
                                enriched_payload = {
                                    'vin': vin,
                                    'parsed': enr.get('parsed', {}),
                                    'derived': enr.get('derived', {})
                                }
                                scraped_result = {
                                    'scraping_id': url_data.get('scraping_id'),
                                    'source_url': url_data.get('source_url', ''),
                                    'listing_url': listing_url,
                                    'canonical_url': canonical,
                                    'title': url_data.get('title', ''),
                                    'collection_timestamp': url_data.get('collection_timestamp', ''),
                                    'scraping_timestamp': datetime.now().isoformat(),
                                    'scraping_status': 'success',
                                    'scraping_method': 'enriched_shortcut',
                                    'is_new': url_data.get('is_new', ''),
                                    'first_seen_at': url_data.get('first_seen_at', ''),
                                    'cache_hit': False,
                                    'cache_reason': '',
                                    'price': url_data.get('price'),
                                    'mileage': url_data.get('mileage'),
                                    'raw_text': '',
                                    'raw_html': '',
                                    'extracted_data': { 'enriched': enriched_payload }
                                }
                                scraped_data.append(scraped_result)
                                successful_count += 1
                                print(f"        🚫 Skipped VDP (enriched VIN {vin})")
                                continue
                        if cache_enabled:
                            skip = False
                            reason = ""
                            rec_blob = None
                            if db_conn is not None:
                                skip, reason, rec = self._should_skip_db_cache(db_conn, canonical, ttl_days=ttl_days)
                                rec_blob = (rec or {}).get('data_blob') if rec else None
                            else:
                                should_skip, reason = listing_cache.should_skip(canonical, ttl_days=ttl_days)
                                if should_skip:
                                    rec2 = listing_cache.get(canonical)
                                    rec_blob = rec2.data_blob if rec2 else None
                                    skip = True
                            if skip and rec_blob:
                                scraped_result = {
                                        'scraping_id': url_data.get('scraping_id'),
                                        'source_url': url_data.get('source_url', ''),
                                        'listing_url': listing_url,
                                        'canonical_url': canonical,
                                        'title': url_data.get('title', ''),
                                        'collection_timestamp': url_data.get('collection_timestamp', ''),
                                        'scraping_timestamp': datetime.now().isoformat(),
                                        'scraping_status': 'success',
                                        'scraping_method': 'cache',
                                        'is_new': url_data.get('is_new', ''),
                                        'first_seen_at': url_data.get('first_seen_at', ''),
                                        'cache_hit': True,
                                        'cache_reason': reason,
                                        'raw_text': '',
                                        'raw_html': '',
                                        'extracted_data': rec_blob
                                    }
                                    scraped_data.append(scraped_result)
                                    successful_count += 1
                                    print(f"        💾 Cache hit: {reason}")
                                    # Skip network fetch
                                    continue

                        # Create new page for each URL to avoid state issues
                        page = context.new_page()
                        
                        # Set user agent and headers
                        page.set_extra_http_headers({
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'DNT': '1',
                            'Connection': 'keep-alive',
                            'Upgrade-Insecure-Requests': '1'
                        })
                        
                        # Navigate to the listing page first so content is available
                        print(f"        🌐 Navigating to listing: {listing_url}")
                        try:
                            page.goto(listing_url, wait_until='domcontentloaded', timeout=45000)
                        except Exception as e:
                            print(f"        ⚠️  DOM content load failed, retrying with full load: {e}")
                            page.goto(listing_url, wait_until='load', timeout=60000)

                        # Use the universal scraper to extract data
                        scraping_result = scraper.scrape(page, listing_url)
                        
                        if scraping_result.success:
                            # Build fallback raw_text from extracted sections if DOM text absent
                            fallback_text = ''
                            try:
                                sections = scraping_result.data.get('raw_sections', {}) or {}
                                if isinstance(sections, dict):
                                    fallback_text = " \n ".join([str(v) for v in sections.values() if v])
                            except Exception:
                                fallback_text = ''
                            # Convert scraping result to our pipeline format
                            scraped_result = {
                                'scraping_id': url_data.get('scraping_id'),
                                'source_url': url_data.get('source_url', ''),
                                'listing_url': listing_url,
                                'canonical_url': url_data.get('canonical_url', ''),
                                'title': url_data.get('title', ''),
                                'collection_timestamp': url_data.get('collection_timestamp', ''),
                                'scraping_timestamp': datetime.now().isoformat(),
                                'scraping_status': 'success',
                                'scraping_method': 'universal_scraper_with_profiles',
                                'is_new': url_data.get('is_new', ''),
                                'first_seen_at': url_data.get('first_seen_at', ''),
                                'cache_hit': False,
                                'cache_reason': '',
                                'raw_text': scraping_result.data.get('raw_dom_text') or fallback_text,
                                'raw_html': scraping_result.data.get('raw_html', ''),
                                'extracted_data': {
                                    'source': scraping_result.data.get('source', 'unknown'),
                                    'raw_sections': scraping_result.data.get('raw_sections', {}),
                                    'raw_dom_text': scraping_result.data.get('raw_dom_text', '')
                                }
                            }
                            
                            scraped_data.append(scraped_result)
                            successful_count += 1
                            print(f"        ✅ Successfully scraped: {scraping_result.data.get('source', 'unknown')}")
                            # Save to cache
                            try:
                                listing_cache.save_result(
                                    canonical,
                                    scraped_result['extracted_data'],
                                )
                                listing_cache.save()
                            except Exception:
                                pass
                            
                        else:
                            # Handle failed scraping
                            failed_result = {
                                'scraping_id': url_data.get('scraping_id'),
                                'source_url': url_data.get('source_url', ''),
                                'listing_url': listing_url,
                                'canonical_url': url_data.get('canonical_url', ''),
                                'title': url_data.get('title', ''),
                                'collection_timestamp': url_data.get('collection_timestamp', ''),
                                'scraping_timestamp': datetime.now().isoformat(),
                                'scraping_status': 'failed',
                                'scraping_method': 'universal_scraper_with_profiles',
                                'is_new': url_data.get('is_new', ''),
                                'first_seen_at': url_data.get('first_seen_at', ''),
                                'cache_hit': False,
                                'cache_reason': '',
                                'raw_text': '',
                                'raw_html': '',
                                'extracted_data': {
                                    'source': 'unknown',
                                    'error': scraping_result.error
                                }
                            }
                            
                            scraped_data.append(failed_result)
                            failed_count += 1
                            print(f"        ❌ Failed to scrape: {scraping_result.error}")
                        
                        # Close page to free memory
                        page.close()
                        
                        # Polite delay between requests
                        if i < len(prepared_urls) - 1:
                            delay = scraping_config.get('polite_delay_ms', 1000) / 1000.0
                            print(f"        ⏱️  Waiting {delay:.1f}s before next request...")
                            time.sleep(delay)
                        
                    except Exception as e:
                        print(f"        ❌ Error scraping URL {i+1}: {e}")
                        failed_count += 1
                        
                        # Add failed result
                        failed_result = {
                            'scraping_id': url_data.get('scraping_id'),
                            'source_url': url_data.get('source_url', ''),
                            'listing_url': url_data.get('listing_url', ''),
                            'title': url_data.get('title', ''),
                            'collection_timestamp': url_data.get('collection_timestamp', ''),
                            'scraping_timestamp': datetime.now().isoformat(),
                            'scraping_status': 'error',
                            'scraping_method': 'universal_scraper_with_profiles',
                            'raw_text': '',
                            'raw_html': '',
                            'extracted_data': {
                                'source': 'unknown',
                                'error': str(e)
                            }
                        }
                        
                        scraped_data.append(failed_result)
                        continue
                
                context.close()
                browser.close()
            
            print(f"     📊 Scraping completed: {successful_count} successful, {failed_count} failed")
            return scraped_data
            
        except Exception as e:
            print(f"     ❌ Scraping process failed: {e}")
            raise e

    def _scrape_urls_concurrent(self, prepared_urls: List[Dict[str, Any]], scraping_config: Dict[str, Any], headful: bool, **kwargs) -> List[Dict[str, Any]]:
        """Concurrent scraping using async Playwright with a single headful browser and multiple pages."""
        print("     🧵 Starting concurrent scraping path...")
        try:
            import asyncio
            from playwright.async_api import async_playwright
            from ...scrapers.universal_async import UniversalVDPScraperAsync

            scraper = UniversalVDPScraperAsync(scraping_config)

            async def run_concurrent() -> List[Dict[str, Any]]:
                results: List[Dict[str, Any]] = []
                successful_count = 0
                failed_count = 0

                concurrency = max(1, int(scraping_config.get('concurrency', 1)))
                polite_delay_ms = int(scraping_config.get('polite_delay_ms', 1000))
                sem = asyncio.Semaphore(concurrency)

                # Optional: warm URL→VIN index from recent CSVs
                try:
                    if bool(scraping_config.get('warm_index_on_start', True)):
                        from ..backfill_url_vin import backfill as _warm_backfill
                        _warm_backfill(Path('x987-data/results'), limit=5)
                except Exception:
                    pass

                # Prepare cache and enrichment shortcuts (shared across workers)
                cache_cfg = (scraping_config.get('cache') or {}) if isinstance(scraping_config, dict) else {}
                ttl_days = int(cache_cfg.get('ttl_days', 3))
                cache_enabled = bool(cache_cfg.get('enabled', True))
                # Default results path; consistent with serial path
                output_dir = Path('x987-data/results')
                cache_dir = output_dir.parent if output_dir.name == 'results' else output_dir.parent
                cache_path = cache_dir / 'listing_cache.json'
                listing_cache = ListingCache(cache_path)

                # Load URL→VIN index and VIN-enriched store for fast-shortcuts
                skip_if_enriched = bool(scraping_config.get('skip_vdp_if_enriched', True))
                url_vin_map = {}
                vin_store = {}
                if skip_if_enriched:
                    try:
                        from ..url_vin_index import load_index as load_url_vin_index
                        url_vin_map = load_url_vin_index() or {}
                    except Exception:
                        url_vin_map = {}
                    try:
                        vin_path = Path('x987-data/metadata/vin_enriched.json')
                        if vin_path.exists():
                            raw = json.loads(vin_path.read_text(encoding='utf-8'))
                            vin_store = raw.get('entries') if isinstance(raw, dict) and 'entries' in raw else raw
                            if not isinstance(vin_store, dict):
                                vin_store = {}
                    except Exception:
                        vin_store = {}

                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=not headful)
                    context = await browser.new_context()

                    # Install network blocking at context level
                    block_patterns = [
                        "googletagmanager.com", "google-analytics.com", "doubleclick.net",
                        "facebook.net", "adservice.google", "adsystem", "scorecardresearch",
                        "criteo", "hotjar", "optimizely", "segment.io", "newrelic", "snowplow"
                    ]
                    async def _block_route(route):
                        req = route.request
                        url = req.url
                        rtype = getattr(req, 'resource_type', '')
                        if any(pat in url for pat in block_patterns):
                            return await route.abort()
                        if rtype in ["image", "media", "font", "stylesheet"]:
                            return await route.abort()
                        return await route.continue_()
                    await context.route("**/*", _block_route)

                    async def worker(url_data: Dict[str, Any], index: int):
                        nonlocal successful_count, failed_count
                        async with sem:
                            listing_url = url_data.get('listing_url')
                            if not listing_url:
                                failed_count += 1
                                return
                            # Enriched-shortcut or cache decision before creating page
                            canonical = url_data.get('canonical_url') or canonicalize_url(listing_url)
                            if skip_if_enriched and canonical in url_vin_map:
                                vin = str(url_vin_map.get(canonical) or '').strip().upper()
                                enr = vin_store.get(vin) if vin else None
                                if enr:
                                    results.append({
                                        'scraping_id': url_data.get('scraping_id'),
                                        'source_url': url_data.get('source_url', ''),
                                        'listing_url': listing_url,
                                        'canonical_url': canonical,
                                        'title': url_data.get('title', ''),
                                        'collection_timestamp': url_data.get('collection_timestamp', ''),
                                        'scraping_timestamp': datetime.now().isoformat(),
                                        'scraping_status': 'success',
                                        'scraping_method': 'enriched_shortcut',
                                        'is_new': url_data.get('is_new', ''),
                                        'first_seen_at': url_data.get('first_seen_at', ''),
                                        'cache_hit': False,
                                        'cache_reason': '',
                                        'price': url_data.get('price'),
                                        'mileage': url_data.get('mileage'),
                                        'raw_text': '',
                                        'raw_html': '',
                                        'extracted_data': { 'enriched': {
                                            'vin': vin,
                                            'parsed': enr.get('parsed', {}),
                                            'derived': enr.get('derived', {})
                                        }}
                                    })
                                    successful_count += 1
                                    return
                            if cache_enabled:
                                should_skip, reason = listing_cache.should_skip(canonical, ttl_days=ttl_days)
                                if should_skip:
                                    rec = listing_cache.get(canonical)
                                    if rec and rec.data_blob:
                                        results.append({
                                            'scraping_id': url_data.get('scraping_id'),
                                            'source_url': url_data.get('source_url', ''),
                                            'listing_url': listing_url,
                                            'canonical_url': canonical,
                                            'title': url_data.get('title', ''),
                                            'collection_timestamp': url_data.get('collection_timestamp', ''),
                                            'scraping_timestamp': datetime.now().isoformat(),
                                            'scraping_status': 'success',
                                            'scraping_method': 'cache',
                                            'is_new': url_data.get('is_new', ''),
                                            'first_seen_at': url_data.get('first_seen_at', ''),
                                            'cache_hit': True,
                                            'cache_reason': reason,
                                            'raw_text': '',
                                            'raw_html': '',
                                            'extracted_data': rec.data_blob,
                                        })
                                        successful_count += 1
                                        return

                            page = await context.new_page()
                            try:
                                # Headers
                                await page.set_extra_http_headers({
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                    'Accept-Language': 'en-US,en;q=0.5',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'DNT': '1',
                                    'Connection': 'keep-alive',
                                    'Upgrade-Insecure-Requests': '1'
                                })
                                result = await scraper.scrape(page, listing_url)
                                if result.success:
                                    # Build a fallback raw_text from sections if DOM text not captured
                                    fallback_text = ''
                                    try:
                                        sections = result.data.get('raw_sections', {}) or {}
                                        if isinstance(sections, dict):
                                            fallback_text = " \n ".join([str(v) for v in sections.values() if v])
                                    except Exception:
                                        fallback_text = ''
                                    mapped = {
                                        'scraping_id': url_data.get('scraping_id'),
                                        'source_url': url_data.get('source_url', ''),
                                        'listing_url': listing_url,
                                        'canonical_url': canonical,
                                        'title': url_data.get('title', ''),
                                        'collection_timestamp': url_data.get('collection_timestamp', ''),
                                        'scraping_timestamp': datetime.now().isoformat(),
                                        'scraping_status': 'success',
                                        'scraping_method': 'universal_scraper_async',
                                        'is_new': url_data.get('is_new', ''),
                                        'first_seen_at': url_data.get('first_seen_at', ''),
                                        'cache_hit': False,
                                        'cache_reason': '',
                                        # Ensure downstream transformation has text to parse
                                        'raw_text': result.data.get('raw_dom_text') or fallback_text,
                                        'extracted_data': {
                                            'source': result.data.get('source', 'unknown'),
                                            'raw_sections': result.data.get('raw_sections', {}),
                                        }
                                    }
                                    # Optionally include raw artifacts in memory if enabled
                                    if scraping_config.get('capture_raw_html'):
                                        mapped['raw_html'] = result.data.get('raw_html', '')
                                    if scraping_config.get('capture_dom_text') and result.data.get('raw_dom_text'):
                                        mapped['raw_text'] = result.data.get('raw_dom_text', '')
                                    results.append(mapped)
                                    successful_count += 1
                                    # Save to cache
                                    try:
                                        if db_conn is not None:
                                            db_cache_save(db_conn, canonical, mapped['extracted_data'])
                                        else:
                                            listing_cache.save_result(
                                                canonical,
                                                mapped['extracted_data'],
                                            )
                                            listing_cache.save()
                                    except Exception:
                                        pass
                                else:
                                    results.append({
                                        'scraping_id': url_data.get('scraping_id'),
                                        'source_url': url_data.get('source_url', ''),
                                        'listing_url': listing_url,
                                        'canonical_url': canonical,
                                        'title': url_data.get('title', ''),
                                        'collection_timestamp': url_data.get('collection_timestamp', ''),
                                        'scraping_timestamp': datetime.now().isoformat(),
                                        'scraping_status': 'failed',
                                        'scraping_method': 'universal_scraper_async',
                                        'is_new': url_data.get('is_new', ''),
                                        'first_seen_at': url_data.get('first_seen_at', ''),
                                        'cache_hit': False,
                                        'cache_reason': '',
                                        'extracted_data': {'source': 'unknown', 'error': result.error}
                                    })
                                    failed_count += 1
                            except Exception as e:
                                results.append({
                                    'scraping_id': url_data.get('scraping_id'),
                                    'source_url': url_data.get('source_url', ''),
                                    'listing_url': url_data.get('listing_url', ''),
                                    'canonical_url': canonical,
                                    'title': url_data.get('title', ''),
                                    'collection_timestamp': url_data.get('collection_timestamp', ''),
                                    'scraping_timestamp': datetime.now().isoformat(),
                                    'scraping_status': 'error',
                                    'scraping_method': 'universal_scraper_async',
                                    'is_new': url_data.get('is_new', ''),
                                    'first_seen_at': url_data.get('first_seen_at', ''),
                                    'cache_hit': False,
                                    'cache_reason': '',
                                    'extracted_data': {'source': 'unknown', 'error': str(e)}
                                })
                                failed_count += 1
                            finally:
                                await page.close()

                            # Polite delay between starting next task per worker
                            await asyncio.sleep(max(0.0, polite_delay_ms / 1000.0))

                    tasks = [worker(u, i) for i, u in enumerate(prepared_urls)]
                    await asyncio.gather(*tasks)

                    await context.close()
                    await browser.close()

                    print(f"     📊 Concurrent scraping completed: {successful_count} successful, {failed_count} failed")
                    return results

            return asyncio.run(run_concurrent())
        except Exception as e:
            print(f"     ❌ Concurrent scraping process failed: {e}")
            raise e
    
    # _use_collection_data method removed - now using universal scraper with profiles


    
    def _get_short_url(self, url: str) -> str:
        """Get a shortened version of the URL for display"""
        if len(url) > 60:
            return url[:57] + "..."
        return url
    
    def _process_scraped_data(self, scraped_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and validate scraped data"""
        print("     🔄 Processing and validating scraped data...")
        
        processed_data = []
        successful_count = 0
        failed_count = 0
        
        for data in scraped_data:
            if data.get('scraping_status') == 'success':
                # Validate extracted data
                extracted_data = data.get('extracted_data', {})
                validation_result = self._validate_extracted_data(extracted_data)
                
                if validation_result['is_valid']:
                    data['validation_status'] = 'valid'
                    data['validation_score'] = validation_result['score']
                    successful_count += 1
                else:
                    data['validation_status'] = 'invalid'
                    data['validation_errors'] = validation_result['errors']
                    failed_count += 1
            else:
                data['validation_status'] = 'failed'
                failed_count += 1
                # Close DB cache connection if opened
                try:
                    if db_conn is not None:
                        db_conn.close()
                except Exception:
                    pass
            processed_data.append(data)
        
        print(f"       ✅ Successfully processed {successful_count} items")
        print(f"       ❌ Failed to process {failed_count} items")
        
        return processed_data
    
    def _validate_extracted_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data quality"""
        required_fields = ['year', 'make', 'model', 'price']
        present_fields = [field for field in required_fields if extracted_data.get(field)]
        
        score = len(present_fields) / len(required_fields)
        is_valid = score >= 0.5  # At least 50% of required fields present
        
        errors = []
        for field in required_fields:
            if not extracted_data.get(field):
                errors.append(f"Missing {field}")
        
        return {
            'is_valid': is_valid,
            'score': score,
            'errors': errors,
            'present_fields': present_fields,
            'missing_fields': [f for f in required_fields if f not in present_fields]
        }
    
    def _save_scraping_results(self, processed_data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[str]:
        """Save scraping results to files"""
        export_csv = bool((config.get('pipeline', {}) or {}).get('export_csv', True)) if isinstance(config, dict) else True
        if not export_csv:
            print("     🗃️  Skipping CSV export (pipeline.export_csv = false)")
            return []
        print("     📄 Saving scraping results to files...")
        
        output_dir = Path(config.get('pipeline', {}).get('output_directory', 'x987-data/results'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []
        
        # Optionally persist raw artifacts to separate files (paths referenced in CSV)
        capture_raw_html = bool(config.get('scraping', {}).get('capture_raw_html', False))
        capture_dom_text = bool(config.get('scraping', {}).get('capture_dom_text', False))
        artifacts_dir = output_dir / "artifacts"
        if capture_raw_html or capture_dom_text:
            artifacts_dir.mkdir(parents=True, exist_ok=True)

        # Save detailed scraping data
        detailed_filename = f"scraping_detailed_{timestamp}.csv"
        detailed_filepath = output_dir / detailed_filename
        
        try:
            with open(detailed_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if processed_data:
                    # Define a stable set of fields and avoid huge inline blobs
                    base_fields = [
                        'scraping_id', 'source_url', 'listing_url', 'title',
                        'canonical_url', 'collection_timestamp', 'scraping_timestamp', 'scraping_status',
                        'validation_status', 'validation_score'
                    ]
                    extra_fields = ['scraping_method', 'is_new', 'first_seen_at', 'cache_hit', 'cache_reason']
                    artifact_fields = ['raw_html_path', 'raw_text_path']
                    fieldnames = base_fields + extra_fields + ['extracted_data'] + artifact_fields
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for row in processed_data:
                        # Build a safe row copy
                        safe_row = {k: row.get(k, '') for k in base_fields + extra_fields}
                        safe_row['extracted_data'] = row.get('extracted_data', {})

                        # Persist artifacts if enabled
                        raw_html_path = ''
                        raw_text_path = ''
                        if capture_raw_html and row.get('raw_html'):
                            artifact_name = f"raw_{row.get('scraping_id','')}_{timestamp}.html"
                            (artifacts_dir / artifact_name).write_text(row.get('raw_html', ''), encoding='utf-8', errors='ignore')
                            raw_html_path = str(artifacts_dir / artifact_name)
                        if capture_dom_text and row.get('raw_text'):
                            artifact_name = f"text_{row.get('scraping_id','')}_{timestamp}.txt"
                            (artifacts_dir / artifact_name).write_text(row.get('raw_text', ''), encoding='utf-8', errors='ignore')
                            raw_text_path = str(artifacts_dir / artifact_name)
                        safe_row['raw_html_path'] = raw_html_path
                        safe_row['raw_text_path'] = raw_text_path

                        writer.writerow(safe_row)
            
            saved_files.append(str(detailed_filepath))
            print(f"       ✅ Created {detailed_filename} with {len(processed_data)} rows")
            
        except Exception as e:
            print(f"       ❌ Error creating {detailed_filename}: {e}")
        
        # Save summary data
        summary_filename = f"scraping_summary_{timestamp}.csv"
        summary_filepath = output_dir / summary_filename
        
        try:
            with open(summary_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['scraping_id', 'source_url', 'scraping_status', 'validation_status', 'validation_score', 'scraping_timestamp']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for data in processed_data:
                    row = {
                        'scraping_id': data.get('scraping_id', ''),
                        'source_url': data.get('source_url', ''),
                        'scraping_status': data.get('scraping_status', ''),
                        'validation_status': data.get('validation_status', ''),
                        'validation_score': data.get('validation_score', 0),
                        'scraping_timestamp': data.get('scraping_timestamp', '')
                    }
                    writer.writerow(row)
            
            saved_files.append(str(summary_filepath))
            print(f"       ✅ Created {summary_filename}")
            
        except Exception as e:
            print(f"       ❌ Error creating {summary_filename}: {e}")
        
        return saved_files
    
    def _generate_scraping_summary(self, collection_data: List[Dict[str, Any]], 
                                 processed_data: List[Dict[str, Any]], 
                                 saved_files: List[str]) -> Dict[str, Any]:
        """Generate comprehensive scraping summary"""
        
        # Calculate statistics
        total_urls = len(collection_data)
        successful_scrapes = len([d for d in processed_data if d.get('scraping_status') == 'success'])
        failed_scrapes = len([d for d in processed_data if d.get('scraping_status') == 'failed'])
        valid_data = len([d for d in processed_data if d.get('validation_status') == 'valid'])
        invalid_data = len([d for d in processed_data if d.get('validation_status') == 'invalid'])
        
        # Calculate average validation score
        validation_scores = [d.get('validation_score', 0) for d in processed_data if d.get('validation_score') is not None]
        avg_validation_score = sum(validation_scores) / len(validation_scores) if validation_scores else 0
        # Cache metrics
        cache_hits = len([d for d in processed_data if d.get('cache_hit') or d.get('scraping_method') == 'cache'])
        network_requests = len(processed_data) - cache_hits
        try:
            print(f"🧠 Cache hits: {cache_hits} | Network scrapes: {network_requests}")
        except Exception:
            pass

        summary = {
            "total_pages_scraped": total_urls,
            "scraping_data": processed_data,
            "successful_scrapes": successful_scrapes,
            "failed_scrapes": failed_scrapes,
            "valid_data": valid_data,
            "invalid_data": invalid_data,
            "cache_hits": cache_hits,
            "network_requests": network_requests,
            "saved_files": saved_files,
            "scraping_stats": {
                "scraping_success_rate": successful_scrapes / total_urls if total_urls > 0 else 0,
                "data_validation_rate": valid_data / successful_scrapes if successful_scrapes > 0 else 0,
                "average_validation_score": avg_validation_score,
                "total_processing_time": sum(d.get('scraping_metadata', {}).get('processing_time_ms', 0) for d in processed_data)
            },
            "scraping_timestamp": datetime.now().isoformat()
        }
        
        return summary


# Export the scraping step instance
SCRAPING_STEP = ScrapingStep()
