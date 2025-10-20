from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional, Iterable, Tuple

from .core import get_connection


def _now_iso() -> str:
    return datetime.now().isoformat()


def upsert_listing_by_key(conn: sqlite3.Connection, listing_key: str, *, listing_url: Optional[str] = None, source_url: Optional[str] = None, vin: Optional[str] = None, location: Optional[str] = None) -> int:
    """Insert or update a listing row identified by listing_key. Returns listing_id."""
    now = _now_iso()
    with conn:
        cur = conn.execute(
            "SELECT id FROM listings WHERE listing_key = ?",
            (listing_key,),
        )
        row = cur.fetchone()
        if row:
            conn.execute(
                "UPDATE listings SET listing_url = COALESCE(?, listing_url), source_url = COALESCE(?, source_url), vin = COALESCE(?, vin), location = COALESCE(?, location), updated_at = ? WHERE listing_key = ?",
                (listing_url, source_url, vin, location, now, listing_key),
            )
            return int(row[0])
        cur2 = conn.execute(
            "INSERT INTO listings (listing_key, listing_url, source_url, vin, location, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
            (listing_key, listing_url, source_url, vin, location, now, now),
        )
        return int(cur2.lastrowid)


def get_listing_id_by_key(conn: sqlite3.Connection, listing_key: str) -> Optional[int]:
    cur = conn.execute("SELECT id FROM listings WHERE listing_key = ?", (listing_key,))
    row = cur.fetchone()
    return int(row[0]) if row else None


# Seen registry
def seen_is_seen(conn: sqlite3.Connection, listing_key: str) -> bool:
    cur = conn.execute("SELECT 1 FROM seen_registry WHERE listing_key = ?", (listing_key,))
    return cur.fetchone() is not None


def seen_get_first_seen(conn: sqlite3.Connection, listing_key: str) -> Optional[str]:
    cur = conn.execute("SELECT first_seen_at FROM seen_registry WHERE listing_key = ?", (listing_key,))
    row = cur.fetchone()
    return str(row[0]) if row else None


def seen_mark_seen(conn: sqlite3.Connection, listing_key: str, now_iso: Optional[str] = None) -> Tuple[str, str]:
    now = now_iso or _now_iso()
    with conn:
        cur = conn.execute("SELECT first_seen_at FROM seen_registry WHERE listing_key = ?", (listing_key,))
        row = cur.fetchone()
        if row:
            first = str(row[0])
            conn.execute("UPDATE seen_registry SET last_seen_at = ? WHERE listing_key = ?", (now, listing_key))
            return first, now
        conn.execute(
            "INSERT INTO seen_registry (listing_key, first_seen_at, last_seen_at) VALUES (?,?,?)",
            (listing_key, now, now),
        )
        return now, now


# Listing cache
def cache_get(conn: sqlite3.Connection, listing_key: str) -> Optional[Dict[str, Any]]:
    cur = conn.execute("SELECT last_scraped_at, data_blob FROM listing_cache WHERE listing_key = ?", (listing_key,))
    row = cur.fetchone()
    if not row:
        return None
    try:
        data = json.loads(row[1]) if row[1] else None
    except Exception:
        data = None
    return {"last_scraped_at": row[0], "data_blob": data}


def cache_save(conn: sqlite3.Connection, listing_key: str, data_blob: Dict[str, Any], now_iso: Optional[str] = None) -> None:
    now = now_iso or _now_iso()
    with conn:
        payload = json.dumps(data_blob)
        conn.execute(
            "INSERT INTO listing_cache (listing_key, last_scraped_at, data_blob) VALUES (?,?,?)\n             ON CONFLICT(listing_key) DO UPDATE SET last_scraped_at=excluded.last_scraped_at, data_blob=excluded.data_blob",
            (listing_key, now, payload),
        )


