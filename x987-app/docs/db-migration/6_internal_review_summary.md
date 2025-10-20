Title: Internal Review — Storage Transition

Quality of Decision
- Matches app scale and philosophy (lightweight, modular, maintainable).
- Limits dependencies; straightforward to reason about and to debug.

Maintainability
- Small, explicit DAL with JSON-through-DB strategy for nested blobs.
- Schema names map directly to pipeline stages.

Alignment with Objectives
- Durable linkage via `listing_key` across collection → scraping → parsed/enriched → ranking.
- Staged migration with dual-write ensures continuity and easy rollback.

Readiness
- Code paths added behind config flag; defaults to SQLite.
- Migration script provided; historical data import supported.
- Next steps identified to phase out legacy JSON reads.

