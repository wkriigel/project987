"""
Listing Cache (JSON-backed)

Purpose: Avoid full VDP scrapes when a listing hasn't changed materially.

Keyed by canonical URL. Stores last scraped payload and cheap invariants (price,
mileage). Conservative: only skip if we have a prior payload and price matches
within TTL.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


@dataclass
class CacheRecord:
    last_scraped_at: Optional[str]
    data_blob: Optional[Dict[str, Any]]


class ListingCache:
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self._data: Dict[str, CacheRecord] = {}
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        try:
            if self.file_path.exists():
                raw = json.loads(self.file_path.read_text(encoding="utf-8"))
                for key, val in raw.items():
                    if isinstance(val, dict):
                        self._data[key] = CacheRecord(
                            last_scraped_at=val.get("last_scraped_at"),
                            data_blob=val.get("data_blob"),
                        )
            self._loaded = True
        except Exception:
            self._data = {}
            self._loaded = True

    def save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        serializable = {
            k: {
                "last_scraped_at": v.last_scraped_at,
                "data_blob": v.data_blob,
            }
            for k, v in self._data.items()
        }
        self.file_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    def get(self, canonical_url: str) -> Optional[CacheRecord]:
        self.load()
        return self._data.get(canonical_url)

    def save_result(
        self,
        canonical_url: str,
        data_blob: Dict[str, Any],
        now_iso: Optional[str] = None,
    ) -> None:
        self.load()
        now = now_iso or datetime.now().isoformat()
        self._data[canonical_url] = CacheRecord(
            last_scraped_at=now,
            data_blob=data_blob,
        )

    def should_skip(
        self,
        canonical_url: str,
        ttl_days: int = 3,
    ) -> Tuple[bool, str]:
        """Return (should_skip, reason). Conservative: require data_blob and TTL valid."""
        self.load()
        rec = self._data.get(canonical_url)
        if not rec:
            return False, "miss:no_record"
        if not rec.data_blob:
            return False, "miss:no_payload"
        # TTL window
        try:
            if rec.last_scraped_at:
                last = datetime.fromisoformat(rec.last_scraped_at)
                if datetime.now() - last > timedelta(days=max(0, int(ttl_days))):
                    return False, "miss:ttl_expired"
        except Exception:
            return False, "miss:bad_timestamp"

        return True, "hit:ttl_valid"
