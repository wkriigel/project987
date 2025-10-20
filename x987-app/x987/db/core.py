from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, Union

from ..config import get_data_dir


def resolve_db_path(config: Union[Dict[str, Any], Any]) -> Path:
    """Resolve database path from config or fall back to data dir.

    Accepts a dict or ConfigManager-like object.
    """
    # Extract storage config dict
    storage = {}
    if hasattr(config, "get_storage_config"):
        try:
            storage = config.get_storage_config() or {}
        except Exception:
            storage = {}
    elif isinstance(config, dict):
        storage = config.get("storage", {}) if isinstance(config.get("storage", {}), dict) else {}

    db_path_raw = storage.get("db_path") if isinstance(storage, dict) else None
    if not db_path_raw:
        # Default in data dir
        return get_data_dir() / "x987.db"

    p = Path(db_path_raw)
    if p.is_absolute():
        return p

    # If relative, resolve from project root (parent of current cwd expected inside x987-app)
    root = Path.cwd().parent
    return (root / p).resolve()


def get_connection(config: Union[Dict[str, Any], Any]) -> sqlite3.Connection:
    """Open a SQLite connection with sane defaults."""
    db_path = resolve_db_path(config)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def ensure_db(config: Union[Dict[str, Any], Any]) -> Path:
    """Ensure database exists with required schema. Returns the DB path."""
    db_path = resolve_db_path(config)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_key TEXT NOT NULL UNIQUE, -- canonical URL
                source_url TEXT,
                listing_url TEXT,
                vin TEXT,
                location TEXT,
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS seen_registry (
                listing_key TEXT PRIMARY KEY,
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS listing_cache (
                listing_key TEXT PRIMARY KEY,
                last_scraped_at TEXT,
                data_blob TEXT
            );

            CREATE TABLE IF NOT EXISTS scrapes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL,
                scraped_at TEXT,
                method TEXT,
                status TEXT,
                raw_text TEXT,
                raw_html TEXT,
                data_json TEXT,
                FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_scrapes_listing_id ON scrapes(listing_id);

            CREATE TABLE IF NOT EXISTS parsed_listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL UNIQUE,
                updated_at TEXT,
                year INTEGER,
                model TEXT,
                trim TEXT,
                transmission_norm TEXT,
                mileage INTEGER,
                asking_price_usd INTEGER,
                exterior TEXT,
                interior TEXT,
                color_ext_bucket TEXT,
                color_int_bucket TEXT,
                raw_options TEXT,
                options_list TEXT,
                options_detected TEXT,
                options_by_category TEXT,
                top_options TEXT,
                vin TEXT,
                location TEXT,
                FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS enrichments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_id INTEGER NOT NULL UNIQUE,
                enriched_at TEXT,
                total_options_msrp INTEGER,
                msrp_breakdown TEXT,
                derived_json TEXT,
                notes TEXT,
                FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS rankings (
                run_timestamp TEXT NOT NULL,
                listing_id INTEGER NOT NULL,
                rank INTEGER NOT NULL,
                total_options_msrp INTEGER,
                PRIMARY KEY(run_timestamp, listing_id),
                FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS url_vin_index (
                canonical_url TEXT PRIMARY KEY,
                vin TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS vin_enriched (
                vin TEXT PRIMARY KEY,
                source TEXT,
                updated_at TEXT,
                link TEXT,
                raw TEXT,
                parsed_json TEXT,
                derived_json TEXT
            );

            CREATE TABLE IF NOT EXISTS listing_options (
                listing_id INTEGER NOT NULL,
                option_id TEXT NOT NULL,
                display TEXT,
                category TEXT,
                msrp INTEGER,
                value INTEGER,
                PRIMARY KEY(listing_id, option_id),
                FOREIGN KEY(listing_id) REFERENCES listings(id) ON DELETE CASCADE
            );
            """
        )
    finally:
        conn.close()
    return db_path
