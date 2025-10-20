"""
SQLite-backed data layer for x987 (lightweight, single-user).

PROVIDES: Connection helpers, schema initialization, and simple CRUD ops.
DESIGN: Minimal surface area, no external ORM, JSON stored as TEXT.
"""

from .core import get_connection, ensure_db, resolve_db_path
from .api import (
    upsert_listing_by_key,
    get_listing_id_by_key,
    seen_is_seen,
    seen_get_first_seen,
    seen_mark_seen,
    cache_get,
    cache_save,
    insert_scrape,
    upsert_parsed,
    upsert_enrichment,
    upsert_url_vin,
    save_ranking_batch,
)

__all__ = [
    "get_connection",
    "ensure_db",
    "resolve_db_path",
    "upsert_listing_by_key",
    "get_listing_id_by_key",
    "seen_is_seen",
    "seen_get_first_seen",
    "seen_mark_seen",
    "cache_get",
    "cache_save",
    "insert_scrape",
    "upsert_parsed",
    "upsert_enrichment",
    "upsert_url_vin",
    "save_ranking_batch",
]

