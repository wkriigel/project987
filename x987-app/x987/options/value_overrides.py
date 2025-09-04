"""
Options value overrides per model/generation from config.
"""

from typing import Optional, Dict, Any

from x987.config.manager import get_config
from x987.vehicles import get_vehicle_catalog


def _get_generation_code(model: Optional[str], year: Optional[int]) -> Optional[str]:
    if not model or not year:
        return None
    for m in get_vehicle_catalog():
        if m.name.lower() == model.lower():
            for g in m.generations:
                if (g.min_year is None or year >= g.min_year) and (g.max_year is None or year <= g.max_year):
                    return g.code
    return None


def get_override_value(option_id: str, model: Optional[str], year: Optional[int]) -> Optional[int]:
    """
    Return per-generation override value for an option if available.
    """
    cfg = get_config().get('options_per_generation', {}) or {}
    if not cfg or not model:
        return None
    model_map: Dict[str, Any] = cfg.get(model, {}) or {}
    if not model_map:
        return None
    gen_code = _get_generation_code(model, year)
    if gen_code is None:
        return None
    gen_map: Dict[str, Any] = model_map.get(gen_code, {}) or {}
    msrp_map: Dict[str, Any] = gen_map.get('msrp', {}) or {}
    if not msrp_map:
        return None
    # Normalize keys: option IDs in config can be quoted; compare case-insensitively
    for k, v in msrp_map.items():
        try:
            if str(k).lower() == str(option_id).lower():
                return int(v)
        except Exception:
            continue
    return None

