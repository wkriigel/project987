# CSV Schema for Ranking Output (Web FE Friendly)

Authoritative guidance for clean, extensible CSV output produced by the Python pipeline.

## Columns (recommended)

- year: int (e.g., 2010)
- model: string (e.g., Cayman)
- trim: string (e.g., S)
- model_trim: string (e.g., Cayman S) — transitional; may be removed later
- asking_price_usd: int (raw dollars)
- mileage: int (raw miles)
- total_options_msrp: int (raw dollars)
- options_list: string | string[] (comma-separated list ok)
- exterior: string (raw color name, e.g., "Malachite Green Metallic")
- interior: string (raw color name, e.g., "Black")
- exterior_hex: string (optional, e.g., "#2C5F51")
- interior_hex: string (optional)
- listing_url: string
- source_url: string

Notes:
- Keep values raw (no currency/k suffixes) for numeric fields. Formatting is FE’s job.
- Provide separate `model` and `trim`. `model_trim` can remain during transition.
- Provide separate `exterior` and `interior`; hex fields are optional but preferred when known.

## Writing CSV (Python)

```python
from csv import DictWriter

FIELDS = [
    'year','model','trim','model_trim',
    'asking_price_usd','mileage','total_options_msrp','options_list',
    'exterior','interior','exterior_hex','interior_hex',
    'listing_url','source_url'
]

with open(out_csv, 'w', newline='', encoding='utf-8') as f:
    w = DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
    w.writeheader()
    for rec in rows:
        # ensure separate fields populated
        if not rec.get('model') and rec.get('model_trim'):
            parts = str(rec['model_trim']).split(' ', 1)
            rec['model'] = parts[0]
            rec['trim'] = parts[1] if len(parts) > 1 else ''
        w.writerow(rec)
```

## Backwards compatibility

- During rollout, continue emitting `model_trim` while FE migrates fully. FE already prefers `model` + `trim` when present.
- Keep `exterior`/`interior` names authoritative; FE normalizes + maps to hex when missing.

## Filters & FE expectations

- Numeric columns (year, asking_price_usd, mileage, total_options_msrp) are raw integers — supports < / > filters.
- Text columns (model, trim, exterior, interior) are simple strings — FE builds facets and free-text filters.

