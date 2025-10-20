from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .core import get_connection, ensure_db
from ..pipeline.seen_registry import canonicalize_url
from .api import (
    upsert_listing_by_key,
    get_listing_id_by_key,
    seen_mark_seen,
    insert_scrape,
    upsert_parsed,
    upsert_enrichment,
    save_ranking_batch,
    replace_listing_options,
)


def is_sqlite_enabled(config: Dict[str, Any]) -> bool:
    storage = (config.get("storage") or {}) if isinstance(config, dict) else {}
    return str(storage.get("mode", "sqlite")).lower() == "sqlite"


def record_collection(processed_urls: List[Dict[str, Any]], config: Dict[str, Any]) -> None:
    """Upsert listings and seen entries for collected URLs when SQLite is enabled."""
    if not is_sqlite_enabled(config) or not processed_urls:
        return
    ensure_db(config)
    conn = get_connection(config)
    try:
        for row in processed_urls:
            listing_url = row.get("listing_url") or ""
            listing_key = row.get("canonical_url") or (canonicalize_url(listing_url) if listing_url else "")
            source_url = row.get("source_url") or None
            vin = (row.get("vin") or None)
            location = (row.get("location") or None)
            lid = upsert_listing_by_key(conn, listing_key, listing_url=listing_url, source_url=source_url, vin=vin, location=location)
            # Mirror seen flags
            first_seen = row.get("first_seen_at")
            if first_seen:
                seen_mark_seen(conn, listing_key, now_iso=row.get("collection_timestamp") or first_seen)
    finally:
        conn.close()


def record_scraping(processed_data: List[Dict[str, Any]], config: Dict[str, Any]) -> None:
    """Persist scrapes to DB when SQLite is enabled."""
    if not is_sqlite_enabled(config) or not processed_data:
        return
    ensure_db(config)
    conn = get_connection(config)
    try:
        for d in processed_data:
            listing_key = d.get("canonical_url") or (canonicalize_url(d.get("listing_url")) if d.get("listing_url") else "")
            if not listing_key:
                continue
            lid = get_listing_id_by_key(conn, listing_key)
            if not lid:
                lid = upsert_listing_by_key(
                    conn,
                    listing_key,
                    listing_url=d.get("listing_url"),
                    source_url=d.get("source_url"),
                )
            insert_scrape(
                conn,
                lid,
                scraped_at=d.get("scraping_timestamp"),
                method=d.get("scraping_method"),
                status=d.get("scraping_status"),
                raw_text=d.get("raw_text"),
                raw_html=d.get("raw_html"),
                data={"extracted_data": d.get("extracted_data", {}), "title": d.get("title")},
            )
            # Retention enforcement
            try:
                storage = (config.get('storage') or {}) if isinstance(config, dict) else {}
                retention = (storage.get('retention') or {}) if isinstance(storage, dict) else {}
                max_per = retention.get('scrapes_max_per_listing')
                keep_failed = bool(retention.get('keep_failed', True))
                if isinstance(max_per, int) and max_per >= 0:
                    # Fetch scrapes ordered by scraped_at desc; stale rows beyond limit are removed
                    rows = conn.execute(
                        "SELECT id, status, scraped_at FROM scrapes WHERE listing_id = ? ORDER BY datetime(COALESCE(scraped_at, '')) DESC, id DESC",
                        (lid,),
                    ).fetchall()
                    to_delete = []
                    kept_success = 0
                    for r in rows:
                        st = (r[1] or '').lower()
                        is_failed = (st == 'failed')
                        if is_failed and keep_failed:
                            continue
                        if kept_success < max_per:
                            kept_success += 1
                        else:
                            to_delete.append(int(r[0]))
                    if to_delete:
                        qmarks = ','.join('?' for _ in to_delete)
                        conn.execute(f"DELETE FROM scrapes WHERE id IN ({qmarks})", to_delete)
            except Exception:
                pass
    finally:
        conn.close()


