"""
Transformation Step - Implements modular separation strategy

This step transforms raw scraped data and creates separate files for each property
and option, implementing the modular separation strategy for exceptional maintainability.

PROVIDES: Data transformation with modular file output
DEPENDS: x987.pipeline.steps.scraping:ScrapingStep, x987.extractors:get_unified_extractor, x987.options:get_registry
CONSUMED BY: x987.pipeline.steps.deduplication:DeduplicationStep
CONTRACT: Creates normalized data and separate property/option files with quality scoring
TECH CHOICE: Modular file creation with clear separation of concerns
RISK: Medium - file creation affects data flow, depends on extractors and options systems
"""

import csv
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BasePipelineStep, StepResult


class TransformationStep(BasePipelineStep):
    """Transformation step implementing modular separation strategy"""
    
    def get_step_name(self) -> str:
        return "transformation"
    
    def get_description(self) -> str:
        return "Transforms raw scraped data into normalized format with separate files for each property and option"
    
    def get_dependencies(self) -> List[str]:
        return ["scraping"]  # Depends on scraping step
    
    def get_required_config(self) -> List[str]:
        return ["pipeline"]  # Needs pipeline configuration
    
    def run_step(self, config: Dict[str, Any], previous_results: Dict[str, StepResult], **kwargs) -> Any:
        """Execute the transformation step with modular separation strategy"""
        verbose = bool(kwargs.get('verbose'))
        import builtins
        _orig_print = builtins.print
        if not verbose:
            builtins.print = lambda *a, **k: None
        try:
            print("🔄 Starting transformation with modular separation strategy...")
            print(f"📁 Working directory: {Path.cwd()}")

            # Get scraping results
            if "scraping" in previous_results:
                scraping_result = previous_results["scraping"]
                if not scraping_result.is_success:
                    raise ValueError("Scraping step must complete successfully before transformation")

                scraping_data = scraping_result.data.get("scraping_data", [])
            else:
                # Single step execution - no mock data allowed
                print("❌ No scraping results found - scraping step must run first")
                raise ValueError("Scraping step must complete successfully before transformation")

            if not scraping_data:
                print("⚠️  No data to transform")
                return {
                    "total_listings": 0,
                    "successful_transformations": 0,
                    "failed_transformations": 0,
                    "transformed_data": [],
                    "files_created": [],
                    "transformation_stats": {
                        "success_rate": 0,
                        "error_rate": 0
                    }
                }

            print(f"📊 Processing {len(scraping_data)} scraped listings...")

            # Step 1: Extract basic properties using modular extractors
            print("🔍 Step 1: Extracting basic properties...")
            extracted_properties = self._extract_basic_properties(scraping_data)

            # Step 2: Detect options using modular options system
            print("🔧 Step 2: Detecting options...")
            options_data = self._detect_options(scraping_data)

            # Step 3: Create single unified transformed CSV
            print("📄 Step 3: Creating unified transformed CSV...")
            unified_csv_file, merged_data = self._create_unified_transformed_csv(extracted_properties, options_data, config)

            # Step 4: Generate transformation summary
            print("📊 Step 4: Generating transformation summary...")
            transformation_summary = self._generate_transformation_summary(
                merged_data, options_data, unified_csv_file
            )

            print("✅ Transformation completed successfully!")
            print(f"📊 Processed {len(extracted_properties)} listings")
            print(f"📄 Created unified CSV: {unified_csv_file}")

            return transformation_summary
        finally:
            builtins.print = _orig_print
    
    def _extract_basic_properties(self, scraping_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract basic properties using modular extractors system"""
        print("   🔍 Using modular extractors system...")
        
        try:
            # Import our modular extractors system
            from ...extractors import get_unified_extractor
            
            extractor = get_unified_extractor()
            extracted_listings = []
            
            for i, listing in enumerate(scraping_data):
                print(f"     📝 Processing listing {i+1}/{len(scraping_data)}...")
                
                # Extract all available properties
                extracted_data = {
                    'source_url': listing.get('source_url', ''),
                    'listing_url': listing.get('listing_url', ''),
                    'raw_text': listing.get('raw_text', ''),
                    'extraction_timestamp': datetime.now().isoformat()
                }
                
                # Extract year
                year_value = extractor.extract_year(listing.get('raw_text', ''))
                if year_value is not None:
                    extracted_data['year'] = str(year_value)
                    extracted_data['year_confidence'] = 1.0
                else:
                    extracted_data['year'] = 'Unknown'
                    extracted_data['year_confidence'] = 0.0
                
                # Extract price
                price_value = extractor.extract_price(listing.get('raw_text', ''))
                if price_value is not None:
                    extracted_data['price'] = f"${price_value:,}"
                    extracted_data['price_confidence'] = 1.0
                else:
                    extracted_data['price'] = 'Unknown'
                    extracted_data['price_confidence'] = 0.0
                
                # Extract mileage
                mileage_value = extractor.extract_mileage(listing.get('raw_text', ''))
                if mileage_value is not None:
                    extracted_data['mileage'] = f"{mileage_value:,}"
                    extracted_data['mileage_confidence'] = 1.0
                else:
                    extracted_data['mileage'] = 'Unknown'
                    extracted_data['mileage_confidence'] = 0.0
                
                # Extract model/trim as separate fields
                model_value, trim_value = extractor.extract_model_trim(listing.get('raw_text', ''))
                if model_value and model_value != "Unknown":
                    extracted_data['model'] = model_value
                    extracted_data['trim'] = trim_value or "Base"
                    extracted_data['model_confidence'] = 1.0
                    extracted_data['trim_confidence'] = 1.0 if trim_value else 0.8
                else:
                    extracted_data['model'] = 'Unknown'
                    extracted_data['trim'] = 'Base'
                    extracted_data['model_confidence'] = 0.0
                    extracted_data['trim_confidence'] = 0.0
                
                # Extract colors as separate fields (stop merging); adopt schema names
                exterior_color, interior_color = extractor.extract_colors(listing.get('raw_text', ''))
                if exterior_color:
                    extracted_data['exterior'] = exterior_color
                    extracted_data['exterior_confidence'] = 1.0
                else:
                    extracted_data['exterior'] = 'Unknown'
                    extracted_data['exterior_confidence'] = 0.0
                
                if interior_color:
                    extracted_data['interior'] = interior_color
                    extracted_data['interior_confidence'] = 1.0
                else:
                    extracted_data['interior'] = 'Unknown'
                    extracted_data['interior_confidence'] = 0.0
                
                # Extract source
                source_value = extractor.extract_source(listing.get('raw_text', ''), listing.get('source_url', ''))
                if source_value and source_value != "unknown":
                    extracted_data['source'] = source_value
                    extracted_data['source_confidence'] = 1.0
                else:
                    extracted_data['source'] = 'Unknown'
                    extracted_data['source_confidence'] = 0.0
                
                # Add additional metadata
                extracted_data['extraction_method'] = 'unified_extractor'
                extracted_data['data_quality_score'] = self._calculate_data_quality_score(extracted_data)
                
                extracted_listings.append(extracted_data)
            
            print(f"   ✅ Successfully extracted properties from {len(extracted_listings)} listings")
            return extracted_listings
            
        except Exception as e:
            print(f"   ❌ Error in property extraction: {e}")
            print(f"   🔍 Debug info: {type(e).__name__}: {str(e)}")
            raise e
    
    def _calculate_data_quality_score(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate a data quality score based on extracted fields"""
        # Prefer separate fields only
        quality_fields = ['year', 'price', 'mileage', 'model', 'trim', 'exterior', 'interior', 'source']
        total_fields = len(quality_fields)
        valid_fields = 0
        
        for field in quality_fields:
            value = extracted_data.get(field, '')
            if value and value != 'Unknown':
                valid_fields += 1
        
        return valid_fields / total_fields if total_fields > 0 else 0.0
    
    def _detect_options(self, scraping_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect options using modular options system"""
        print("   🔧 Using modular options system...")
        
        try:
            # Import our modular options system
            from ...options import get_registry
            from ...config import get_config
            
            options_registry = get_registry()
            all_options = options_registry.get_all_options()
            
            print(f"   📋 Found {len(all_options)} available options to detect")
            
            # Load MSRP catalog from config (option_id -> msrp_int)
            cfg = get_config()
            options_cfg = cfg.get_options_config() or {}
            msrp_catalog = (options_cfg.get('msrp_catalog') or {}) if isinstance(options_cfg, dict) else {}
            # Normalize keys to strings for consistent lookup
            msrp_catalog_norm = {str(k): int(v) for k, v in msrp_catalog.items() if v is not None}
            
            options_data = []
            
            for i, listing in enumerate(scraping_data):
                print(f"     🔍 Detecting options for listing {i+1}/{len(scraping_data)}...")
                
                listing_options = {
                    'source_url': listing.get('source_url', ''),
                    'raw_text': listing.get('raw_text', ''),
                    'detection_timestamp': datetime.now().isoformat(),
                    'detected_options': [],
                    'options_by_category': {},
                    'total_options_value': 0,
                    'total_options_msrp': 0
                }
                
                raw_text = listing.get('raw_text', '')
                
                # Check each available option
                for option in all_options:
                    try:
                        if hasattr(option, 'is_present') and option.is_present(raw_text):
                            option_info = {
                                'id': getattr(option, 'get_id', lambda: 'unknown')(),
                                'display': getattr(option, 'get_display', lambda: 'Unknown Option')(),
                                'category': getattr(option, 'get_category', lambda: 'unknown')(),
                                'value': getattr(option, 'get_value', lambda x: 0)(raw_text),
                                'confidence': getattr(option, 'get_confidence', lambda: 1.0)()
                            }
                            
                            listing_options['detected_options'].append(option_info)
                            listing_options['total_options_value'] += option_info['value']
                            # Add MSRP if available for this option id
                            opt_id = str(option_info['id'])
                            if opt_id in msrp_catalog_norm:
                                listing_options['total_options_msrp'] += int(msrp_catalog_norm[opt_id])
                            
                            # Group by category
                            category = option_info['category']
                            if category not in listing_options['options_by_category']:
                                listing_options['options_by_category'][category] = []
                            listing_options['options_by_category'][category].append(option_info)
                    
                    except Exception as e:
                        print(f"       ⚠️  Error checking option: {e}")
                        continue
                
                options_data.append(listing_options)
                
                if listing_options['detected_options']:
                    print(f"       ✅ Detected {len(listing_options['detected_options'])} options (Value ${listing_options['total_options_value']:,}, MSRP ${listing_options['total_options_msrp']:,})")
                else:
                    print(f"       ⚠️  No options detected")
            
            print(f"   ✅ Successfully detected options from {len(options_data)} listings")
            return options_data
            
        except Exception as e:
            print(f"   ❌ Error in options detection: {e}")
            raise e
    
    def _create_unified_transformed_csv(self, extracted_properties: List[Dict[str, Any]], 
                                   options_data: List[Dict[str, Any]], 
                                   config: Dict[str, Any]) -> tuple[str, List[Dict[str, Any]]]:
        """Create the unified transformed CSV with all data"""
        print("   📄 Creating unified transformed CSV...")
        
        output_dir = Path(config.get('pipeline', {}).get('output_directory', 'x987-data/results'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transformed_data_{timestamp}.csv"
        filepath = output_dir / filename
        
        try:
            # Merge properties and options data
            merged_data = []
            
            for i, (properties, options) in enumerate(zip(extracted_properties, options_data)):
                merged_row = {
                    'listing_id': i + 1,
                    'source_url': properties.get('source_url', ''),
                    'listing_url': properties.get('listing_url', ''),
                    'extraction_timestamp': properties.get('extraction_timestamp', ''),
                    'detection_timestamp': options.get('detection_timestamp', ''),
                    'data_quality_score': properties.get('data_quality_score', 0),
                    
                    # Basic properties
                    # Separate fields per CSV schema
                    'year': properties.get('year', ''),
                    'year_confidence': properties.get('year_confidence', ''),
                    'price': properties.get('price', ''),
                    'price_confidence': properties.get('price_confidence', ''),
                    'mileage': properties.get('mileage', ''),
                    'mileage_confidence': properties.get('mileage_confidence', ''),
                    'model': properties.get('model', ''),
                    'trim': properties.get('trim', ''),
                    'model_confidence': properties.get('model_confidence', ''),
                    'trim_confidence': properties.get('trim_confidence', ''),
                    'exterior': properties.get('exterior', ''),
                    'interior': properties.get('interior', ''),
                    'exterior_confidence': properties.get('exterior_confidence', ''),
                    'interior_confidence': properties.get('interior_confidence', ''),
                    'source': properties.get('source', ''),
                    'source_confidence': properties.get('source_confidence', ''),
                    
                    # Options summary
                    'total_options': options.get('total_options', 0),
                    'total_options_value': options.get('total_options_value', 0),
                    'total_options_msrp': options.get('total_options_msrp', 0),
                    'options_categories': ', '.join(options.get('options_by_category', {}).keys()),
                    'options_list': ', '.join([opt.get('display', '') for opt in options.get('detected_options', [])])
                }
                
                merged_data.append(merged_row)
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if merged_data:
                    fieldnames = merged_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for row in merged_data:
                        writer.writerow(row)
            
            print(f"       ✅ Created {filename} with {len(merged_data)} rows")
            return str(filepath), merged_data
            
        except Exception as e:
            print(f"       ❌ Error creating unified CSV: {e}")
            return "", []
    
    def _generate_transformation_summary(self, merged_data: List[Dict[str, Any]], 
                                       options_data: List[Dict[str, Any]], 
                                       unified_csv_file: str) -> Dict[str, Any]:
        """Generate comprehensive transformation summary"""
        
        # Calculate statistics
        total_listings = len(merged_data)
        successful_transformations = len([p for p in merged_data if p.get('data_quality_score', 0) > 0.3])
        failed_transformations = total_listings - successful_transformations
        
        # Options statistics
        total_options_detected = sum(len(opt.get('detected_options', [])) for opt in options_data)
        total_options_value = sum(opt.get('total_options_value', 0) for opt in options_data)
        
        # File creation statistics
        total_files_created = 1 # Only unified CSV is created
        
        # Data quality statistics
        avg_quality_score = sum(p.get('data_quality_score', 0) for p in merged_data) / total_listings if total_listings > 0 else 0
        
        summary = {
            "total_listings": total_listings,
            "successful_transformations": successful_transformations,
            "failed_transformations": failed_transformations,
            "transformed_data": merged_data,
            "options_data": options_data,
            "files_created": {
                "unified_csv": unified_csv_file
            },
            "total_files_created": total_files_created,
            "transformation_stats": {
                "success_rate": successful_transformations / total_listings if total_listings > 0 else 0,
                "error_rate": failed_transformations / total_listings if total_listings > 0 else 0,
                "options_detected": total_options_detected,
                "total_options_value": total_options_value,
                "average_options_per_listing": total_options_detected / total_listings if total_listings > 0 else 0,
                "average_data_quality_score": avg_quality_score
            },
            "transformation_timestamp": datetime.now().isoformat()
        }
        
        return summary


# Export the transformation step instance
TRANSFORMATION_STEP = TransformationStep()
