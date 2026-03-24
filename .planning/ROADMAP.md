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

## Phase 03: Multi-version Blender test harness

Goal: Download, cache, and select multiple official Blender versions for automated test runs while preserving the current single-binary fallback.

**Requirements:** [TEST-01, TEST-02, TEST-03, TEST-04]

Plans:
- [x] 03-multi-version-blender-test-harness-01-PLAN.md — define the Blender version registry, cache layout, and download/checksum contract
- [x] 03-multi-version-blender-test-harness-02-PLAN.md — wire version selection into the test runner, docs, and verification workflow

## Phase 04: Blender test harness import-path repair

Goal: Make the Blender embedded pytest run collect `tests/integration/test_blender_matrix.py` without `ModuleNotFoundError: No module named 'test'` by exposing the root harness through a package-safe import path.

**Requirements:** [TEST-05]

Plans:
- [x] 04-blender-test-harness-import-path-repair-01-PLAN.md — expose the harness through the tests package and switch matrix coverage to the package-safe import path

## Phase 05: Testing TUI overhaul

Goal: Make Blender test runs readable by surfacing download progress, selected versions, and a cleaner terminal UI during the testing phase.

**Requirements:** [TEST-06, TEST-07]

Plans:
- [x] 05-testing-tui-overhaul-01-PLAN.md — surface download progress and version status in the outer harness
- [x] 05-testing-tui-overhaul-02-PLAN.md — replace the noisy Blender-side test output with a structured terminal UI

## Phase 06: Testing runner progress and logging

Goal: Make Blender test runs easy to monitor with colored progress, continued execution after failures, and timestamped logs for diagnosis.

**Requirements:** [TEST-08, TEST-09, TEST-10]

Plans:
- [x] 06-testing-runner-progress-and-logging-01-PLAN.md — add the colored grid progress/status renderer and unit coverage
- [x] 06-testing-runner-progress-and-logging-02-PLAN.md — keep the matrix running through failures, write timestamped logs, and summarize failures at the end
