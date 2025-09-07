"""
Ranking Step - Ranks vehicle listings by Options MSRP total (MSRP-only)

PROVIDES: Vehicle listing ranking by Options MSRP total
DEPENDS: x987.pipeline.steps.deduplication:DeduplicationStep
CONSUMED BY: x987.pipeline.steps.view:ViewStep and end users
CONTRACT: Provides ranked vehicle listings sorted by total_options_msrp
TECH CHOICE: Deterministic sort by numeric field
RISK: Low - straightforward ordering and CSV output
"""

from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from .base import BasePipelineStep, StepResult


class RankingStep(BasePipelineStep):
    """Ranking step for MSRP-only mode"""

    def get_step_name(self) -> str:
        return "ranking"

    def get_description(self) -> str:
        return "Ranks vehicle listings by Options MSRP total (descending)"

    def get_dependencies(self) -> List[str]:
        return ["deduplication"]

    def get_required_config(self) -> List[str]:
        return []

    def run_step(self, config: Dict[str, Any], previous_results: Dict[str, StepResult], **kwargs) -> Any:
        """Execute the ranking step."""
        verbose = bool(kwargs.get('verbose'))
        import builtins
        _orig_print = builtins.print
        if not verbose:
            builtins.print = lambda *a, **k: None
        try:
            print("🏆 Starting ranking process...")
            print(f"📁 Working directory: {Path.cwd()}")
            print(f"⏰ Ranking started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # Require deduplication results
            dedupe_result = previous_results.get("deduplication")
            if not dedupe_result or not dedupe_result.is_success:
                print("❌ Deduplication step must complete successfully before ranking")
                raise ValueError("Deduplication step must complete successfully before ranking")

            data = list(dedupe_result.data.get("deduped_data", []))
            if not data:
                print("⚠️  No data to rank")
                return {
                    "total_listings": 0,
                    "ranked_data": [],
                    "files_created": [],
                    "ranking_timestamp": datetime.now().isoformat()
                }

            # Helper: parse integer values robustly
            def to_int(v):
                try:
                    s = str(v).replace(',', '').replace('$', '').strip()
                    return int(s)
                except Exception:
                    return 0

            # Sort by total_options_msrp descending
            data.sort(key=lambda x: to_int(x.get('total_options_msrp', 0)), reverse=True)

            # Add rank and normalize key fields
            ranked: List[Dict[str, Any]] = []
            for i, item in enumerate(data):
                row = dict(item)
                row['rank'] = i + 1
                if 'asking_price_usd' not in row:
                    row['asking_price_usd'] = row.get('price', '')
                ranked.append(row)

            # Output directory from config
            output_dir = Path(config.get('pipeline', {}).get('output_directory', 'x987-data/results'))
            output_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            out_file = output_dir / f"ranking_main_{ts}.csv"
            self._save_csv(ranked, out_file)
            print(f"📄 Saved MSRP-only ranking: {out_file}")

            return {
                "total_listings": len(ranked),
                "ranked_data": ranked,
                "files_created": [str(out_file)],
                "ranking_timestamp": datetime.now().isoformat()
            }
        finally:
            builtins.print = _orig_print

    def _save_csv(self, data: List[Dict[str, Any]], file_path: Path) -> None:
        import csv
        if not data:
            return
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)


# Export the step instance
RANKING_STEP = RankingStep()

