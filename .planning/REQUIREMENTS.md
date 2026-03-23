# Requirements: Cozy Studio / GitBlocks

**Defined:** 2026-03-23
**Core Value:** Blender add-on for Git-backed datablock version control.

## v1 Requirements

### Brand Migration

- [x] **BRAND-01**: Inventory every `Cozy Studio` / `cozystudio` / `cozy` variation and classify each occurrence by surface area.
- [x] **BRAND-02**: Define and document the canonical GitBlocks brand contract, including compatibility policy for legacy names and on-disk paths.
- [x] **BRAND-03**: Migrate runtime UI and public-facing addon metadata to GitBlocks branding through a shared brand contract.
- [x] **BRAND-04**: Migrate backend storage/path handling and UI refresh identifiers to GitBlocks-compatible namespaces.
- [ ] **BRAND-05**: Update docs, test harnesses, and automated tests, then verify only intentional legacy aliases remain.

## v2 Requirements

Deferred until the migration phase is complete.

### Brand Clean-up

- **BRAND-06**: Remove compatibility aliases once all consumers have moved to GitBlocks.
- **BRAND-07**: Rename remaining internal identifiers if and only if the compatibility layer is retired.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Shipping a hard removal of all Cozy Studio aliases | This phase preserves compatibility for existing repos and saved data. |
| Rewriting unrelated Blender add-on behavior | Brand migration must not break autosave or repo-state behavior. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BRAND-01 | Phase 01 | Complete |
| BRAND-02 | Phase 01 | Complete |
| BRAND-03 | Phase 02 | Complete |
| BRAND-04 | Phase 03 | Complete |
| BRAND-05 | Phase 05 | Pending |

**Coverage:**
- v1 requirements: 5 total
- Mapped to phases: 5
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-23*
*Last updated: 2026-03-23 after Phase 01 Plan 01*
