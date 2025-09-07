"""
Seen Registry

Provides a lightweight persistent registry to track whether a listing has been
seen before across pipeline runs. Used to mark items as "new" in CSV outputs.

Design goals:
- Minimal dependencies (JSON file on disk)
- Stable keys using canonicalized URLs (safe default)
- Optional first_seen timestamp storage

This module is intentionally small and reusable across steps.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


TRACKING_QUERY_PREFIXES = (
    "utm_",
    "aff",
    "affiliate",
    "campaign",
    "cmpid",
    "gclid",
    "fbclid",
    "mc_cid",
    "mc_eid",
)


def canonicalize_url(url: str) -> str:
    """Produce a canonical form of a URL for stable identity.

    - Lowercase scheme and host
    - Drop fragment
    - Drop known tracking query params
    - Keep path and non-tracking query params in stable order
    """
    try:
        parts = urlsplit(url)
        scheme = parts.scheme.lower()
        netloc = parts.netloc.lower()
        path = parts.path or "/"

        # Filter query params
        if parts.query:
            pairs = parse_qsl(parts.query, keep_blank_values=True)
            filtered = []
            for k, v in pairs:
                if any(k.startswith(pref) for pref in TRACKING_QUERY_PREFIXES):
                    continue
                filtered.append((k, v))
            # Sort for stability
            query = urlencode(filtered)
        else:
            query = ""

        return urlunsplit((scheme, netloc, path, query, ""))
    except Exception:
        return url


@dataclass
class SeenRecord:
    first_seen_at: str
    last_seen_at: str


class SeenRegistry:
    """JSON-backed registry of seen listing IDs."""

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self._data: Dict[str, SeenRecord] = {}
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        try:
            if self.file_path.exists():
                raw = json.loads(self.file_path.read_text(encoding="utf-8"))
                # Validate shape
                for key, val in raw.items():
                    if isinstance(val, dict) and "first_seen_at" in val and "last_seen_at" in val:
                        self._data[key] = SeenRecord(
                            first_seen_at=val["first_seen_at"],
                            last_seen_at=val["last_seen_at"],
                        )
            self._loaded = True
        except Exception:
            # Corrupt file: start fresh
            self._data = {}
            self._loaded = True

    def save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        serializable = {k: vars(v) for k, v in self._data.items()}
        self.file_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    def is_seen(self, key: str) -> bool:
        self.load()
        return key in self._data

    def get_first_seen(self, key: str) -> Optional[str]:
        self.load()
        rec = self._data.get(key)
        return rec.first_seen_at if rec else None

    def mark_seen(self, key: str, now_iso: Optional[str] = None) -> SeenRecord:
        self.load()
        now = now_iso or datetime.now().isoformat()
        if key in self._data:
            rec = self._data[key]
            rec.last_seen_at = now
            return rec
        rec = SeenRecord(first_seen_at=now, last_seen_at=now)
        self._data[key] = rec
        return rec

