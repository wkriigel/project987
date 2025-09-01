"""
Fair Value Step - Calculates fair values and deal deltas for vehicles

This step implements the modular separation strategy for fair value calculation with
high-quality standardized process output and exceptional maintainability.

PROVIDES: Fair value calculations and deal delta analysis for vehicle listings
DEPENDS: x987.pipeline.steps.deduplication:DeduplicationStep and x987.config:get_config
CONSUMED BY: x987.pipeline.steps.ranking:RankingStep
CONTRACT: Provides fair values and deal deltas for ranking with configurable pricing model
TECH CHOICE: Modular fair value calculation with clear separation of concerns
RISK: Medium - fair value logic requires careful validation, pricing model assumptions may be incorrect
"""

import csv
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base import BasePipelineStep, StepResult


class FairValueStep(BasePipelineStep):
    """Fair value step implementing modular separation strategy"""
    
    def get_step_name(self) -> str:
        return "fair_value"
    
    def get_description(self) -> str:
        return "Calculates fair values and deal deltas for vehicle listings"
    
    def get_dependencies(self) -> List[str]:
        return ["deduplication"]  # Depends on deduplication step
    
    def get_required_config(self) -> List[str]:
        return ["fair_value"]  # Requires fair value configuration
    
    def run_step(self, config: Dict[str, Any], previous_results: Dict[str, StepResult], **kwargs) -> Any:
        """Execute the fair value calculation step with high-quality process output"""
        verbose = bool(kwargs.get('verbose'))
        import builtins
        _orig_print = builtins.print
        if not verbose:
            builtins.print = lambda *a, **k: None
        try:
            print("💰 Starting fair value calculation process...")
            print(f"📁 Working directory: {Path.cwd()}")
            print(f"⏰ Fair value calculation started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Get deduplication results
            if "deduplication" in previous_results:
                dedupe_result = previous_results["deduplication"]
                if not dedupe_result.is_success:
                    print("❌ Deduplication step must complete successfully before fair value calculation")
                    raise ValueError("Deduplication step must complete successfully before fair value calculation")

                deduped_data = dedupe_result.data.get("deduped_data", [])
            else:
                # Single step execution - use mock data
                print("⚠️  No deduplication results found, using mock data for single step execution")
                deduped_data = [
                {
                    'source_url': 'https://example.com/listing1',
                    'year': '2010',
                    'model': 'Cayman',
                    'price': '$35,000',
                    'mileage': '45,000',
                    'exterior_color': 'Guards Red',
                    'interior_color': 'Black'
                },
                {
                    'source_url': 'https://example.com/listing2',
                    'year': '2011',
                    'model': 'Cayman S',
                    'price': '$38,500',
                    'mileage': '52,000',
                    'exterior_color': 'Black',
                    'interior_color': 'Red'
                }
            ]
        
            if not deduped_data:
                print("⚠️  No data to calculate fair values for")
                return {
                    "total_listings": 0,
                    "listings_with_fair_value": 0,
                    "listings_with_deal_delta": 0,
                    "fair_value_data": [],
                    "fair_value_stats": {
                        "avg_fair_value": 0,
                        "avg_deal_delta": 0,
                        "fair_value_coverage": 0,
                        "deal_delta_coverage": 0
                    },
                    "fair_value_timestamp": datetime.now().isoformat()
                }
            
            print(f"📊 Processing {len(deduped_data)} deduplicated listings...")
        
            # Get fair value configuration
            fair_value_config = config.get("fair_value", {})
            base_value = fair_value_config.get("base_value_usd", 30500)
            year_step = fair_value_config.get("year_step_usd", 500)
            s_premium = fair_value_config.get("s_premium_usd", 7000)
            
            print(f"⚙️  Fair value configuration:")
            print(f"   • Base value: ${base_value:,}")
            print(f"   • Year step: ${year_step:,}")
            print(f"   • S premium: ${s_premium:,}")
            print()
            
            # Step 1: Calculate fair values
            print("💰 Step 1: Calculating fair values...")
            fair_value_data = self._calculate_fair_values(deduped_data, fair_value_config)
            
            # Step 2: Calculate deal deltas
            print("💰 Step 2: Calculating deal deltas...")
            deal_delta_data = self._calculate_deal_deltas(fair_value_data)
            
            # Step 3: Analyze fair value distribution
            print("📊 Step 3: Analyzing fair value distribution...")
            value_analysis = self._analyze_value_distribution(deal_delta_data)
            
            # Step 4: Save fair value results
            print("📄 Step 4: Saving fair value results...")
            saved_files = self._save_fair_value_results(deal_delta_data, config)
            
            # Step 5: Generate fair value summary
            print("📊 Step 5: Generating fair value summary...")
            fair_value_summary = self._generate_fair_value_summary(
                deduped_data, deal_delta_data, saved_files, fair_value_config
            )
            
            print("✅ Fair value calculation completed successfully!")
            print(f"📊 Processed {len(deduped_data)} listings")
            print(f"💰 Calculated fair values for {len([d for d in deal_delta_data if d.get('fair_value_usd')])} listings")
            print(f"📈 Calculated deal deltas for {len([d for d in deal_delta_data if d.get('deal_delta_usd')])} listings")
            print(f"📄 Saved results to {len(saved_files)} files")
            
            return fair_value_summary
        finally:
            builtins.print = _orig_print
    
    def _calculate_fair_values(self, deduped_data: List[Dict[str, Any]], 
                              fair_value_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate fair values for each vehicle listing"""
        print("     💰 Calculating fair values based on configuration...")
        
        fair_value_data = []
        base_value = fair_value_config.get("base_value_usd", 30500)
        year_step = fair_value_config.get("year_step_usd", 500)
        s_premium = fair_value_config.get("s_premium_usd", 7000)
        
        for i, listing in enumerate(deduped_data):
            print(f"       📝 Processing listing {i+1}/{len(deduped_data)}...")
            
            # Extract basic information
            year = self._extract_year(listing.get('year', ''))
            model = listing.get('model', '')
            trim = listing.get('trim', '')
            mileage = self._extract_mileage(listing.get('mileage', ''))
            # Colors per schema; accept legacy keys as fallback during transition
            exterior_color = listing.get('exterior') or listing.get('exterior_color', '')
            interior_color = listing.get('interior') or listing.get('interior_color', '')
            
            # Calculate base fair value
            fair_value = base_value
            
            # Adjust for year
            if year:
                year_diff = 2012 - year  # Assuming 2012 is the reference year
                fair_value += year_diff * year_step
                print(f"          📅 Year {year}: ${year_diff * year_step:,} adjustment")
            
            # Adjust for trim (S trim gets premium)
            if str(trim).strip().upper() == 'S' or (not trim and model and ' S' in str(model)):
                fair_value += s_premium
                print(f"          🚗 Trim S: ${s_premium:,} premium")
            
            # Adjust for mileage (high mileage gets discount)
            if mileage:
                mileage_discount = self._calculate_mileage_discount(mileage)
                fair_value += mileage_discount
                if mileage_discount < 0:
                    print(f"          🛣️  Mileage {mileage:,}: ${mileage_discount:,} discount")
                else:
                    print(f"          🛣️  Mileage {mileage:,}: ${mileage_discount:,} premium")
            
            # Adjust for colors (special colors get premium)
            color_premium = self._calculate_color_premium(exterior_color, interior_color)
            fair_value += color_premium
            if color_premium > 0:
                print(f"          🎨 Colors: ${color_premium:,} premium")
            
            # Add fair value to listing
            listing_with_fair_value = {
                **listing,
                'fair_value_usd': fair_value,
                'fair_value_calculation': {
                    'base_value': base_value,
                    'year_adjustment': year_diff * year_step if year else 0,
                    'model_premium': s_premium if (str(trim).strip().upper() == 'S' or (not trim and model and ' S' in str(model))) else 0,
                    'mileage_adjustment': mileage_discount if mileage else 0,
                    'color_premium': color_premium,
                    'calculation_timestamp': datetime.now().isoformat()
                }
            }
            
            fair_value_data.append(listing_with_fair_value)
            print(f"          ✅ Fair value: ${fair_value:,}")
        
        print(f"     ✅ Calculated fair values for {len(fair_value_data)} listings")
        return fair_value_data
    
    def _extract_year(self, year_str: str) -> Optional[int]:
        """Extract year as integer from string"""
        try:
            if isinstance(year_str, int):
                return year_str
            if isinstance(year_str, str):
                # Remove non-numeric characters
                year_clean = ''.join(c for c in year_str if c.isdigit())
                if year_clean:
                    return int(year_clean)
        except (ValueError, TypeError):
            pass
        return None
    
    def _extract_mileage(self, mileage_str: str) -> Optional[int]:
        """Extract mileage as integer from string"""
        try:
            if isinstance(mileage_str, int):
                return mileage_str
            if isinstance(mileage_str, str):
                # Remove non-numeric characters
                mileage_clean = ''.join(c for c in mileage_str if c.isdigit())
                if mileage_clean:
                    return int(mileage_clean)
        except (ValueError, TypeError):
            pass
        return None
    
    def _calculate_mileage_discount(self, mileage: int) -> int:
        """Calculate mileage-based discount/premium"""
        if mileage < 30000:
            return 1000  # Low mileage premium
        elif mileage < 50000:
            return 0  # Normal mileage
        elif mileage < 75000:
            return -500  # High mileage discount
        else:
            return -1500  # Very high mileage discount
    
    def _calculate_color_premium(self, exterior_color: str, interior_color: str) -> int:
        """Calculate color-based premium"""
        premium = 0
        
        # Exterior color premiums
        if exterior_color:
            exterior_lower = exterior_color.lower()
            if 'guards red' in exterior_lower:
                premium += 500
            elif 'black' in exterior_lower:
                premium += 300
            elif 'white' in exterior_lower:
                premium += 200
        
        # Interior color premiums
        if interior_color:
            interior_lower = interior_color.lower()
            if 'black' in interior_lower:
                premium += 200
            elif 'red' in interior_lower:
                premium += 300
        
        return premium
    
    def _calculate_deal_deltas(self, fair_value_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate deal deltas (difference between asking price and fair value)"""
        print("     📈 Calculating deal deltas...")
        
        deal_delta_data = []
        
        for listing in fair_value_data:
            fair_value = listing.get('fair_value_usd', 0)
            asking_price = self._extract_price(listing.get('price', ''))
            
            if asking_price and fair_value:
                # New definition: Deal Δ = fair_value - asking_price
                deal_delta = fair_value - asking_price
                deal_percentage = (deal_delta / fair_value) * 100
                
                # Categorize deal quality (positive = undervalued)
                if deal_delta > 1000:
                    deal_quality = "Excellent Deal"
                elif deal_delta > 0:
                    deal_quality = "Good Deal"
                elif deal_delta > -1000:
                    deal_quality = "Fair Price"
                else:
                    deal_quality = "Overpriced"
                
                listing_with_deal_delta = {
                    **listing,
                    'asking_price_usd': asking_price,
                    'deal_delta_usd': deal_delta,
                    'deal_percentage': deal_percentage,
                    'deal_quality': deal_quality
                }
            else:
                listing_with_deal_delta = {
                    **listing,
                    'asking_price_usd': None,
                    'deal_delta_usd': None,
                    'deal_percentage': None,
                    'deal_quality': 'Unknown'
                }
            
            deal_delta_data.append(listing_with_deal_delta)
        
        print(f"     ✅ Calculated deal deltas for {len(deal_delta_data)} listings")
        return deal_delta_data
    
    def _extract_price(self, price_str: str) -> Optional[int]:
        """Extract price as integer from string"""
        try:
            if isinstance(price_str, int):
                return price_str
            if isinstance(price_str, str):
                # Remove non-numeric characters except decimal point
                price_clean = ''.join(c for c in price_str if c.isdigit() or c == '.')
                if price_clean:
                    return int(float(price_clean))
        except (ValueError, TypeError):
            pass
        return None
    
    def _analyze_value_distribution(self, deal_delta_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the distribution of fair values and deal deltas"""
        print("     📊 Analyzing value distribution...")
        
        fair_values = [d.get('fair_value_usd', 0) for d in deal_delta_data if d.get('fair_value_usd')]
        deal_deltas = [d.get('deal_delta_usd', 0) for d in deal_delta_data if d.get('deal_delta_usd') is not None]
        
        analysis = {
            'fair_value_stats': {
                'count': len(fair_values),
                'min': min(fair_values) if fair_values else 0,
                'max': max(fair_values) if fair_values else 0,
                'average': sum(fair_values) / len(fair_values) if fair_values else 0,
                'total': sum(fair_values) if fair_values else 0
            },
            'deal_delta_stats': {
                'count': len(deal_deltas),
                'min': min(deal_deltas) if deal_deltas else 0,
                'max': max(deal_deltas) if deal_deltas else 0,
                'average': sum(deal_deltas) / len(deal_deltas) if deal_deltas else 0,
                'total': sum(deal_deltas) if deal_deltas else 0
            },
            'deal_quality_distribution': {}
        }
        
        # Count deal quality categories
        for listing in deal_delta_data:
            quality = listing.get('deal_quality', 'Unknown')
            if quality not in analysis['deal_quality_distribution']:
                analysis['deal_quality_distribution'][quality] = 0
            analysis['deal_quality_distribution'][quality] += 1
        
        print(f"       📊 Fair values: {len(fair_values)} listings, avg ${analysis['fair_value_stats']['average']:,.0f}")
        print(f"       📈 Deal deltas: {len(deal_deltas)} listings, avg ${analysis['deal_delta_stats']['average']:,.0f}")
        print(f"       🏷️  Deal quality distribution: {analysis['deal_quality_distribution']}")
        
        return analysis
    
    def _save_fair_value_results(self, deal_delta_data: List[Dict[str, Any]], 
                                config: Dict[str, Any]) -> List[str]:
        """Save fair value results to files"""
        print("     📄 Saving fair value results...")
        
        output_dir = Path(config.get('pipeline', {}).get('output_directory', 'x987-data/results'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []
        
        # Save detailed fair value data
        detailed_filename = f"fair_value_detailed_{timestamp}.csv"
        detailed_filepath = output_dir / detailed_filename
        
        try:
            with open(detailed_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                if deal_delta_data:
                    fieldnames = deal_delta_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for row in deal_delta_data:
                        writer.writerow(row)
            
            saved_files.append(str(detailed_filepath))
            print(f"       ✅ Created {detailed_filename} with {len(deal_delta_data)} rows")
            
        except Exception as e:
            print(f"       ❌ Error creating {detailed_filename}: {e}")
        
        # Save fair value summary
        summary_filename = f"fair_value_summary_{timestamp}.csv"
        summary_filepath = output_dir / summary_filename
        
        try:
            with open(summary_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                # Include trim as separate column for FE consumption
                fieldnames = ['source_url', 'year', 'model', 'trim', 'fair_value_usd', 'asking_price_usd', 'deal_delta_usd', 'deal_quality', 'timestamp']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for listing in deal_delta_data:
                    row = {
                        'source_url': listing.get('source_url', ''),
                        'year': listing.get('year', ''),
                        'model': listing.get('model', ''),
                        'trim': listing.get('trim', ''),
                        'fair_value_usd': listing.get('fair_value_usd', ''),
                        'asking_price_usd': listing.get('asking_price_usd', ''),
                        'deal_delta_usd': listing.get('deal_delta_usd', ''),
                        'deal_quality': listing.get('deal_quality', ''),
                        'timestamp': datetime.now().isoformat()
                    }
                    writer.writerow(row)
            
            saved_files.append(str(summary_filepath))
            print(f"       ✅ Created {summary_filename}")
            
        except Exception as e:
            print(f"       ❌ Error creating {summary_filename}: {e}")
        
        return saved_files
    
    def _generate_fair_value_summary(self, deduped_data: List[Dict[str, Any]], 
                                   deal_delta_data: List[Dict[str, Any]], 
                                   saved_files: List[str], 
                                   fair_value_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive fair value summary"""
        
        # Calculate statistics
        total_listings = len(deduped_data)
        listings_with_fair_value = len([d for d in deal_delta_data if d.get('fair_value_usd')])
        listings_with_deal_delta = len([d for d in deal_delta_data if d.get('deal_delta_usd') is not None])
        
        # Calculate average fair value and deal delta
        fair_values = [d.get('fair_value_usd', 0) for d in deal_delta_data if d.get('fair_value_usd')]
        deal_deltas = [d.get('deal_delta_usd', 0) for d in deal_delta_data if d.get('deal_delta_usd') is not None]
        
        avg_fair_value = sum(fair_values) / len(fair_values) if fair_values else 0
        avg_deal_delta = sum(deal_deltas) / len(deal_deltas) if deal_deltas else 0
        
        summary = {
            "total_listings": total_listings,
            "listings_with_fair_value": listings_with_fair_value,
            "listings_with_deal_delta": listings_with_deal_delta,
            "fair_value_data": deal_delta_data,
            "saved_files": saved_files,
            "fair_value_stats": {
                "avg_fair_value": avg_fair_value,
                "avg_deal_delta": avg_deal_delta,
                "fair_value_coverage": listings_with_fair_value / total_listings if total_listings > 0 else 0,
                "deal_delta_coverage": listings_with_deal_delta / total_listings if total_listings > 0 else 0
            },
            "fair_value_config": fair_value_config,
            "fair_value_timestamp": datetime.now().isoformat()
        }
        
        return summary


# Export the fair value step instance
FAIR_VALUE_STEP = FairValueStep()
