Title: Transition to SQLite-backed Storage

Context
- App processes car listings in a single-user, agent-driven flow.
- Current storage uses CSV/JSON spread across steps (collection, scraping, transformation/enrichment, ranking).
- Need durable, linkable references for each car item across all stages.

Decision
- Adopt SQLite as the primary storage backend with a thin in-repo DAL.
- Keep CSV export paths for continuity and human inspection during migration.

Rationale
- SQLite requires no extra infrastructure, ships with Python, and is portable (single file under `x987-data/`).
- Strong data integrity and simple indexes/foreign keys.
- Easy to mirror existing JSON/CSV with minimal adapter code inside steps.

Alternatives Considered
- PostgreSQL/MySQL: excessive operational overhead for single-user local app.
- ORMs (SQLAlchemy/SQLModel): additional dependencies/boilerplate not warranted yet.
- TinyDB/JSON stores: insufficient relational linking and scaling for cross-stage references.

Consequences
- A single durable `listing_key` (canonical URL) links collection → scrapes → parsed/enriched → ranking.
- JSON/CSV artifacts remain as optional outputs (export) rather than primary storage.
- Clear migration path and staged cutover; rollback is trivial by continuing to read CSV/JSON.

