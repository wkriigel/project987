Title: Data Model Plan — Linking Across Stages

Unique Reference
- `listing_key` = canonicalized listing URL (scheme/host lowercase, stable query sans trackers).
- Stored in `listings.listing_key` (UNIQUE). Surrogate `listings.id` used as FK target.

Tables
- `listings(id, listing_key, listing_url, source_url, vin, location, created_at, updated_at)`
  - One row per discovered listing.
- `seen_registry(listing_key, first_seen_at, last_seen_at)`
  - Mirrors previous JSON; DB now the durable index for new runs.
- `listing_cache(listing_key, last_scraped_at, data_blob)`
  - Optional cache mirror for continuity (reads may remain file-based short-term).
- `scrapes(id, listing_id, scraped_at, method, status, raw_text, raw_html, data_json)`
  - Historical scrape snapshots; links to `listings`.
- `parsed_listings(listing_id, updated_at, year, model, trim, transmission_norm, mileage, asking_price_usd, …)`
  - One latest normalized record per listing.
- `enrichments(listing_id, enriched_at, total_options_msrp, msrp_breakdown, derived_json)`
  - Aggregated enrichment outputs (present/future use).
- `rankings(run_timestamp, listing_id, rank, total_options_msrp)`
  - Per-run ranking output.
- `url_vin_index(canonical_url, vin)` and `vin_enriched(vin, …)`
  - Imported reference stores enabling enriched shortcuts.

Relationships
- `listings.id` is referenced by `scrapes`, `parsed_listings`, `enrichments`, and `rankings`.
- External VIN enrichment joins via `vin` on demand.

