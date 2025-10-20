"""
Archive legacy JSON stores now replaced by SQLite.

Moves the following into x987-data/_archive/<timestamp>/ if they exist:
  - x987-data/seen_registry.json
  - x987-data/listing_cache.json
  - x987-data/metadata/url_vin_index.json

Usage:
  python -m x987.scripts.archive_legacy_storage
"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


def main():
    root = Path.cwd().parent  # running from x987-app
    data_dir = root / 'x987-data'
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_dir = data_dir / '_archive' / ts
    archive_dir.mkdir(parents=True, exist_ok=True)

    candidates = [
        data_dir / 'seen_registry.json',
        data_dir / 'listing_cache.json',
        data_dir / 'metadata' / 'url_vin_index.json',
    ]

    moved = []
    for p in candidates:
        try:
            if p.exists():
                dest = archive_dir / p.name
                shutil.move(str(p), str(dest))
                moved.append(str(dest))
        except Exception as e:
            print(f"⚠️  Failed to archive {p}: {e}")

    if moved:
        print("✓ Archived legacy files:")
        for m in moved:
            print(f"  - {m}")
    else:
        print("No legacy files found to archive.")


if __name__ == '__main__':
    main()

