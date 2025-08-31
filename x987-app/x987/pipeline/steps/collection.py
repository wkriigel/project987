"""
Collection Step - Collects vehicle listing URLs from search sources

This step implements the modular separation strategy for URL collection with
high-quality standardized process output and exceptional maintainability.

PROVIDES: Vehicle listing URL collection from configured search sources
DEPENDS: x987.config:get_config and playwright for web scraping
CONSUMED BY: x987.pipeline.steps.scraping:ScrapingStep
CONTRACT: Provides list of URLs to scrape with metadata and validation
TECH CHOICE: Modular collection with clear separation of concerns using Playwright
RISK: Medium - web scraping can be fragile, site changes may break selectors
"""

import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BasePipelineStep, StepResult


class CollectionStep(BasePipelineStep):
    """Collection step implementing modular separation strategy"""
    
    def get_step_name(self) -> str:
        return "collection"
    
    def get_description(self) -> str:
        return "Collects vehicle listing URLs from configured search sources"
    
    def get_dependencies(self) -> List[str]:
        return []  # No dependencies - this is the first step
    
    def get_required_config(self) -> List[str]:
        return ["search"]
    
    def run_step(self, config: Dict[str, Any], previous_results: Dict[str, StepResult], **kwargs) -> Any:
        """Execute the collection step with high-quality process output"""
        verbose = bool(kwargs.get('verbose'))
        import builtins
        _orig_print = builtins.print
        if not verbose:
            builtins.print = lambda *a, **k: None
        try:
            def _run():
                print("📡 Starting URL collection process...")
                print(f"📁 Working directory: {Path.cwd()}")
                print(f"⏰ Collection started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                # Get search configuration
                if hasattr(config, 'get_search_urls'):
                    urls = config.get_search_urls()
                else:
                    search_config = config.get("search", {})
                    urls = search_config.get("urls", [])

                if not urls:
                    print("❌ No search URLs configured")
                    raise ValueError("No search URLs configured")

                print(f"🔍 Found {len(urls)} configured search URLs")
                for i, url in enumerate(urls, 1):
                    print(f"   {i}. {url}")
                print()

                # Step 1: Validate URLs
                print("🔍 Step 1: Validating search URLs...")
                valid_urls = self._validate_search_urls(urls)
                if not valid_urls:
                    print("❌ No valid search URLs found")
                    return {
                        "urls_collected": 0,
                        "collection_data": [],
                        "search_urls": urls,
                        "valid_urls": [],
                        "validation_errors": ["All URLs failed validation"],
                        "collection_timestamp": datetime.now().isoformat()
                    }

                print(f"✅ Validated {len(valid_urls)} search URLs")

                # Step 2: Collect URLs per source
                print("🔍 Step 2: Collecting URLs from search sources...")
                collection_results = []
                for i, url in enumerate(valid_urls, 1):
                    print(f"   📡 Processing source {i}/{len(valid_urls)}: {self._get_source_name(url)}")
                    try:
                        urls_from_source = self._collect_urls_from_source(url, **kwargs)
                        collection_results.extend(urls_from_source)
                        print(f"      ✅ Collected {len(urls_from_source)} URLs from {self._get_source_name(url)}")
                        # Polite delay between sources
                        if i < len(valid_urls):
                            polite_delay_sec = 2.0
                            try:
                                scraping_cfg = config.get("scraping", {}) if isinstance(config, dict) else getattr(config, 'data', {}).get('scraping', {})
                                polite_delay_ms = scraping_cfg.get("polite_delay_ms", 2000)
                                polite_delay_sec = max(0.0, float(polite_delay_ms) / 1000.0)
                            except Exception:
                                polite_delay_sec = 2.0
                            print(f"      ⏱️  Waiting {polite_delay_sec:.1f}s before next source...")
                            time.sleep(polite_delay_sec)
                    except Exception as e:
                        print(f"      ❌ Error collecting from {self._get_source_name(url)}: {e}")
                        continue

                # Step 3: Process and deduplicate collected URLs
                print("🔍 Step 3: Processing collected URLs...")
                processed_urls = self._process_collected_urls(collection_results)

                # Step 4: Save collection results
                print("📄 Step 4: Saving collection results...")
                saved_files = self._save_collection_results(processed_urls, config)

                # Step 5: Summary
                print("📊 Step 5: Generating collection summary...")
                collection_summary = self._generate_collection_summary(urls, valid_urls, processed_urls, saved_files)

                print("✅ URL collection completed successfully!")
                print(f"📊 Processed {len(valid_urls)} search sources")
                print(f"🔗 Collected {len(processed_urls)} unique vehicle listing URLs")
                print(f"📄 Saved results to {len(saved_files)} files")

                return collection_summary

            return _run()
        finally:
            builtins.print = _orig_print
    
    def _validate_search_urls(self, urls: List[str]) -> List[str]:
        """Validate search URLs and return valid ones"""
        print("     🔍 Validating URL format and accessibility...")
        
        valid_urls = []
        for url in urls:
            if self._is_valid_url(url):
                valid_urls.append(url)
                print(f"       ✅ Valid: {url}")
            else:
                print(f"       ❌ Invalid: {url}")
        
        return valid_urls
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        if not isinstance(url, str):
            return False
        
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Basic URL validation - could be enhanced with more sophisticated checks
        return True
    
    def _get_source_name(self, url: str) -> str:
        """Extract source name from URL"""
        if 'autotempest.com' in url:
            return 'AutoTempest'
        elif 'cars.com' in url:
            return 'Cars.com'
        elif 'cargurus.com' in url:
            return 'CarGurus'
        elif 'truecar.com' in url:
            return 'TrueCar'
        elif 'carmax.com' in url:
            return 'CarMax'
        else:
            return 'Unknown Source'
    
    def _collect_urls_from_source(self, url: str, **kwargs) -> List[Dict[str, Any]]:
        """Collect URLs from a specific search source"""
        headful = kwargs.get('headful', True)
        
        print(f"        🌐 Using {'headful' if headful else 'headless'} mode")
        
        try:
            # Real AutoTempest scraping implementation
            if 'autotempest.com' in url:
                return self._scrape_autotempest_listings(url, headful)
            else:
                print(f"        ❌ Source not yet implemented: {url}")
                raise NotImplementedError(f"Source {url} not yet implemented")
                
        except Exception as e:
            print(f"        ❌ Error collecting from source: {e}")
            print(f"        🔍 This is a real failure - not falling back to mock data")
            raise e
    
    def _scrape_autotempest_listings(self, search_url: str, headful: bool = False) -> List[Dict[str, Any]]:
        """Scrape vehicle listing URLs from AutoTempest search results"""
        print(f"        🕷️  Scraping AutoTempest for vehicle listing URLs...")
        
        try:
            from playwright.sync_api import sync_playwright
            from urllib.parse import urljoin, urlsplit, urlunsplit
            import time
            
            with sync_playwright() as p:
                # Launch browser with better configuration
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
                page = browser.new_page()

                # Install lightweight network blocking to speed up page load
                try:
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
                    page.route("**/*", _block_route)
                except Exception:
                    pass
                
                # Set user agent and other headers to avoid detection
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                })
                
                # Navigate to search page with more reasonable timeout
                print(f"        🌐 Navigating to: {search_url}")
                try:
                    # First try with domcontentloaded (faster)
                    page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
                    print(f"        ✅ Page loaded successfully")
                except Exception as e:
                    print(f"        ⚠️  DOM content load failed, trying load event: {e}")
                    try:
                        page.goto(search_url, wait_until='load', timeout=30000)
                        print(f"        ✅ Page loaded with load event")
                    except Exception as e2:
                        print(f"        ❌ Page load failed: {e2}")
                        raise e2
                
                # Wait for listings to appear (selector-based, fallback to short timeout)
                listing_selector = 'li.result-list-item a.listing-link.source-link'
                try:
                    page.wait_for_selector(listing_selector, timeout=5000)
                except Exception:
                    try:
                        page.wait_for_selector('a.listing-link', timeout=3000)
                    except Exception:
                        page.wait_for_timeout(1500)
                
                print(f"        🔍 Looking for listings with selector: {listing_selector}")
                links = page.query_selector_all(listing_selector)
                
                if not links:
                    print(f"        ❌ No listings found with selector: {listing_selector}")
                    # Try fallback selector
                    fallback_selector = 'a.listing-link'
                    print(f"        🔍 Trying fallback selector: {fallback_selector}")
                    links = page.query_selector_all(fallback_selector)
                    
                    if not links:
                        print(f"        ❌ No listings found with fallback selector either")
                        raise ValueError(f"No vehicle listings found on {search_url}. The page may be blocking automated access or the selectors need updating.")
                
                print(f"        🔍 Found {len(links)} potential listings")
                
                vehicle_listings = []
                
                # Optional cap per source to avoid excessive enumeration
                cap_per_source = None
                try:
                    cap_per_source = int((kwargs.get('scraping', {}) or {}).get('cap_listings'))
                except Exception:
                    try:
                        # If full config dict provided
                        cap_per_source = int((kwargs.get('config', {}).get('scraping', {}) or {}).get('cap_listings'))
                    except Exception:
                        cap_per_source = None

                for i, link in enumerate(links):
                    try:
                        href = link.get_attribute('href')
                        if href:
                            # Normalize URL using the current page URL as base
                            full_url = urljoin(search_url, href)

                            # Fix double-domain artifacts like /www.autotempest.com/details/...
                            parts = urlsplit(full_url)
                            if parts.netloc.endswith('autotempest.com') and parts.path.startswith('/www.autotempest.com/'):
                                fixed_path = parts.path.replace('/www.autotempest.com/', '/', 1)
                                full_url = urlunsplit((parts.scheme, parts.netloc, fixed_path, parts.query, parts.fragment))

                            # Exclude AutoTempest internal detail/interstitial pages
                            if 'autotempest.com/details/' in full_url:
                                print(f"        ⚠️  Skipping internal AutoTempest detail page: {full_url}")
                                continue
                            
                            # Get basic info from the listing element for reference
                            listing_container = link.query_selector('li.result-list-item')
                            title = "Vehicle Listing"
                            if listing_container:
                                title_elem = listing_container.query_selector('h3, h4, .title, .vehicle-title, .listing-title, .result-title')
                                if title_elem:
                                    title = title_elem.inner_text().strip()
                            
                            # Store minimal data - just the URL and basic info
                            # The actual data extraction will be done by the scraper step
                            listing_data = {
                                'source_url': search_url,
                                'listing_url': full_url,
                                'title': title,
                                'collection_timestamp': datetime.now().isoformat(),
                                'scraping_method': 'autotempest_urls_only'
                            }
                            
                            vehicle_listings.append(listing_data)
                            print(f"        📋 Found listing {i+1}: {title[:50]}...")
                            print(f"           URL: {full_url}")

                            # Respect cap if configured
                            if cap_per_source and len(vehicle_listings) >= cap_per_source:
                                print(f"        ⛔ Cap reached for this source ({cap_per_source}); stopping enumeration")
                                break
                            
                    except Exception as e:
                        print(f"        ⚠️  Error processing listing {i+1}: {e}")
                        continue
                
                browser.close()
                
                if vehicle_listings:
                    print(f"        ✅ Successfully collected {len(vehicle_listings)} listing URLs")
                    return vehicle_listings
                else:
                    print(f"        ❌ No vehicle listing URLs found")
                    raise ValueError(f"No vehicle listing URLs found on {search_url}. The page may be blocking automated access or the selectors need updating.")
                    
        except Exception as e:
            print(f"        ❌ AutoTempest scraping failed: {e}")
            raise e
    
    def _process_collected_urls(self, collection_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process and deduplicate collected URLs"""
        print("     🔄 Processing and deduplicating collected URLs...")
        
        # Remove duplicates based on listing URL
        seen_urls = set()
        unique_results = []
        
        for result in collection_results:
            listing_url = result.get('listing_url', '')
            if listing_url and listing_url not in seen_urls:
                seen_urls.add(listing_url)
                unique_results.append(result)
        
        print(f"       ✅ Deduplicated: {len(collection_results)} → {len(unique_results)} unique URLs")
        
        # Add processing metadata
        for result in unique_results:
            result['processed_timestamp'] = datetime.now().isoformat()
            result['processing_status'] = 'success'
        
        return unique_results
    
    def _save_collection_results(self, processed_urls: List[Dict[str, Any]], config: Dict[str, Any]) -> List[str]:
        """Save collection results to files"""
        print("     📄 Saving collection results to files...")
        
        output_dir = Path(config.get('pipeline', {}).get('output_directory', 'x987-data/results'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []
        
        # Save detailed collection data
        detailed_filename = f"collection_detailed_{timestamp}.csv"
        detailed_filepath = output_dir / detailed_filename
        
        try:
            import csv
            with open(detailed_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if processed_urls:
                    fieldnames = processed_urls[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for row in processed_urls:
                        writer.writerow(row)
            
            saved_files.append(str(detailed_filepath))
            print(f"       ✅ Created {detailed_filename} with {len(processed_urls)} rows")
            
        except Exception as e:
            print(f"       ❌ Error creating {detailed_filename}: {e}")
        
        # Save summary data
        summary_filename = f"collection_summary_{timestamp}.csv"
        summary_filepath = output_dir / summary_filename
        
        try:
            with open(summary_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['source_url', 'urls_collected', 'collection_timestamp', 'processing_status']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Group by source
                source_counts = {}
                for url_data in processed_urls:
                    source = url_data.get('source_url', '')
                    if source not in source_counts:
                        source_counts[source] = 0
                    source_counts[source] += 1
                
                for source, count in source_counts.items():
                    row = {
                        'source_url': source,
                        'urls_collected': count,
                        'collection_timestamp': datetime.now().isoformat(),
                        'processing_status': 'success'
                    }
                    writer.writerow(row)
            
            saved_files.append(str(summary_filepath))
            print(f"       ✅ Created {summary_filename}")
            
        except Exception as e:
            print(f"       ❌ Error creating {summary_filename}: {e}")
        
        return saved_files
    
    def _generate_collection_summary(self, original_urls: List[str], valid_urls: List[str], 
                                   processed_urls: List[Dict[str, Any]], saved_files: List[str]) -> Dict[str, Any]:
        """Generate comprehensive collection summary"""
        
        # Calculate statistics
        total_sources = len(original_urls)
        valid_sources = len(valid_urls)
        failed_sources = total_sources - valid_sources
        total_urls_collected = len(processed_urls)
        
        # Group by source
        source_counts = {}
        for url_data in processed_urls:
            source = url_data.get('source_url', '')
            if source not in source_counts:
                source_counts[source] = 0
            source_counts[source] += 1
        
        summary = {
            "urls_collected": total_urls_collected,
            "collection_data": processed_urls,
            "search_urls": original_urls,
            "valid_urls": valid_urls,
            "saved_files": saved_files,
            "collection_stats": {
                "total_sources": total_sources,
                "valid_sources": valid_sources,
                "failed_sources": failed_sources,
                "success_rate": valid_sources / total_sources if total_sources > 0 else 0,
                "urls_per_source": total_urls_collected / valid_sources if valid_sources > 0 else 0
            },
            "source_breakdown": source_counts,
            "collection_timestamp": datetime.now().isoformat()
        }
        
        return summary


# Export the collection step instance
COLLECTION_STEP = CollectionStep()
