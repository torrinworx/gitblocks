---
phase: 03-multi-version-blender-test-harness
plan: 01
subsystem: blender-test-harness
tags: [blender, testing, cache, downloads]
depends_on: []
provides:
  - tests/blender_versions.py
  - tests/unit/test_blender_versions.py
affects:
  - __init__.py
  - tests/conftest.py
  - tests/helpers.py
decisions:
  - "Resolve Blender release URLs from explicit version strings and cache installs under ~/.cache/gitblocks/blender by default."
metrics:
  duration: "~45m"
  completed: "2026-03-23"
---

# Phase 03 Plan 01: Multi-version Blender test harness Summary

Shared Blender version resolution and cache helpers with checksum-aware download/install plumbing.

## Completed Tasks

| Task | Name | Commit | Files |
| ---- | ---- | ------ | ----- |
| 1 | Write the Blender version resolver contract | e8a313d | tests/blender_versions.py, tests/unit/test_blender_versions.py |
| 2 | Add cache reuse and checksum-verified download behavior | e8a313d | tests/blender_versions.py, tests/unit/test_blender_versions.py |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Made the test suite importable outside Blender**
- **Found during:** Task 1
- **Issue:** `pytest` collection failed because `bpy` was imported unconditionally from the addon package and shared test helpers.
- **Fix:** Added optional Blender shims/guards in `__init__.py`, `tests/conftest.py`, and `tests/helpers.py` so unit tests can run in a normal Python environment.
- **Files modified:** `__init__.py`, `tests/conftest.py`, `tests/helpers.py`
- **Commit:** `e8a313d`

## Self-Check: PASSED
