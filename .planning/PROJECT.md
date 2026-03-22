# Cozy Studio

## What This Is

Cozy Studio is a Blender add-on that brings Git-style version control to Blender datablocks. It serializes datablocks into readable JSON files, tracks them in a Git repository, and restores them back into Blender when users revisit earlier history.

It is designed to fit Blender's workflow instead of fighting it: autosave stays on, users can stage and commit changes from inside Blender, and the project stays understandable through history, diffs, checkout, merge, and rebase flows.

## Core Value

Let Blender projects use trustworthy Git history at datablock granularity without breaking autosave or forcing a non-Blender workflow.

## Requirements

### Validated

- ✓ Initialize a Git/Cozy Studio repository from Blender — existing feature
- ✓ Serialize individual datablocks into JSON files — existing feature
- ✓ Stage and unstage individual datablocks or grouped updates — existing feature
- ✓ Commit from inside Blender with clear blockers when something is wrong — existing feature
- ✓ Check out older commits, switch branches, and create branches from commits — existing feature
- ✓ Merge and rebase with conflict-resolution tools — existing feature
- ✓ Keep Blender autosave enabled without interference — existing behavior

### Active

- [ ] Keep the datablock history workflow reliable across real Blender projects
- [ ] Improve the usability of staging, checkout, and recovery flows as the product evolves
- [ ] Preserve compatibility with Blender autosave and repo state during future changes

### Out of Scope

- Full-file `.blend` snapshot versioning — conflicts with datablock-level history and readable diffs
- Recording raw user input instead of datablock state — too fragile for dependable history
- Disabling Blender autosave — the product is meant to work alongside it

## Context

This project is an existing Blender add-on. The repository already contains the core add-on code, UI, and tests, and the product description in `README.md` matches the current direction: version control for Blender datablocks with Git-backed history.

The main emphasis is on preserving a Blender-native experience while keeping the data model reviewable, reversible, and friendly to Git workflows.

## Constraints

- **Compatibility**: Must keep working with Blender's autosave and repo state — regressions here are high risk
- **Workflow**: Must feel native inside Blender — the add-on should not require users to leave the editor for basic Git actions
- **Data model**: Must keep datablock-level serialization readable and reversible — this is the product's differentiator

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use datablock-level JSON serialization | Keeps history readable and diffs actionable | ✓ Good |
| Keep autosave enabled | Avoids disrupting Blender's native safety net | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-21 after initialization*
