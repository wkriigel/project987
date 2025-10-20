"""
URL↔VIN index utilities

Stores a mapping from canonical listing URL → VIN so the scraping step can
skip opening VDP pages when VIN enrichment exists.

Primary storage: SQLite (when storage.mode = 'sqlite').
Fallback storage: x987-data/metadata/url_vin_index.json
Shape: { "<canonical_url>": "VIN", ... }
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

try:
    from x987.config import get_config
    from x987.db.core import get_connection as _db_conn, ensure_db as _db_ensure
    from x987.db.api import upsert_url_vin as _db_upsert
except Exception:
    get_config = None  # type: ignore
    _db_conn = None  # type: ignore
    _db_ensure = None  # type: ignore
    _db_upsert = None  # type: ignore


def _is_sqlite_enabled() -> bool:
    try:
        cfg = get_config()
        storage = cfg.get_storage_config() if hasattr(cfg, 'get_storage_config') else cfg.get('storage', {})
        return str((storage or {}).get('mode', 'sqlite')).lower() == 'sqlite'
    except Exception:
        return False


def _index_path() -> Path:
    p = Path('x987-data/metadata/url_vin_index.json')
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load_index() -> Dict[str, str]:
    # Prefer DB when enabled
    if _is_sqlite_enabled() and _db_conn is not None and _db_ensure is not None:
        try:
            cfg = get_config()
            _db_ensure(cfg)
            conn = _db_conn(cfg)
            try:
                rows = conn.execute("SELECT canonical_url, vin FROM url_vin_index").fetchall()
                return {str(r[0]): str(r[1]) for r in rows if r[0] and r[1]}
            finally:
                conn.close()
        except Exception:
            # Fall through to JSON
            pass
    try:
        p = _index_path()
        if p.exists():
            return json.loads(p.read_text(encoding='utf-8')) or {}
    except Exception:
        pass
    return {}


def save_index(idx: Dict[str, str]) -> None:
    if _is_sqlite_enabled() and _db_conn is not None and _db_upsert is not None and _db_ensure is not None:
        try:
            cfg = get_config()
            _db_ensure(cfg)
            conn = _db_conn(cfg)
            try:
                for url, vin in (idx or {}).items():
                    if url and vin:
                        _db_upsert(conn, url, vin)
            finally:
                conn.close()
            return
        except Exception:
            pass
    try:
        p = _index_path()
        p.write_text(json.dumps(idx, indent=2), encoding='utf-8')
    except Exception:
        pass


def upsert_url_vin(canonical_url: str, vin: str) -> None:
    if not canonical_url or not vin:
        return
    if _is_sqlite_enabled() and _db_conn is not None and _db_upsert is not None and _db_ensure is not None:
        try:
            cfg = get_config()
            _db_ensure(cfg)
            conn = _db_conn(cfg)
            try:
                _db_upsert(conn, canonical_url, vin)
            finally:
                conn.close()
            return
        except Exception:
            pass
    try:
        idx = load_index()
        if idx.get(canonical_url) == vin:
            return
        idx[canonical_url] = vin
        save_index(idx)
    except Exception:
        pass
