# Roadmap

## Phase 01: GitBlocks brand migration

Goal: Rebrand the add-on to GitBlocks while preserving compatibility for existing repos and saved data.

**Requirements:** [BRAND-01, BRAND-02, BRAND-03, BRAND-04, BRAND-05]

Plans:
- [x] 01-gitblocks-brand-migration-01-PLAN.md — audit legacy brand usage and write the migration map
- [x] 01-gitblocks-brand-migration-02-PLAN.md — migrate runtime UI and addon metadata to GitBlocks
- [x] 01-gitblocks-brand-migration-03-PLAN.md — migrate storage paths and redraw hooks to GitBlocks-compatible namespaces
- [x] 01-gitblocks-brand-migration-04-PLAN.md — update docs and local harnesses for the new brand
- [x] 01-gitblocks-brand-migration-05-PLAN.md — update tests and run the final brand verification sweep

## Phase 02: GitBlocks brand cleanup

Goal: Remove the remaining legacy brand surfaces and compatibility aliases so GitBlocks is the only brand left in code, docs, tests, and harnesses.

**Requirements:** [BRAND-06, BRAND-07]

Plans:
- [x] 02-gitblocks-brand-cleanup-01-PLAN.md — rebrand the runtime addon surface and UI registration to GitBlocks only
- [x] 02-gitblocks-brand-cleanup-02-PLAN.md — remove legacy storage namespace and internal identifier fallbacks
- [x] 02-gitblocks-brand-cleanup-03-PLAN.md — update tests and harnesses to the renamed identifiers
- [x] 02-gitblocks-brand-cleanup-04-PLAN.md — finish docs, metadata, and the final zero-legacy sweep
