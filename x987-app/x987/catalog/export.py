"""
Generation Catalog Exporter

Builds a JSON catalog of models → generations → trims and options for FE/docs.
Options are sourced from per-generation MSRP overrides if available; otherwise options list is omitted and marked as defaults in the JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from x987.config.manager import get_config
from x987.vehicles import get_vehicle_catalog
from x987.options.registry import OptionsRegistry


def build_generation_catalog() -> Dict[str, Any]:
    cfg = get_config()
    vehicles = get_vehicle_catalog()
    # Build option id → display mapping from registry
    reg = OptionsRegistry()
    id_to_display: Dict[str, str] = {}
    for opt in reg.get_all_options():
        try:
            oid = getattr(opt, 'get_id')()
            disp = getattr(opt, 'get_display')()
            if oid:
                id_to_display[str(oid)] = disp
        except Exception:
            continue

    opg = cfg.get('options_per_generation', {}) or {}

    models_out: List[Dict[str, Any]] = []
    for m in vehicles:
        model_entry: Dict[str, Any] = {
            'name': m.name,
            'generations': []
        }
        # Model-level trims are not used; we list per-generation
        for g in m.generations:
            key = f"{m.name}-{g.code}"
            trims = [t.name for t in g.trims]
            # Options from per-generation MSRP map, if present
            gen_opts: List[Dict[str, Any]] = []
            options_default = True
            try:
                model_map = opg.get(m.name, {}) or {}
                gen_map = model_map.get(g.code, {}) or {}
                msrp_map = gen_map.get('msrp', {}) or {}
                if msrp_map:
                    for oid, msrp in msrp_map.items():
                        disp = id_to_display.get(str(oid), str(oid))
                        try:
                            msrp_int = int(msrp)
                        except Exception:
                            msrp_int = None
                        gen_opts.append({
                            'id': str(oid),
                            'display': disp,
                            'msrp': msrp_int
                        })
                    options_default = False
            except Exception:
                pass

            model_entry['generations'].append({
                'key': key,
                'code': g.code,
                'years': {'min': g.min_year, 'max': g.max_year},
                'trims': trims,
                'trims_default': False,  # trims come from config; considered authoritative
                'options': gen_opts,
                'options_default': options_default
            })
        models_out.append(model_entry)

    return {'models': models_out}


def export_generation_catalog_json(out_path: Path) -> Path:
    data = build_generation_catalog()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return out_path


if __name__ == '__main__':
    # Default output path co-located with FE API for easy serving
    default_out = Path.cwd().parent / 'x987-web' / 'apps' / 'api' / 'data' / 'generation_catalog.json'
    p = export_generation_catalog_json(default_out)
    print(f"✓ Exported generation catalog to {p}")
