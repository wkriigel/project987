Title: Risk Register — DB Transition

Known Risks
- Data mismatch during dual-write period (CSV vs DB).
- Incorrect URL canonicalization leading to split identities.
- Partial imports from historical CSVs (missing URL columns in some files).
- Concurrency edge cases (not expected; single-user design).

Mitigations
- Use canonical URL function used in pipeline for identity.
- Import scripts are idempotent; can be re-run safely.
- Retain CSV/JSON artifacts; DB writes are additive.
- Foreign keys + UNIQUE constraints prevent silent duplication.

Rollback Triggers
- Row counts deviate substantially from CSV snapshots without clear cause.
- Webapp cannot resolve listings by URL consistently.

Rollback Plan
- Switch `storage.mode = 'files'`; disable DB persistence.
- Continue using CSV/JSON while issues are investigated.

