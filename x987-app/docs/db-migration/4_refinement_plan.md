Title: Refinement Plan — Simplifications Enabled by DB

Immediately
- Stable ID: Use `listings.id` across modules instead of passing long URLs.
- Drop fragile CSV field coupling between steps; use DB queries for joins.
- De-dupe logic can leverage `listings` and `scrapes` counts/recency.

Near-term
- Replace JSON `SeenRegistry` and `ListingCache` reads with DB-backed adapters.
- Consolidate options/enrichment breakdowns under `enrichments`.
- Add light views (e.g., SQL views) for common queries used by the webapp.

Later
- Introduce `runs` table to track end-to-end pipeline executions and enable reproducible slicing.

