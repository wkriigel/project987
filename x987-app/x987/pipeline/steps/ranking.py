"""
Ranking Step - Ranks vehicle listings by Options MSRP total (MSRP-only)

PROVIDES: Vehicle listing ranking by Options MSRP total
DEPENDS: x987.pipeline.steps.deduplication:DeduplicationStep
CONSUMED BY: x987.pipeline.steps.view:ViewStep and end users
CONTRACT: Provides ranked vehicle listings sorted by total_options_msrp
TECH CHOICE: Simple MSRP-based ordering
RISK: Low - deterministic sort by numeric field
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
        return "Ranks vehicle listings by Options MSRP total (descending)"
    
    def get_dependencies(self) -> List[str]:
        # MSRP-only cleanup: depend solely on deduplication
        return ["deduplication"]
    
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

            from ...config import get_config
            cfg = get_config()
            # MSRP-only flow: use deduplicated data and sort by total_options_msrp (desc)
                # Use deduplicated data and sort by total_options_msrp (desc)
                if "deduplication" not in previous_results:
                    print("❌ Deduplication step must complete successfully before ranking in MSRP-only mode")
                    raise ValueError("Deduplication step must complete successfully before ranking")
                dedupe_result = previous_results["deduplication"]
                if not dedupe_result.is_success:
                    print("❌ Deduplication step failed; cannot rank")
                    raise ValueError("Deduplication step must succeed before ranking")
                data = list(dedupe_result.data.get("deduped_data", []))
                if not data:
                    print("⚠️  No data to rank")
                    return {
                        "total_listings": 0,
                        "ranked_data": [],
                        "files_created": [],
                        "ranking_timestamp": datetime.now().isoformat()
                    }
                # Numeric helper
                def to_int(v):
                    try:
                        s = str(v).replace(',', '').replace('$', '').strip()
                        return int(s)
                    except Exception:
                        return 0
                # Sort by MSRP descending
                data.sort(key=lambda x: to_int(x.get('total_options_msrp', 0)), reverse=True)
                # Add rank index
                normalized: List[Dict[str, Any]] = []
                for i, item in enumerate(data):
                    row = dict(item)
                    row['rank'] = i + 1
                    # Normalize price column name expected by FE/API
                    if 'asking_price_usd' not in row:
                        row['asking_price_usd'] = row.get('price', '')
                    normalized.append(row)
                # Save a single main ranking CSV
                out_dir = Path(cfg.get('pipeline.output_directory', 'x987-data/results'))
                out_dir.mkdir(parents=True, exist_ok=True)
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                out_file = out_dir / f"ranking_main_{ts}.csv"
                self._save_csv(normalized, out_file)
                print(f"📄 Saved MSRP-only ranking: {out_file}")
                return {
                    "total_listings": len(normalized),
                    "ranked_data": normalized,
                    "files_created": [str(out_file)],
                    "ranking_timestamp": datetime.now().isoformat()
                }
        finally:
            builtins.print = _orig_print

    # Legacy multi-output methods removed; MSRP-only saves a single ranking_main CSV.
        
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
