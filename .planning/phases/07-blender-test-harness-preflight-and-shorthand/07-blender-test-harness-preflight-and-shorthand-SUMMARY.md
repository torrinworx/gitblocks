---
phase: 07-blender-test-harness-preflight-and-shorthand
plan: complete
subsystem: testing-harness
tags: [blender, pytest, preflight, shorthand]
requires: [TEST-11, TEST-12]
provides: [compatibility-gate, single-test-shorthand]
affects: [test.py, tests/runner.py, tests/blender_versions.py, tests/unit/test_blender_versions.py, tests/unit/test_test_entrypoint.py, tests/unit/test_runner_selection.py, README.md, .env.example]
tech-stack: [python, pytest, argparse]
key-files: [tests/blender_versions.py, test.py, tests/runner.py, README.md, .env.example]
decisions: [Use the supported Blender matrix 4.1.0, 4.5.1, 5.1.0 for compatibility gating; forward --test / GITBLOCKS_TEST_FILTER as a pytest -k shorthand]
metrics:
  duration: "~"
  completed: "2026-03-24"
---

# Phase 07 Plan 01+02: Blender Test Harness Preflight and Shorthand Summary

Added a fail-fast Blender compatibility gate and a single-test shorthand that flows from the outer harness into the Blender-side pytest run.

## Completed Work

- Added `SUPPORTED_BLENDER_VERSIONS`, `BlenderCompatibilityResult`, and `check_blender_compatibility(...)`.
- Gate unsupported version selections before any Blender subprocess starts.
- Added `--test` support to the outer harness and inner runner.
- Forwarded the shorthand selector only to the `not install` phase via `pytest -k`.
- Updated README and `.env.example` with the supported matrix and filter example.

## Verification

- `PYTHONPATH=. uv run --with pytest pytest tests/unit/test_blender_versions.py tests/unit/test_test_entrypoint.py tests/unit/test_runner_selection.py -q`

## Deviations from Plan

None.

## Known Stubs

None.

## Commits

- `3e6211e` — add Blender compatibility gate
- `843c285` — add preflight gate and test shorthand

## Self-Check: PASSED
