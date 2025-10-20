"""
URL↔VIN index utilities

Stores a lightweight mapping from canonical listing URL → VIN so the scraping
step can skip opening VDP pages when VINAnalytics enrichment exists.

Location: x987-data/metadata/url_vin_index.json
Shape: { "<canonical_url>": "VIN", ... }
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


def _index_path() -> Path:
    p = Path('x987-data/metadata/url_vin_index.json')
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load_index() -> Dict[str, str]:
    try:
        p = _index_path()
        if p.exists():
            return json.loads(p.read_text(encoding='utf-8')) or {}
    except Exception:
        pass
    return {}


def save_index(idx: Dict[str, str]) -> None:
    try:
        p = _index_path()
        p.write_text(json.dumps(idx, indent=2), encoding='utf-8')
    except Exception:
        pass


def upsert_url_vin(canonical_url: str, vin: str) -> None:
    if not canonical_url or not vin:
        return
    try:
        idx = load_index()
        if idx.get(canonical_url) == vin:
            return
        idx[canonical_url] = vin
        save_index(idx)
    except Exception:
        pass

