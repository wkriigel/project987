"""
Migration script: move JSON/CSV storage into SQLite.

Usage:
  python -m x987.scripts.migrate_to_db

Idempotent imports from:
  - x987-data/seen_registry.json
  - x987-data/listing_cache.json
  - x987-data/results/collection_detailed_*.csv
  - x987-data/results/scraping_detailed_*.csv
  - x987-data/results/ranking_main_*.csv (best-effort)
  - x987-data/metadata/vin_enriched.json
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from x987.config import get_config, get_data_dir
from x987.pipeline.seen_registry import canonicalize_url
from x987.db import ensure_db, get_connection
from x987.db.api import (
    upsert_listing_by_key,
    seen_mark_seen,
    cache_save,
    insert_scrape,
    get_listing_id_by_key,
    save_ranking_batch,
)


def import_seen_registry(conn, data_dir: Path) -> None:
    fp = data_dir / "seen_registry.json"
    if not fp.exists():
        print("- seen_registry.json not found; skipping")
        return
    raw = json.loads(fp.read_text(encoding="utf-8"))
    count = 0
    for key, rec in raw.items():
        if not isinstance(rec, dict):
            continue
        upsert_listing_by_key(conn, key, listing_url=key)
        seen_mark_seen(conn, key, now_iso=rec.get("last_seen_at"))
        count += 1
    print(f"✓ Imported seen registry: {count} entries")


def import_listing_cache(conn, data_dir: Path) -> None:
    fp = data_dir / "listing_cache.json"
    if not fp.exists():
        print("- listing_cache.json not found; skipping")
        return
    raw = json.loads(fp.read_text(encoding="utf-8"))
    count = 0
    for key, rec in raw.items():
        if not isinstance(rec, dict):
            continue
        payload = rec.get("data_blob") or {}
        ts = rec.get("last_scraped_at")
        upsert_listing_by_key(conn, key, listing_url=key)
        cache_save(conn, key, payload, now_iso=ts)
        count += 1
    print(f"✓ Imported listing cache: {count} entries")


def import_collection_csvs(conn, results_dir: Path) -> None:
    files = sorted(results_dir.glob("collection_detailed_*.csv"))
    if not files:
        print("- No collection_detailed_*.csv; skipping")
        return
    total = 0
    for fp in files:
        with fp.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("listing_url") or ""
                if not url:
                    continue
                key = row.get("canonical_url") or canonicalize_url(url)
                upsert_listing_by_key(
                    conn,
                    key,
                    listing_url=url,
                    source_url=row.get("source_url"),
                )
                # seen
                seen_mark_seen(conn, key, now_iso=row.get("collection_timestamp"))
                total += 1
    print(f"✓ Imported collection CSVs: {total} rows")


def import_scraping_csvs(conn, results_dir: Path) -> None:
    files = sorted(results_dir.glob("scraping_detailed_*.csv"))
    if not files:
        print("- No scraping_detailed_*.csv; skipping")
        return
    total = 0
    for fp in files:
        with fp.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("listing_url") or ""
                key = row.get("canonical_url") or (canonicalize_url(url) if url else None)
                if not key:
                    continue
                lid = get_listing_id_by_key(conn, key)
                if not lid:
                    lid = upsert_listing_by_key(conn, key, listing_url=url, source_url=row.get("source_url"))
                # extracted_data may be serialized; attempt JSON else wrap
                ed = row.get("extracted_data")
                try:
                    if isinstance(ed, str) and ed.strip().startswith("{"):
                        ed_obj = json.loads(ed)
                    elif isinstance(ed, str):
                        ed_obj = {"raw": ed}
                    else:
                        ed_obj = ed or {}
                except Exception:
                    ed_obj = {"raw": ed}
                insert_scrape(
                    conn,
                    lid,
                    scraped_at=row.get("scraping_timestamp"),
                    method=row.get("scraping_method"),
                    status=row.get("scraping_status"),
                    raw_text=None,
                    raw_html=None,
                    data={"extracted_data": ed_obj},
                )
                total += 1
    print(f"✓ Imported scraping CSVs: {total} rows")


def import_ranking_csvs(conn, results_dir: Path) -> None:
    files = sorted(results_dir.glob("ranking_main_*.csv"))
    if not files:
        print("- No ranking_main_*.csv; skipping")
        return
    for fp in files:
        ts = fp.stem.replace("ranking_main_", "")
        rows = []
        with fp.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("listing_url") or None
                key = canonicalize_url(url) if url else None
                if not key:
                    continue
                lid = get_listing_id_by_key(conn, key)
                if not lid:
                    lid = upsert_listing_by_key(conn, key, listing_url=url)
                rows.append({
                    "listing_id": lid,
                    "rank": int(row.get("rank") or 0),
                    "total_options_msrp": _to_int(row.get("total_options_msrp")),
                })
        if rows:
            save_ranking_batch(conn, ts, rows)
            print(f"✓ Imported rankings from {fp.name}: {len(rows)} rows")


def import_vin_enriched(conn, data_dir: Path) -> None:
    fp = data_dir / "metadata" / "vin_enriched.json"
    if not fp.exists():
        print("- metadata/vin_enriched.json not found; skipping")
        return
    raw = json.loads(fp.read_text(encoding="utf-8"))
    entries = raw.get("entries", {}) if isinstance(raw, dict) else raw
    if not isinstance(entries, dict):
        print("- Unexpected vin_enriched.json format; skipping")
        return
    count = 0
    with conn:
        for vin, payload in entries.items():
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO vin_enriched (vin, source, updated_at, link, raw, parsed_json, derived_json) VALUES (?,?,?,?,?,?,?)",
                    (
                        vin,
                        (payload.get("source") if isinstance(payload, dict) else None),
                        (payload.get("updatedAt") if isinstance(payload, dict) else None),
                        (payload.get("link") if isinstance(payload, dict) else None),
                        (payload.get("raw") if isinstance(payload, dict) else None),
                        json.dumps(payload.get("parsed") if isinstance(payload, dict) else {}),
                        json.dumps(payload.get("derived") if isinstance(payload, dict) else {}),
                    ),
                )
                count += 1
            except Exception:
                continue
    print(f"✓ Imported VIN enrichment store: {count} entries")


def _to_int(v: Any):
    try:
        s = str(v).replace(",", "").replace("$", "").strip()
        return int(s)
    except Exception:
        return None


def main():
    cfg = get_config()
    ensure_db(cfg)
    conn = get_connection(cfg)
    try:
        data_dir = get_data_dir()
        results_dir = data_dir / "results"
        print(f"Using data dir: {data_dir}")
        print(f"Using results dir: {results_dir}")

        import_seen_registry(conn, data_dir)
        import_listing_cache(conn, data_dir)
        import_collection_csvs(conn, results_dir)
        import_scraping_csvs(conn, results_dir)
        import_ranking_csvs(conn, results_dir)
        import_vin_enriched(conn, data_dir)

        print("\nMigration complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

