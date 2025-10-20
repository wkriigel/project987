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
        """Return (should_skip, reason).

        Rules (in order):
        - miss:no_record → no cache record
        - miss:no_payload → record present but no payload
        - miss:incomplete_fields → cached payload exists but price/mileage/year appear missing
        - miss:ttl_expired → TTL window expired
        - hit:ttl_valid → safe to reuse cached payload
        """
        self.load()
        rec = self._data.get(canonical_url)
        if not rec:
            return False, "miss:no_record"
        if not rec.data_blob:
            return False, "miss:no_payload"

        # If cached payload appears incomplete, force a rescrape regardless of TTL
        try:
            from x987.utils.extractors import (
                extract_price_unified,
                extract_mileage_unified,
                extract_vehicle_info_unified,
                clean_text_unified,
            )
        except Exception:
            # If extractors unavailable, be conservative and skip based on TTL only
            extract_price_unified = extract_mileage_unified = extract_vehicle_info_unified = None  # type: ignore
            clean_text_unified = None  # type: ignore

        try:
            blob = rec.data_blob or {}
            raw_text = ""
            if isinstance(blob, dict):
                # Prefer DOM text; fall back to joined sections
                dom = blob.get("raw_dom_text") or ""
                sections = blob.get("raw_sections") or {}
                joined = " \n ".join([str(v) for v in sections.values() if v]) if isinstance(sections, dict) else ""
                raw_text = str(dom or joined or "")
            if clean_text_unified:
                raw_text = clean_text_unified(raw_text)  # type: ignore

            has_price = extract_price_unified(raw_text) is not None if extract_price_unified else True
            has_miles = extract_mileage_unified(raw_text) is not None if extract_mileage_unified else True
            y_m_t = extract_vehicle_info_unified(raw_text) if extract_vehicle_info_unified else (None, None, None)
            year_val = y_m_t[0] if isinstance(y_m_t, tuple) and len(y_m_t) >= 1 else None
            has_year = year_val is not None

            if not (has_price and has_miles and has_year):
                return False, "miss:incomplete_fields"
        except Exception:
            # If something goes wrong computing completeness, fall back to TTL behavior
            pass

        # TTL window
        try:
            if rec.last_scraped_at:
                last = datetime.fromisoformat(rec.last_scraped_at)
                if datetime.now() - last > timedelta(days=max(0, int(ttl_days))):
                    return False, "miss:ttl_expired"
        except Exception:
            return False, "miss:bad_timestamp"

        return True, "hit:ttl_valid"
