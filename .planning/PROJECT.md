# Cozy Studio

## What This Is

Cozy Studio is a Blender add-on that brings Git-style version control to `.blend` projects by serializing datablocks into readable JSON files. It is for Blender users who want reviewable history, safe checkout/branching, and merge/rebase workflows without giving up Blender's normal save and autosave behavior.

## Core Value

Provide trustworthy, readable version control for Blender scenes and datablocks without making the Blender workflow brittle.

## Requirements

### Validated

- ✓ Users can initialize a Cozy Studio repository from the Blender UI.
- ✓ Supported datablocks are captured into JSON-backed block files.
- ✓ Users can stage, commit, checkout, branch, merge, and rebase from the add-on UI.

### Active

- [ ] Dependency bootstrap and repository setup stay reliable in fresh Blender installs.
- [ ] Datablock capture and restore stay correct for supported types.
- [ ] UI state stays responsive and reflects Git status without blocking draw paths.
- [ ] Conflicts and blockers are surfaced before destructive repo actions complete.

### Out of Scope

- Real-time multi-user collaboration — the add-on is local-first Git version control.
- Cloud sync or hosted project storage — project data stays in the user's repo.
- Non-Blender file formats as a primary source of truth — `.blend` datablocks remain the core model.

## Context

This is an existing Blender add-on codebase with layered architecture around add-on registration, UI state, Git orchestration, and datablock serialization. The current codebase map highlights a few important concerns: runtime dependency bootstrap inside Blender, a known UUID-tracking bug, incomplete restore paths for some datablocks, shallow manifest validation, and performance pressure from full-scene capture.

## Constraints

- **Runtime**: Must run inside Blender's embedded Python environment — the add-on depends on `bpy`.
- **Architecture**: Local Git repo rooted at the project `.blend` directory — all history lives on disk.
- **Compatibility**: Must preserve autosave and existing Blender workflows — version control cannot break normal editing.
- **Performance**: UI refresh and scene capture must stay responsive — large scenes already stress full-scene scans.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Git-backed datablock serialization | Keeps history readable and diffable instead of storing full `.blend` copies | ✓ Good |
| Local-first repository model | Fits Blender project folders and avoids external service dependencies | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (`/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (`/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-22 after initialization*