def insert_scrape(conn: sqlite3.Connection, listing_id: int, *, scraped_at: Optional[str] = None, method: Optional[str] = None, status: Optional[str] = None, raw_text: Optional[str] = None, raw_html: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> int:
    with conn:
        cur = conn.execute(
            "INSERT INTO scrapes (listing_id, scraped_at, method, status, raw_text, raw_html, data_json) VALUES (?,?,?,?,?,?,?)",
            (listing_id, scraped_at or _now_iso(), method, status, raw_text, raw_html, json.dumps(data or {})),
        )
        return int(cur.lastrowid)


def upsert_parsed(conn: sqlite3.Connection, listing_id: int, parsed: Dict[str, Any]) -> None:
    fields = [
        "year", "model", "trim", "transmission_norm", "mileage", "asking_price_usd",
        "exterior", "interior", "color_ext_bucket", "color_int_bucket",
        "raw_options", "options_list", "options_detected", "options_by_category", "top_options", "vin", "location",
    ]
    # Prepare values
    values = {k: parsed.get(k) for k in fields}
    # JSON-encode list/dict fields
    for jk in ("options_list", "options_detected", "options_by_category"):
        if values.get(jk) is not None and not isinstance(values[jk], str):
            try:
                values[jk] = json.dumps(values[jk])
            except Exception:
                values[jk] = None
    now = _now_iso()
    with conn:
        # Try update
        cur = conn.execute("SELECT id FROM parsed_listings WHERE listing_id = ?", (listing_id,))
        row = cur.fetchone()
        if row:
            conn.execute(
                """
                UPDATE parsed_listings SET
                    updated_at=?, year=?, model=?, trim=?, transmission_norm=?, mileage=?, asking_price_usd=?,
                    exterior=?, interior=?, color_ext_bucket=?, color_int_bucket=?, raw_options=?, options_list=?,
                    options_detected=?, options_by_category=?, top_options=?, vin=?, location=?
                WHERE listing_id=?
                """,
                (
                    now,
                    values["year"], values["model"], values["trim"], values["transmission_norm"], values["mileage"], values["asking_price_usd"],
                    values["exterior"], values["interior"], values["color_ext_bucket"], values["color_int_bucket"], values["raw_options"], values["options_list"],
                    values["options_detected"], values["options_by_category"], values["top_options"], values["vin"], values["location"],
                    listing_id,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO parsed_listings (
                    listing_id, updated_at, year, model, trim, transmission_norm, mileage, asking_price_usd,
                    exterior, interior, color_ext_bucket, color_int_bucket, raw_options, options_list,
                    options_detected, options_by_category, top_options, vin, location
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    listing_id, now, values["year"], values["model"], values["trim"], values["transmission_norm"], values["mileage"], values["asking_price_usd"],
                    values["exterior"], values["interior"], values["color_ext_bucket"], values["color_int_bucket"], values["raw_options"], values["options_list"],
                    values["options_detected"], values["options_by_category"], values["top_options"], values["vin"], values["location"],
                ),
            )


def upsert_enrichment(conn: sqlite3.Connection, listing_id: int, enrichment: Dict[str, Any]) -> None:
    total_msrp = enrichment.get("total_options_msrp")
    msrp_breakdown = enrichment.get("msrp_breakdown")
    derived = enrichment.get("derived")
    now = _now_iso()
    with conn:
        cur = conn.execute("SELECT id FROM enrichments WHERE listing_id = ?", (listing_id,))
        row = cur.fetchone()
        payload_breakdown = json.dumps(msrp_breakdown or {})
        payload_derived = json.dumps(derived or {})
        if row:
            conn.execute(
                "UPDATE enrichments SET enriched_at=?, total_options_msrp=?, msrp_breakdown=?, derived_json=? WHERE listing_id=?",
                (now, total_msrp, payload_breakdown, payload_derived, listing_id),
            )
        else:
            conn.execute(
                "INSERT INTO enrichments (listing_id, enriched_at, total_options_msrp, msrp_breakdown, derived_json) VALUES (?,?,?,?,?)",
                (listing_id, now, total_msrp, payload_breakdown, payload_derived),
            )


def upsert_url_vin(conn: sqlite3.Connection, canonical_url: str, vin: str) -> None:
    with conn:
        conn.execute(
            "INSERT INTO url_vin_index (canonical_url, vin, updated_at) VALUES (?,?,?)\n             ON CONFLICT(canonical_url) DO UPDATE SET vin=excluded.vin, updated_at=excluded.updated_at",
            (canonical_url, vin, _now_iso()),
        )


def save_ranking_batch(conn: sqlite3.Connection, run_timestamp: str, rows: Iterable[Dict[str, Any]]) -> None:
    with conn:
        for row in rows:
            listing_id = int(row["listing_id"])
            rank = int(row["rank"])
            total = row.get("total_options_msrp")
            conn.execute(
                "INSERT OR REPLACE INTO rankings (run_timestamp, listing_id, rank, total_options_msrp) VALUES (?,?,?,?)",
                (run_timestamp, listing_id, rank, total),
            )


def replace_listing_options(conn: sqlite3.Connection, listing_id: int, options: Iterable[Dict[str, Any]]) -> None:
    """Replace all options for a listing with given iterable of option dicts.

    Each item may include: id (or option_id), display, category, msrp, value.
    Missing msrp/value are stored as NULL.
    """
    with conn:
        conn.execute("DELETE FROM listing_options WHERE listing_id = ?", (listing_id,))
        for opt in options or []:
            oid = opt.get('id') or opt.get('option_id')
            if not oid:
                continue
            conn.execute(
                "INSERT INTO listing_options (listing_id, option_id, display, category, msrp, value) VALUES (?,?,?,?,?,?)",
                (
                    listing_id,
                    str(oid),
                    opt.get('display'),
                    opt.get('category'),
                    opt.get('msrp'),
                    opt.get('value'),
                ),
            )
