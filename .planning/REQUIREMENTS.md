# GitBlocks Requirements

**Defined:** 2026-03-23
**Core Value:** Blender add-on for Git-backed datablock version control.

## v1 Requirements

### Brand Migration

- [x] **BRAND-01**: Inventory every legacy brand variation and classify each occurrence by surface area.
- [x] **BRAND-02**: Define and document the canonical GitBlocks brand contract, including compatibility policy for legacy names and on-disk paths.
- [x] **BRAND-03**: Migrate runtime UI and public-facing addon metadata to GitBlocks branding through a shared brand contract.
- [x] **BRAND-04**: Migrate backend storage/path handling and UI refresh identifiers to GitBlocks-compatible namespaces.
- [x] **BRAND-05**: Update docs, test harnesses, and automated tests, then verify only intentional legacy aliases remain.

## v2 Requirements

Planned for the GitBlocks brand cleanup phase.

### Brand Clean-up

- [x] **BRAND-06**: Remove compatibility aliases once all consumers have moved to GitBlocks.
- [x] **BRAND-07**: Rename remaining internal identifiers if and only if the compatibility layer is retired.

### Multi-version Blender Test Harness

- [x] **TEST-01**: Define a version manifest, cache layout, and official Blender release URL rules for local test installs.
- [x] **TEST-02**: Download Blender releases from the official archive, verify checksums, and reuse cached installs instead of redownloading.
- [x] **TEST-03**: Select a Blender version from CLI or environment without breaking the current single-binary fallback.
- [x] **TEST-04**: List installed Blender versions and run the harness across a version matrix with clear per-version results.

### Blender Matrix Import Path Repair

- [x] **TEST-05**: Make the Blender test harness importable through a package-safe path inside Blender's embedded pytest environment, so `tests/integration/test_blender_matrix.py` collects without `ModuleNotFoundError: No module named 'test'`.

### Testing TUI Overhaul

- [x] **TEST-06**: Surface Blender download progress and selected version status in the test harness so long installs do not look frozen.
- [x] **TEST-07**: Replace the noisy Blender-side test output with a structured terminal UI that prints stage headers, readable per-test results, and concise summaries.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Shipping a hard removal of all legacy aliases | This phase preserves compatibility for existing repos and saved data. |
| Rewriting unrelated Blender add-on behavior | Brand migration must not break autosave or repo-state behavior. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BRAND-01 | Phase 01 | Complete |
| BRAND-02 | Phase 01 | Complete |
| BRAND-03 | Phase 01 | Complete |
| BRAND-04 | Phase 01 | Complete |
| BRAND-05 | Phase 01 | Complete |
| BRAND-06 | Phase 02 | Complete |
| BRAND-07 | Phase 02 | Complete |
| TEST-01 | Phase 03 | Complete |
| TEST-02 | Phase 03 | Complete |
| TEST-03 | Phase 03 | Complete |
| TEST-04 | Phase 03 | Complete |
| TEST-05 | Phase 04 | Planned |
| TEST-06 | Phase 05 | Planned |
| TEST-07 | Phase 05 | Planned |

**Coverage:**
- Requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-23*
*Last updated: 2026-03-23 after Phase 02 cleanup*
