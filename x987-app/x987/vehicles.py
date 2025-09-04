"""
Vehicle catalog utilities: configurable model/trim detection.

PROVIDES: Detects canonical model and trim from free text using config-driven catalog.
DEPENDS: x987.config.manager for config access.
CONTRACT: Returns (model, trim) where both are canonical names when detected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .config.manager import get_config


@dataclass
class TrimEntry:
    name: str
    synonyms: List[str]


@dataclass
class GenerationEntry:
    code: str
    min_year: Optional[int]
    max_year: Optional[int]
    trims: List[TrimEntry]


@dataclass
class ModelEntry:
    name: str
    synonyms: List[str]
    trims: List[TrimEntry]
    generations: List[GenerationEntry]


def _compile_word_pattern(terms: List[str]) -> re.Pattern:
    # Use word boundaries; allow dots/spaces between tokens (e.g., "GT3 RS")
    escaped = [re.escape(t) for t in terms if t and t.strip()]
    # Prioritize longer phrases by ordering handled at call site; regex matches any
    pattern = r"\b(?:" + r"|".join(escaped) + r")\b"
    return re.compile(pattern, re.IGNORECASE)


def _load_catalog() -> List[ModelEntry]:
    cfg: Dict[str, Any] = get_config().get('vehicles', {}) or {}
    models_cfg: Dict[str, Any] = cfg.get('models', {}) or {}

    catalog: List[ModelEntry] = []
    for key, val in models_cfg.items():
        if not isinstance(val, dict):
            continue
        name = str(val.get('name') or key)
        synonyms = [str(s) for s in (val.get('synonyms') or []) if str(s).strip()]
        trims_cfg = val.get('trims') or []
        trims: List[TrimEntry] = []
        # trims can be TOML arrays of tables [[...]] or dict map; handle both
        if isinstance(trims_cfg, list):
            for t in trims_cfg:
                if not isinstance(t, dict):
                    continue
                t_name = str(t.get('name') or '').strip()
                t_syn = [str(s) for s in (t.get('synonyms') or []) if str(s).strip()]
                if t_name:
                    trims.append(TrimEntry(name=t_name, synonyms=t_syn))
        elif isinstance(trims_cfg, dict):
            for t_name, syns in trims_cfg.items():
                t_name_s = str(t_name).strip()
                if not t_name_s:
                    continue
                if isinstance(syns, list):
                    t_syn = [str(s) for s in syns if str(s).strip()]
                else:
                    t_syn = [str(syns)] if syns else []
                trims.append(TrimEntry(name=t_name_s, synonyms=t_syn))
        # generations
        gens_cfg = val.get('generations') or []
        generations: List[GenerationEntry] = []
        if isinstance(gens_cfg, list):
            for g in gens_cfg:
                if not isinstance(g, dict):
                    continue
                code = str(g.get('code') or '').strip()
                years = g.get('years') or {}
                min_year = None
                max_year = None
                if isinstance(years, dict):
                    my = years.get('min')
                    mx = years.get('max')
                    try:
                        min_year = int(my) if my is not None else None
                    except Exception:
                        min_year = None
                    try:
                        max_year = int(mx) if mx is not None else None
                    except Exception:
                        max_year = None
                g_trims_raw = g.get('trims') or []
                g_trims: List[TrimEntry] = []
                if isinstance(g_trims_raw, list):
                    for t in g_trims_raw:
                        if not isinstance(t, dict):
                            continue
                        t_name = str(t.get('name') or '').strip()
                        t_syn = [str(s) for s in (t.get('synonyms') or []) if str(s).strip()]
                        if t_name:
                            g_trims.append(TrimEntry(name=t_name, synonyms=t_syn))
                generations.append(GenerationEntry(code=code, min_year=min_year, max_year=max_year, trims=g_trims))

        catalog.append(ModelEntry(name=name, synonyms=synonyms, trims=trims, generations=generations))

    return catalog


_CATALOG_CACHE: Optional[List[ModelEntry]] = None


def get_vehicle_catalog() -> List[ModelEntry]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE is None:
        _CATALOG_CACHE = _load_catalog()
    return _CATALOG_CACHE


def reload_catalog():
    global _CATALOG_CACHE
    _CATALOG_CACHE = None


def detect_model_and_trim(text: str, year: Optional[int] = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Detect canonical model and trim from text using config-driven catalog.

    Prefers more specific trims first by checking longer synonyms before shorter ones.
    """
    if not text:
        return None, None
    catalog = get_vehicle_catalog()
    if not catalog:
        return None, None

    # Normalize spacing
    s = str(text)

    detected_model: Optional[ModelEntry] = None
    # Find model by synonyms
    for model in catalog:
        if not model.synonyms:
            continue
        model_pat = _compile_word_pattern(sorted(model.synonyms, key=len, reverse=True))
        if model_pat.search(s):
            detected_model = model
            break

    if not detected_model:
        return None, None

    # Find the most specific trim, preferring generation that matches year
    detected_trim: Optional[str] = None
    candidate_trims: List[TrimEntry] = []

    if year is not None and detected_model.generations:
        # Select generation that matches year
        for g in detected_model.generations:
            if g.min_year is not None and year < g.min_year:
                continue
            if g.max_year is not None and year > g.max_year:
                continue
            candidate_trims.extend(g.trims)
            break

    # Fallback to union of all generation trims and model-level trims
    if not candidate_trims:
        all_gen_trims: List[TrimEntry] = []
        for g in detected_model.generations:
            all_gen_trims.extend(g.trims)
        candidate_trims = all_gen_trims + detected_model.trims

    # Build an ordered list of (trim_name, synonyms_sorted)
    ordered_trims: List[Tuple[str, List[str]]] = []
    for t in candidate_trims:
        syns = sorted(list(dict.fromkeys(t.synonyms + [t.name])), key=len, reverse=True)
        ordered_trims.append((t.name, syns))

    # Check longer synonyms first to avoid "Carrera" matching before "Carrera 4S"
    for t_name, syns in sorted(ordered_trims, key=lambda x: max(len(s) for s in x[1]), reverse=True):
        pat = _compile_word_pattern(syns)
        if pat.search(s):
            detected_trim = t_name
            break

    return detected_model.name, detected_trim
