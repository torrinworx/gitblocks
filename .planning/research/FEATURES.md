# Feature Landscape: Cozy Studio

**Domain:** Blender datablock version control
**Researched:** 2026-03-21
**Overall confidence:** MEDIUM

## Table Stakes

Features users expect. Missing = the product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---|---|---:|---|
| Repository/project initialization | Every competitor starts with a way to connect Blender work to a versioned store. | Low | Must create/attach repo cleanly from Blender. |
| Commit/save a version | Core action for any history tool. | Low | Needs clear commit blockers and good messages. |
| Browse history | Users need to see prior versions to trust the system. | Low | Commit list / checkpoint list / timeline view. |
| Checkout / restore older versions | The whole point is recovery and iteration. | Med | Must be safe with unsaved Blender state. |
| Branch creation and switching | Standard Git-style workflow in every visible competitor. | Med | Needed for parallel modeling/scene variants. |
| Diff / compare versions | Users need to know what changed before restoring. | Med | Basic diff is expected even if it is not semantic. |
| Revert / undo to a prior state | Fast recovery is a baseline expectation. | Low | Often the most-used rescue path. |
| Readable on-disk representation | Binary `.blend` alone is not enough for reviewable history. | Med | JSON/datablock serialization or equivalent. |
| Autosave-safe workflow | Blender users expect autosave to keep working. | Med | Product must not fight Blender’s native safety net. |

## Differentiators

Features that are competitive advantages, not just baseline expectations.

| Feature | Value Proposition | Complexity | Notes |
|---|---|---:|---|
| Datablock-level versioning | Much smaller, more understandable changes than full-file snapshots. | High | Core Cozy Studio differentiator. |
| Stage / unstage individual datablocks or grouped changes | Gives users Git-like control at the right granularity. | High | Requires precise change grouping and UI clarity. |
| Commit blockers with actionable messages | Prevents bad history and makes failures understandable. | Med | Better DX than silent failure or raw Git errors. |
| Merge and rebase with conflict-resolution tools | Enables real team workflows instead of just local history. | High | Hardest “Git-real” feature in Blender context. |
| Geometry-aware / semantic diff | Lets artists review mesh/object changes, not bytes. | High | Strong differentiator seen in newer tools. |
| Per-object / per-datablock history timeline | Makes finding the right change much faster. | High | Depends on stable identity across commits. |
| Visual side-by-side compare inside Blender | Keeps review in-context and reduces tool switching. | High | Strong UX differentiator. |
| Commit graph inside the viewport | Nice-to-have that boosts discoverability and trust. | High | Mainly a UX differentiator. |
| Multiple repository storage modes | Helps fit different studio setups without changing workflow. | Med | Inline/hidden/shared repo layouts are valuable. |
| Real-time change tracking | Removes manual export steps for routine edits. | High | Blendit-style “track edits as they happen.” |
| Project regeneration from stored history | Makes the project resilient even if `.blend` files are lost. | High | Strong recovery story, but complex. |

## Anti-Features

Features to deliberately NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|---|---|---|
| Full-file `.blend` snapshot versioning as the core model | Diffs stay opaque and repos get bulky. | Use datablock-level serialization. |
| Recording raw user input instead of state | Too fragile and not reproducible. | Track actual datablock state changes. |
| Disabling Blender autosave | Breaks a key safety net. | Coexist with autosave. |
| Requiring users to leave Blender for basic VCS actions | Harms adoption and breaks workflow. | Keep core actions in the Blender UI. |
| Hiding history behind opaque binary blobs | Users cannot audit or trust changes. | Keep history readable and inspectable. |
| Making Git expertise mandatory for basic use | Raises onboarding cost too much. | Abstract staging, commits, branches, and restore flows. |

## Feature Dependencies

```text
Datablock serialization → readable diff / compare → checkout / restore
Repository initialization → commit history → branch switching
Change detection → stage / unstage → commit
Stable object identity → semantic diff → per-object history timeline
History graph → merge / rebase → conflict resolution tools
Autosave-safe state management → checkout / restore / recovery flows
```

## MVP Recommendation

Prioritize:
1. Repository initialization + commit/history browsing
2. Checkout / restore + branch switching
3. Datablock-level readable serialization

Defer: semantic geometry diff and per-object timelines; they are powerful differentiators but expensive to get right.

## Sources

- https://github.com/imaginelenses/blendit
- https://github.com/makehappyinstall/blender_git
- https://github.com/bkrmendy/cg_timeline
- https://github.com/torrinworx/cozystudio_blender
