"""
Ranking Step - Ranks vehicle listings by deal delta and other criteria

This file contains everything needed to rank and sort vehicle listings.
It's completely self-contained and can be modified independently.

PROVIDES: Vehicle listing ranking by deal delta and other criteria
DEPENDS: x987.pipeline.steps.fair_value:FairValueStep
CONSUMED BY: x987.pipeline.steps.view:ViewStep and end users
CONTRACT: Provides ranked vehicle listings with deal quality assessments
TECH CHOICE: Modular ranking with clear separation of concerns
RISK: Medium - ranking logic affects user experience and decision making
"""

from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from .base import BasePipelineStep, StepResult


class RankingStep(BasePipelineStep):
    """Ranking step implementing modular separation strategy"""
    
    def get_step_name(self) -> str:
        return "ranking"
    
    def get_description(self) -> str:
        return "Ranks vehicle listings by deal delta and other criteria"
    
    def get_dependencies(self) -> List[str]:
        return ["fair_value"]  # Depends on fair value step
    
    def get_required_config(self) -> List[str]:
        return []  # No specific config required
    
    def run_step(self, config: Dict[str, Any], previous_results: Dict[str, StepResult], **kwargs) -> Any:
        """Execute the ranking step with high-quality process output"""
        verbose = bool(kwargs.get('verbose'))
        import builtins
        _orig_print = builtins.print
        if not verbose:
            builtins.print = lambda *a, **k: None
        try:
            print("🏆 Starting ranking process...")
            print(f"📁 Working directory: {Path.cwd()}")
            print(f"⏰ Ranking started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Get fair value results
            if "fair_value" in previous_results:
                fair_value_result = previous_results["fair_value"]
                if not fair_value_result.is_success:
                    print("❌ Fair value step must complete successfully before ranking")
                    raise ValueError("Fair value step must complete successfully before ranking")

                fair_value_data = fair_value_result.data.get("fair_value_data", [])
            else:
                # Single step execution - use mock data
                print("⚠️  No fair value results found, using mock data for single step execution")
                fair_value_data = [
                {
                    'source_url': 'https://example.com/listing1',
                    'year': '2010',
                    'model': 'Cayman',
                    'price': '$35,000',
                    'fair_value_usd': 32000,
                    'deal_delta_usd': 3000,
                    'deal_quality': 'Good Deal',
                    'transmission': 'Manual',
                    'mileage': '45,000',
                    'exterior_color': 'Guards Red',
                    'interior_color': 'Black'
                },
                {
                    'source_url': 'https://example.com/listing2',
                    'year': '2011',
                    'model': 'Cayman S',
                    'price': '$38,500',
                    'fair_value_usd': 37500,
                    'deal_delta_usd': 1000,
                    'deal_quality': 'Fair Deal',
                    'transmission': 'Automatic',
                    'mileage': '52,000',
                    'exterior_color': 'Black',
                    'interior_color': 'Red'
                },
                {
                    'source_url': 'https://example.com/listing3',
                    'year': '2009',
                    'model': 'Cayman',
                    'price': '$32,000',
                    'fair_value_usd': 30000,
                    'deal_delta_usd': 2000,
                    'deal_quality': 'Good Deal',
                    'transmission': 'Manual',
                    'mileage': '60,000',
                    'exterior_color': 'Silver',
                    'interior_color': 'Black'
                }
            ]

            if not fair_value_data:
                print("⚠️  No data to rank")
                return {
                    "total_listings": 0,
                    "ranked_data": [],
                    "top_deals": [],
                    "best_deal": None,
                    "ranking_stats": {
                        "avg_deal_delta": 0,
                        "best_deal_delta": 0,
                        "worst_deal_delta": 0,
                        "automatic_percentage": 0,
                        "manual_percentage": 0
                    },
                    "ranking_timestamp": datetime.now().isoformat()
                }
            
            print(f"📊 Processing {len(fair_value_data)} listings for ranking...")

            # Perform ranking analysis
            ranked_data = self._perform_ranking_analysis(fair_value_data)
            
            # Calculate comprehensive statistics
            ranking_stats = self._calculate_ranking_statistics(ranked_data)
            
            # Identify top deals and categories
            top_deals = self._identify_top_deals(ranked_data)
            category_rankings = self._create_category_rankings(ranked_data)
            
            # Save ranking results
            files_created = self._save_ranking_results(ranked_data, ranking_stats, top_deals, category_rankings)
            
            # Generate summary
            summary = self._generate_ranking_summary(ranked_data, ranking_stats, top_deals, files_created)
            
            print("✅ Ranking process completed successfully!")
            print(f"📈 Ranked {len(ranked_data)} listings")
            print(f"🏆 Best deal: {ranking_stats['best_deal_delta']:,.0f} USD")
            print(f"📁 Files created: {len(files_created)}")
            
            return summary
        finally:
            builtins.print = _orig_print

    def _perform_ranking_analysis(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform comprehensive ranking analysis on the data"""
        print("🔍 Performing ranking analysis...")
        
        # Create enhanced ranking data with scores
        ranked_data = []
        for item in data:
            # Calculate composite score based on multiple factors
            score = self._calculate_composite_score(item)
            
            # Create enhanced item with ranking information
            ranked_item = item.copy()
            ranked_item['composite_score'] = score
            ranked_item['ranking_timestamp'] = datetime.now().isoformat()
            
            ranked_data.append(ranked_item)
        
        # Sort by composite score (descending - best deals first)
        ranked_data.sort(key=lambda x: x.get('composite_score', 0), reverse=True)
        
        # Add rank position
        for i, item in enumerate(ranked_data):
            item['rank'] = i + 1
        
        print(f"📊 Ranking analysis completed for {len(ranked_data)} listings")
        return ranked_data

    def _calculate_composite_score(self, item: Dict[str, Any]) -> float:
        """Calculate a composite score for ranking"""
        score = 0.0
        
        # Deal delta score (higher is better) -- Deal Δ = fair - asking
        deal_delta = item.get('deal_delta_usd', 0)
        if deal_delta:
            score += deal_delta * 0.1  # 10% weight
        
        # Year score (newer is better)
        year = item.get('year', 0)
        if year and str(year).isdigit():
            try:
                score += int(year) * 0.01  # 1% weight for year
            except (ValueError, TypeError):
                pass
        
        # Mileage score (lower is better)
        mileage = item.get('mileage', 0)
        if mileage and str(mileage).replace(',', '').isdigit():
            try:
                mileage_num = int(str(mileage).replace(',', ''))
                score += (100000 - mileage_num) * 0.0001  # Lower mileage gets higher score
            except (ValueError, TypeError):
                pass
        
        # Model premium (S models get bonus)
        model = item.get('model', '')
        if 'S' in model:
            score += 1000  # S model premium
        
        # Transmission preference (Manual gets bonus)
        transmission = item.get('transmission', '')
        if 'Manual' in transmission:
            score += 500  # Manual transmission preference
        
        return score

    def _calculate_ranking_statistics(self, ranked_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive ranking statistics"""
        print("📊 Calculating ranking statistics...")
        
        if not ranked_data:
            return {
                "avg_deal_delta": 0,
                "best_deal_delta": 0,
                "worst_deal_delta": 0,
                "automatic_percentage": 0,
                "manual_percentage": 0,
                "avg_composite_score": 0,
                "score_distribution": {}
            }
        
        # Basic counts
        total_listings = len(ranked_data)
        automatic_listings = len([item for item in ranked_data 
                                if 'automatic' in str(item.get('transmission', '')).lower()])
        manual_listings = len([item for item in ranked_data 
                             if 'manual' in str(item.get('transmission', '')).lower()])
        
        # Deal delta statistics
        deal_deltas = [item.get('deal_delta_usd', 0) for item in ranked_data 
                      if item.get('deal_delta_usd') is not None]
        
        # Composite score statistics
        composite_scores = [item.get('composite_score', 0) for item in ranked_data 
                          if item.get('composite_score', 0) is not None]
        
        # Calculate statistics
        avg_deal_delta = sum(deal_deltas) / len(deal_deltas) if deal_deltas else 0
        best_deal_delta = max(deal_deltas) if deal_deltas else 0
        worst_deal_delta = min(deal_deltas) if deal_deltas else 0
        avg_composite_score = sum(composite_scores) / len(composite_scores) if composite_scores else 0
        
        # Score distribution
        score_ranges = {
            "Excellent (8000+)": len([s for s in composite_scores if s >= 8000]),
            "Very Good (6000-7999)": len([s for s in composite_scores if 6000 <= s < 8000]),
            "Good (4000-5999)": len([s for s in composite_scores if 4000 <= s < 6000]),
            "Fair (2000-3999)": len([s for s in composite_scores if 2000 <= s < 4000]),
            "Poor (<2000)": len([s for s in composite_scores if s < 2000])
        }
        
        return {
            "avg_deal_delta": avg_deal_delta,
            "best_deal_delta": best_deal_delta,
            "worst_deal_delta": worst_deal_delta,
            "automatic_percentage": automatic_listings / total_listings if total_listings > 0 else 0,
            "manual_percentage": manual_listings / total_listings if total_listings > 0 else 0,
            "avg_composite_score": avg_composite_score,
            "score_distribution": score_ranges,
            "total_listings": total_listings,
            "automatic_listings": automatic_listings,
            "manual_listings": manual_listings
        }

    def _identify_top_deals(self, ranked_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify top deals in various categories"""
        print("🏆 Identifying top deals...")
        
        if not ranked_data:
            return {
                "overall_top_5": [],
                "best_deal": None,
                "best_manual": None,
                "best_automatic": None,
                "best_value": None
            }
        
        # Overall top 5
        overall_top_5 = ranked_data[:5]
        
        # Best deal (highest deal delta) - handle None values
        valid_deals = [item for item in ranked_data if item.get('deal_delta_usd') is not None]
        best_deal = max(valid_deals, key=lambda x: x.get('deal_delta_usd', 0)) if valid_deals else None
        
        # Best manual transmission
        manual_listings = [item for item in ranked_data 
                          if 'manual' in str(item.get('transmission', '')).lower()]
        valid_manual = [item for item in manual_listings if item.get('composite_score') is not None]
        best_manual = max(valid_manual, key=lambda x: x.get('composite_score', 0)) if valid_manual else None
        
        # Best automatic transmission
        automatic_listings = [item for item in ranked_data 
                             if 'automatic' in str(item.get('transmission', '')).lower()]
        valid_automatic = [item for item in automatic_listings if item.get('composite_score') is not None]
        best_automatic = max(valid_automatic, key=lambda x: x.get('composite_score', 0)) if valid_automatic else None
        
        # Best value (highest composite score)
        valid_scores = [item for item in ranked_data if item.get('composite_score') is not None]
        best_value = max(valid_scores, key=lambda x: x.get('composite_score', 0)) if valid_scores else None
        
        return {
            "overall_top_5": overall_top_5,
            "best_deal": best_deal,
            "best_manual": best_manual,
            "best_automatic": best_automatic,
            "best_value": best_value
        }

    def _create_category_rankings(self, ranked_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Create rankings by various categories"""
        print("📋 Creating category rankings...")
        
        if not ranked_data:
            return {}
        
        # Rank by year
        year_rankings = sorted(ranked_data, key=lambda x: self._extract_year_value(x.get('year', '0')), reverse=True)
        
        # Rank by price (lowest first)
        price_rankings = sorted(ranked_data, key=lambda x: self._extract_price_value(x.get('price', '0')))
        
        # Rank by mileage (lowest first)
        mileage_rankings = sorted(ranked_data, key=lambda x: self._extract_mileage_value(x.get('mileage', '0')))
        
        # Rank by deal delta (highest undervaluation first)
        valid_deal_deltas = [x for x in ranked_data if x.get('deal_delta_usd') is not None]
        deal_delta_rankings = sorted(valid_deal_deltas, key=lambda x: x.get('deal_delta_usd', 0), reverse=True) if valid_deal_deltas else []
        
        return {
            "by_year": year_rankings,
            "by_price": price_rankings,
            "by_mileage": mileage_rankings,
            "by_deal_delta": deal_delta_rankings
        }

    def _extract_price_value(self, price_str: str) -> float:
        """Extract numeric price value from price string"""
        try:
            return float(str(price_str).replace('$', '').replace(',', ''))
        except (ValueError, TypeError):
            return 0.0

    def _extract_year_value(self, year_str: str) -> int:
        """Extract numeric year value from year string"""
        try:
            year_clean = str(year_str).strip()
            if year_clean.isdigit():
                return int(year_clean)
            return 0
        except (ValueError, TypeError):
            return 0

    def _extract_mileage_value(self, mileage_str: str) -> int:
        """Extract numeric mileage value from mileage string"""
        try:
            return int(str(mileage_str).replace(',', ''))
        except (ValueError, TypeError):
            return 0

    def _save_ranking_results(self, ranked_data: List[Dict[str, Any]], 
                             ranking_stats: Dict[str, Any], 
                             top_deals: Dict[str, Any],
                             category_rankings: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Save ranking results to CSV files"""
        print("💾 Saving ranking results...")
        
        files_created = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Create results directory
            results_dir = Path("x987-data/results")
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # 1. Main ranked data CSV
            main_file = results_dir / f"ranking_main_{timestamp}.csv"
            self._save_csv(ranked_data, main_file)
            files_created.append(str(main_file))
            print(f"📄 Saved main ranking data: {main_file}")
            
            # 2. Top deals CSV
            top_deals_file = results_dir / f"ranking_top_deals_{timestamp}.csv"
            top_deals_data = []
            for category, item in top_deals.items():
                if item and isinstance(item, dict):
                    top_deals_data.append({
                        'category': category,
                        'source_url': item.get('source_url', ''),
                        'year': item.get('year', ''),
                        'model': item.get('model', ''),
                        'price': item.get('price', ''),
                        'deal_delta_usd': item.get('deal_delta_usd', ''),
                        'composite_score': item.get('composite_score', ''),
                        'rank': item.get('rank', '')
                    })
                elif item and isinstance(item, list) and len(item) > 0:
                    # Handle case where item is a list (e.g., overall_top_5)
                    for i, list_item in enumerate(item):
                        if isinstance(list_item, dict):
                            top_deals_data.append({
                                'category': f"{category}_{i+1}",
                                'source_url': list_item.get('source_url', ''),
                                'year': list_item.get('year', ''),
                                'model': list_item.get('model', ''),
                                'price': list_item.get('price', ''),
                                'deal_delta_usd': list_item.get('deal_delta_usd', ''),
                                'composite_score': list_item.get('composite_score', ''),
                                'rank': list_item.get('rank', '')
                            })
            
            if top_deals_data:
                self._save_csv(top_deals_data, top_deals_file)
                files_created.append(str(top_deals_file))
                print(f"📄 Saved top deals: {top_deals_file}")
            else:
                print("⚠️  No top deals data to save")
            
            # 3. Category rankings CSVs
            for category_name, category_data in category_rankings.items():
                if category_data and isinstance(category_data, list) and len(category_data) > 0:
                    category_file = results_dir / f"ranking_{category_name}_{timestamp}.csv"
                    self._save_csv(category_data, category_file)
                    files_created.append(str(category_file))
                    print(f"📄 Saved {category_name} rankings: {category_file}")
            
            # 4. Ranking statistics CSV
            stats_file = results_dir / f"ranking_statistics_{timestamp}.csv"
            stats_data = [{'metric': k, 'value': v} for k, v in ranking_stats.items() 
                         if not isinstance(v, dict)]
            self._save_csv(stats_data, stats_file)
            files_created.append(str(stats_file))
            print(f"📄 Saved ranking statistics: {stats_file}")
            
            # 5. Score distribution CSV
            if ranking_stats.get('score_distribution'):
                dist_file = results_dir / f"ranking_score_distribution_{timestamp}.csv"
                dist_data = [{'score_range': k, 'count': v} 
                            for k, v in ranking_stats['score_distribution'].items()]
                self._save_csv(dist_data, dist_file)
                files_created.append(str(dist_file))
                print(f"📄 Saved score distribution: {dist_file}")
            
        except Exception as e:
            print(f"⚠️  Warning: Error saving some ranking files: {e}")
        
        return files_created

    def _save_csv(self, data: List[Dict[str, Any]], file_path: Path) -> None:
        """Save data to CSV file"""
        import csv
        
        if not data:
            return
        
        # Ensure all items are dictionaries
        clean_data = []
        for item in data:
            if isinstance(item, dict):
                clean_data.append(item)
            else:
                print(f"⚠️  Skipping non-dict item: {type(item)} - {item}")
        
        if not clean_data:
            print(f"⚠️  No valid data to save to {file_path}")
            return
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = clean_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(clean_data)

    def _generate_ranking_summary(self, ranked_data: List[Dict[str, Any]], 
                                 ranking_stats: Dict[str, Any],
                                 top_deals: Dict[str, Any],
                                 files_created: List[str]) -> Dict[str, Any]:
        """Generate comprehensive ranking summary"""
        print("📊 Generating ranking summary...")
        
        return {
            "total_listings": len(ranked_data),
            "ranked_data": ranked_data,
            "top_deals": top_deals,
            "ranking_stats": ranking_stats,
            "files_created": files_created,
            "ranking_timestamp": datetime.now().isoformat(),
            "summary": {
                "best_ranked_listing": ranked_data[0] if ranked_data else None,
                "total_files_created": len(files_created),
                "ranking_completion_time": datetime.now().isoformat()
            }
        }


# Export the step instance
RANKING_STEP = RankingStep()
