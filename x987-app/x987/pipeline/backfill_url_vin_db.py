"""
Backfill URL→VIN index from the SQLite DB.

Scans `listings` and `parsed_listings` to upsert url_vin_index for any
listing that has a VIN. This helps enriched-shortcut skipping work earlier
in runs before VINs are seen again.
"""
from __future__ import annotations

from typing import Optional

def backfill(conn) -> int:
    """Upsert url_vin_index for rows with VIN, returns count upserted."""
    try:
        cur = conn.execute(
            """
            SELECT l.listing_key, COALESCE(pl.vin, l.vin) AS vin
            FROM listings l
            LEFT JOIN parsed_listings pl ON pl.listing_id = l.id
            WHERE COALESCE(pl.vin, l.vin) IS NOT NULL AND TRIM(COALESCE(pl.vin, l.vin)) <> ''
            """
        )
        rows = cur.fetchall() or []
        total = 0
        for r in rows:
            url = str(r[0] or '').strip()
            vin = str(r[1] or '').strip().upper()
            if not url or not vin:
                continue
            try:
                conn.execute(
                    "INSERT INTO url_vin_index (canonical_url, vin, updated_at) VALUES (?,?,datetime('now'))\n                     ON CONFLICT(canonical_url) DO UPDATE SET vin=excluded.vin, updated_at=excluded.updated_at",
                    (url, vin),
                )
                total += 1
            except Exception:
                continue
        return total
    except Exception:
        return 0

