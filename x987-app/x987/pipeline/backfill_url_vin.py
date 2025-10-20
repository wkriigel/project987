"""
Backfill URL→VIN index from existing CSV outputs.

Scans x987-data/results (or a provided directory) for recent CSVs
(ranking_main_*.csv and transformed_data_*.csv) and records mappings of
canonical_url → VIN into x987-data/metadata/url_vin_index.json.

Usage:
  python -m x987.pipeline.backfill_url_vin
  python -m x987.pipeline.backfill_url_vin --results x987-data/results --limit 10
"""

from __future__ import annotations

import csv
import argparse
from pathlib import Path
from typing import Iterable, Tuple

from .url_vin_index import upsert_url_vin
from .seen_registry import canonicalize_url


def _iter_csv_files(results_dir: Path, patterns: Iterable[str]) -> Iterable[Path]:
    files = []
    for pat in patterns:
        files.extend(results_dir.glob(pat))
    # Sort newest first
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def _row_url_vin(row: dict) -> Tuple[str, str]:
    vin = str(row.get('vin') or '').strip().upper()
    canon = str(row.get('canonical_url') or '').strip()
    if not canon:
        lu = str(row.get('listing_url') or '').strip()
        if lu:
            canon = canonicalize_url(lu)
    return canon, vin


def backfill(results_dir: Path, limit: int = 20) -> Tuple[int, int]:
    """Backfill URL→VIN index from recent CSVs.

    Returns (files_read, mappings_added).
    """
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    patterns = [
        'ranking_main_*.csv',
        'transformed_data_*.csv'
    ]
    files = list(_iter_csv_files(results_dir, patterns))
    if limit and limit > 0:
        files = files[:limit]
    added = 0
    for fp in files:
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    canon, vin = _row_url_vin(row)
                    if not canon or not vin:
                        continue
                    upsert_url_vin(canon, vin)
                    added += 1
        except Exception:
            continue
    return len(files), added


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description='Backfill URL→VIN index from existing CSV outputs')
    ap.add_argument('--results', default='x987-data/results', help='Results directory (default: x987-data/results)')
    ap.add_argument('--limit', type=int, default=20, help='Max number of files to scan (newest first)')
    args = ap.parse_args(argv)
    files_read, added = backfill(Path(args.results), limit=args.limit)
    print(f'[backfill] Files read: {files_read} • Mappings added: {added}')


if __name__ == '__main__':
    main()

