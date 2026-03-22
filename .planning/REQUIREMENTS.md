# Requirements: Cozy Studio

**Defined:** 2026-03-21
**Core Value:** Let Blender projects use trustworthy Git history at datablock granularity without breaking autosave or forcing a non-Blender workflow.

## v1 Requirements

### Bootstrap

- [ ] **BOOT-01**: User can initialize a Cozy Studio repository from inside Blender.
- [ ] **BOOT-02**: Add-on startup clearly reports missing dependencies or setup blockers before repo actions run.

### Datablocks

- [ ] **DATA-01**: Supported datablock changes are captured into per-datablock JSON block files.
- [ ] **DATA-02**: Supported datablocks can be restored from stored block data when checking out history.
- [ ] **DATA-03**: Users can inspect staged and unstaged datablock changes before committing.

### History

- [ ] **HIST-01**: User can commit tracked changes from Blender and receive clear blockers when preconditions fail.
- [ ] **HIST-02**: User can check out earlier commits and branches and restore the matching scene state.
- [ ] **HIST-03**: User can create branches from commits inside Blender.

### Conflicts

- [ ] **CONF-01**: User can merge branches and see conflicts surfaced in the UI when automatic resolution fails.
- [ ] **CONF-02**: User can rebase branches and resolve conflicts through the add-on workflow.

### UI State

- [ ] **UI-01**: Repository status, history, and change groups load in the Blender UI without querying Git directly from draw methods.

## v2 Requirements

### Platform

- **PLAT-01**: Bundle or preinstall runtime dependencies so Blender does not need to bootstrap packages at startup.
- **PLAT-02**: Add explicit validation for manifest and stored block integrity before checkout or commit.

### Product

- **PROD-01**: User can synchronize changes with remote Git repositories from inside Blender.
- **PROD-02**: User can share or review changes with richer diff visualization for complex datablocks.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time collaborative editing | The product is local-first Git version control, not live co-editing. |
| Cloud-hosted project storage | The workflow is designed around local project folders and Git repos. |
| Non-Blender primary editing workflows | `.blend` datablocks remain the source of truth. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BOOT-01 | Phase 1 | Pending |
| BOOT-02 | Phase 1 | Pending |
| DATA-01 | Phase 2 | Pending |
| DATA-02 | Phase 2 | Pending |
| DATA-03 | Phase 2 | Pending |
| UI-01 | Phase 2 | Pending |
| HIST-01 | Phase 3 | Pending |
| HIST-02 | Phase 3 | Pending |
| HIST-03 | Phase 3 | Pending |
| CONF-01 | Phase 4 | Pending |
| CONF-02 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-21*
*Last updated: 2026-03-21 after initialization*