def record_transformation(scraping_data: List[Dict[str, Any]], merged_data: List[Dict[str, Any]], config: Dict[str, Any], *, options_data: Optional[List[Dict[str, Any]]] = None) -> None:
    """Upsert parsed fields using alignment with scraping_data (for listing_key)."""
    if not is_sqlite_enabled(config) or not merged_data or not scraping_data:
        return
    ensure_db(config)
    conn = get_connection(config)
    try:
        # We assume merged_data aligns to scraping_data order from earlier steps
        for i, parsed in enumerate(merged_data):
            src = scraping_data[i] if i < len(scraping_data) else {}
            listing_key = src.get("canonical_url") or (canonicalize_url(src.get("listing_url")) if src.get("listing_url") else "")
            if not listing_key:
                continue
            lid = get_listing_id_by_key(conn, listing_key)
            if not lid:
                lid = upsert_listing_by_key(conn, listing_key, listing_url=src.get("listing_url"), source_url=src.get("source_url"))

            # Map parsed fields
            mapped = {
                "year": _to_int(parsed.get("year")),
                "model": parsed.get("model"),
                "trim": parsed.get("trim"),
                "transmission_norm": parsed.get("transmission_norm"),
                "mileage": _to_int(parsed.get("mileage")),
                "asking_price_usd": _to_int(parsed.get("asking_price_usd") or parsed.get("price")),
                "exterior": parsed.get("exterior"),
                "interior": parsed.get("interior"),
                "color_ext_bucket": parsed.get("color_ext_bucket"),
                "color_int_bucket": parsed.get("color_int_bucket"),
                "raw_options": parsed.get("options_list"),
                "options_list": _split_list(parsed.get("options_list")),
                # No options_detected/options_by_category here; available in options_data if needed later
                "vin": parsed.get("vin"),
                "location": parsed.get("location"),
            }
            upsert_parsed(conn, lid, mapped)

            # Enrichment: total_options_msrp and detected options breakdown if available
            try:
                opt = (options_data[i] if options_data and i < len(options_data) else {}) or {}
                total_msrp = opt.get("total_options_msrp")
                if total_msrp is None:
                    # fallback from merged row
                    total_msrp = parsed.get("total_options_msrp")
                msrp_breakdown = {
                    "options_by_category": opt.get("options_by_category", {}),
                    "detected_options": opt.get("detected_options", []),
                }
                upsert_enrichment(
                    conn,
                    lid,
                    {
                        "total_options_msrp": total_msrp,
                        "msrp_breakdown": msrp_breakdown,
                        "derived": {},
                    },
                )
                # Normalize detected options into listing_options table (idempotent replace)
                try:
                    replace_listing_options(conn, lid, opt.get('detected_options', []))
                except Exception:
                    pass
            except Exception:
                pass
    finally:
        conn.close()


def record_ranking(ranked_data: List[Dict[str, Any]], run_timestamp: str, config: Dict[str, Any]) -> None:
    if not is_sqlite_enabled(config) or not ranked_data:
        return
    ensure_db(config)
    conn = get_connection(config)
    try:
        rows = []
        for row in ranked_data:
            # Try to resolve listing_key; fallback by URL if present in row
            listing_key = row.get("canonical_url") or (canonicalize_url(row.get("listing_url")) if row.get("listing_url") else "")
            lid = None
            if listing_key:
                lid = get_listing_id_by_key(conn, listing_key)
            if not lid:
                # If we can't resolve listing, skip ranking entry
                continue
            rows.append({
                "listing_id": lid,
                "rank": int(row.get("rank") or 0),
                "total_options_msrp": _to_int(row.get("total_options_msrp")),
            })
        if rows:
            save_ranking_batch(conn, run_timestamp, rows)
    finally:
        conn.close()


def _to_int(v: Any) -> Optional[int]:
    if v is None:
        return None
    try:
        s = str(v).replace(",", "").replace("$", "").strip()
        return int(s)
    except Exception:
        return None


def _split_list(v: Any) -> Optional[list]:
    if v is None:
        return None
    if isinstance(v, list):
        return v
    try:
        # Assume comma-separated string
        return [s.strip() for s in str(v).split(",") if s.strip()]
    except Exception:
        return None
