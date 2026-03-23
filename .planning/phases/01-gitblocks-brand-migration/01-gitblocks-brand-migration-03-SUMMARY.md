---
phase: 01-gitblocks-brand-migration
plan: 03
subsystem: backend
tags: [gitblocks, cozystudio, compatibility, storage, redraw]

# Dependency graph
requires:
  - phase: 01-gitblocks-brand-migration-02
    provides: runtime brand contract and centralized brand constants
provides:
  - GitBlocks-first on-disk storage with legacy .cozystudio read compatibility
  - Shared path helpers for block and manifest resolution
  - Backend redraw hooks routed through centralized panel-id constants
affects:
  - 01-gitblocks-brand-migration-04-PLAN.md
  - 01-gitblocks-brand-migration-05-PLAN.md

# Tech tracking
tech-stack:
  added: [bl_git/paths.py]
  patterns: [GitBlocks-first storage with legacy fallback, shared namespace helpers, multi-panel redraw helper]

key-files:
  created:
    - bl_git/paths.py
    - .planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-03-SUMMARY.md
  modified:
    - bl_git/__init__.py
    - bl_git/blocks.py
    - bl_git/checkout.py
    - bl_git/diffs.py
    - bl_git/manifest.py
    - bl_git/merge.py
    - bl_git/ops.py
    - bl_git/state.py
    - branding.py
    - ui/helpers.py
    - ui/operators.py
    - ui/state.py
    - utils/redraw.py
    - .planning/phases/01-gitblocks-brand-migration/deferred-items.md

key-decisions:
  - "Canonical storage now resolves to .gitblocks/ while legacy .cozystudio paths remain readable for old repos."
  - "Block-path parsing is shared so backend code and UI file actions accept both namespaces consistently."
  - "Backend redraw targets stay centralized behind brand constants and a multi-panel redraw helper."

patterns-established:
  - "Pattern 1: write new storage to .gitblocks and only fall back to .cozystudio for reads"
  - "Pattern 2: parse block paths through a shared helper instead of repeating namespace literals"
  - "Pattern 3: route UI refreshes through centralized panel-id constants"

requirements-completed: [BRAND-04]

# Metrics
duration: 8 min
completed: 2026-03-23
---

# Phase 01: GitBlocks Brand Migration Summary

**GitBlocks-first storage plumbing with legacy repo compatibility and centralized backend redraw targets**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-23T15:45:18Z
- **Completed:** 2026-03-23T15:53:23Z
- **Tasks:** 2
- **Files modified:** 15

## Accomplishments

- Moved repo path handling to `.gitblocks/` for new writes while preserving `.cozystudio/` reads.
- Added a shared namespace helper for manifest and block paths so backend loaders, staging, and UI file actions agree.
- Centralized backend redraw targets behind brand constants and a reusable multi-panel redraw helper.

## Task Commits

1. **Task 1: Migrate repo path handling to GitBlocks-first storage** - `5aaaab9` (feat)
2. **Task 2: Repoint backend redraw hooks at the new panel identifiers** - `c27d4b3` (refactor)

## Files Created/Modified

- `bl_git/paths.py` - Shared canonical/legacy namespace helpers
- `bl_git/__init__.py` - Canonical and legacy storage roots
- `bl_git/blocks.py` - Dual-read block loading with canonical writes
- `bl_git/manifest.py` - Legacy manifest fallback and block-path filtering
- `bl_git/checkout.py` - Legacy-to-canonical manifest bootstrap and dual-namespace stashing
- `bl_git/ops.py` - Canonical staging paths and refresh helper usage
- `bl_git/merge.py` - Dual-namespace merge-safe path handling
- `bl_git/diffs.py` - Manifest ignore rules and refresh targets
- `bl_git/state.py` - Diff parsing and manifest source lookup
- `branding.py` - Panel-id constants and refresh target grouping
- `utils/redraw.py` - Multi-panel redraw helper
- `ui/helpers.py` - Block path parsing via shared helper
- `ui/operators.py` - File stage/revert helpers now parse both namespaces
- `ui/state.py` - History panel refresh constant usage
- `.planning/phases/01-gitblocks-brand-migration/deferred-items.md` - Logged out-of-scope legacy refs

## Decisions Made

- GitBlocks is the canonical on-disk namespace; Cozy Studio remains compatibility-only for reads and old repos.
- Shared path helpers are worth the small indirection to keep backend and UI compatibility behavior explicit.
- Backend redraw targets should be centralized now so later panel renames only touch the brand constants.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] UI file actions still assumed legacy block paths**
- **Found during:** Task 1 (storage migration)
- **Issue:** `ui/operators.py` still staged and reverted only `.cozystudio/blocks/` paths, which would miss canonical GitBlocks files.
- **Fix:** Routed group staging and revert path parsing through the shared namespace helper.
- **Files modified:** `ui/operators.py`, `bl_git/paths.py`
- **Verification:** `python3 -m py_compile ...` passed and the backend/UI namespace sweep found no literal block-path references in the touched surfaces.
- **Committed in:** `5aaaab9` (part of Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 missing critical compatibility fix)
**Impact on plan:** Compatibility behavior stayed explicit and the migration stayed GitBlocks-first.

## Issues Encountered

- `pytest` was not installed on the system interpreter, and a temporary venv could not run the suite because Blender's `bpy` module is unavailable outside Blender.
- Verified the touched Python modules with `python3 -m py_compile` and a repo-wide namespace sweep instead.
- An unrelated edit remains in `bl_types/README.md`; it was left untouched and logged separately in `deferred-items.md`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Storage and redraw plumbing are now GitBlocks-aware.
- Remaining legacy references are limited to compatibility surfaces and the later docs/test sweep.

## Self-Check: PASSED

- Summary file exists on disk.
- Task commits `5aaaab9` and `c27d4b3` are present in git history.

---
*Phase: 01-gitblocks-brand-migration*
*Completed: 2026-03-23*
