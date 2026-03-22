# Roadmap: Cozy Studio

**Defined:** 2026-03-22

## Phase 1 — Foundation and Bootstrap

**Goal:** Make repo setup and dependency checks reliable in fresh Blender environments.

**Requirements:** BOOT-01, BOOT-02

**Success Criteria:**
1. Blender can initialize a Cozy Studio repo from the add-on UI.
2. Missing Python dependencies fail with clear user-facing blockers.
3. Repo bootstrap does not silently mutate or corrupt the project state.

## Phase 2 — Capture and UI State

**Goal:** Keep datablock capture, staging, and status display correct and responsive.

**Requirements:** DATA-01, DATA-02, DATA-03, UI-01

**Success Criteria:**
1. Supported datablocks serialize into stable JSON block files.
2. Staged versus unstaged changes are visible before commit.
3. UI status updates come from cached state instead of direct draw-time Git work.
4. Capture and refresh paths stay responsive on larger scenes.

## Phase 3 — Commit and History

**Goal:** Make commit, checkout, and branching workflows dependable inside Blender.

**Requirements:** HIST-01, HIST-02, HIST-03

**Success Criteria:**
1. Commit preflight surfaces blockers before destructive actions proceed.
2. Older commits restore the expected scene state.
3. Branch creation is available from the Blender UI.

## Phase 4 — Merge and Rebase

**Goal:** Support conflict-aware merge and rebase workflows with clear UI feedback.

**Requirements:** CONF-01, CONF-02

**Success Criteria:**
1. Merge conflicts are visible and actionable in the add-on UI.
2. Rebase conflicts are routed through the same recovery workflow.
3. Conflict state persists clearly enough to resume work after interruption.

## Coverage

| Phase | Requirements | Status |
|-------|--------------|--------|
| 1 | BOOT-01, BOOT-02 | Pending |
| 2 | DATA-01, DATA-02, DATA-03, UI-01 | Pending |
| 3 | HIST-01, HIST-02, HIST-03 | Pending |
| 4 | CONF-01, CONF-02 | Pending |

**Coverage:** 11/11 v1 requirements mapped

---
*Last updated: 2026-03-22 after initialization*
