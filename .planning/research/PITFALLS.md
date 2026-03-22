# Domain Pitfalls

**Domain:** Blender datablock Git version control
**Researched:** 2026-03-21
**Overall confidence:** MEDIUM

## Critical Pitfalls

### 1) Unstable serialization / identity
**What goes wrong:**
If datablocks are serialized from raw Blender state without canonicalization, the same meaning produces different JSON, hashes, or diffs across saves.

**Why it happens:**
Blender data can contain unordered properties, float noise, byte blobs, and implicit defaults. If identity depends on names or runtime object order, history becomes noisy and checkout/merge logic becomes brittle.

**Consequences:**
False diffs, commit churn, broken change grouping, and merges that fail on harmless edits.

**Warning signs:**
- Diff changes when nothing meaningful changed
- Re-saving the same scene rewrites many block files
- Float or key-order churn in tests/CI
- Hashes differ for equivalent datablocks

**Prevention:**
- Canonicalize JSON output
- Sort keys and normalize arrays where order is not semantic
- Round or normalize float precision
- Use persistent UUIDs for identity, not names or memory order
- Keep a round-trip test for every supported datablock type

**Phase:** Phase 1 (serialization/identity foundation)

### 2) Ignoring datablock dependency chains
**What goes wrong:**
Projects serialize a single datablock as if it were independent, then discover it cannot be restored correctly because its mesh, materials, animation, collections, or parent/child relationships were not included.

**Why it happens:**
Blender assets are usually hierarchies, not isolated records. The manual explicitly treats override hierarchies as a tree of related datablocks, and the repo tests already assume grouped staging and manifest bookkeeping.

**Consequences:**
Broken checkouts, duplicate objects, missing materials/animations, and “works on my scene” restores that fail on real projects.

**Warning signs:**
- Checkout restores an object but not its mesh/material/action
- Duplicate users appear after deserialize
- Group staging misses members
- Restored scenes lose links or constraints

**Prevention:**
- Track root datablocks and their dependency closure
- Stage/checkout by group, not only by leaf block
- Validate referential integrity before commit
- Add explicit handling for linked collections, meshes, actions, and modifiers

**Phase:** Phase 2 (dependency-aware staging/checkout)

### 3) Letting .blend/autosave state leak into repo state
**What goes wrong:**
The add-on treats Blender session files, autosaves, or backup files as if they were authoritative repository state.

**Why it happens:**
Blender’s Auto Save is a crash-recovery backup, not version control. The manual also distinguishes saved versions (.blend1, .blend2, etc.) from the current file. Cozy Studio must keep those safety nets separate from Git history.

**Consequences:**
Dirty worktrees after checkout, accidental commits of bootstrap .blend files, lost work during branch switches, and confusing recovery behavior.

**Warning signs:**
- `.blend` or `.blend1` files show up in staged changes
- Checkout leaves Cozy paths dirty
- Branch switches trigger unexpected carryover or overwrite prompts
- Users report “my autosave disappeared” or “repo state changed by itself”

**Prevention:**
- Never commit session `.blend` bootstrap files through Cozy paths
- Keep autosave enabled but isolated from repo writes
- Block branch/merge actions when Cozy worktree is dirty
- Park and restore working changes explicitly, with validation

**Phase:** Phase 2 (repo hygiene + checkout safety)

### 4) Using line-based merges for structured datablocks
**What goes wrong:**
JSON files are merged like text files instead of structured datablocks, so unrelated changes conflict or nested edits corrupt the result.

**Why it happens:**
Datablocks are semantic objects. A transform, material slot, or animation change needs field-aware three-way merge logic, not generic line merging.

**Consequences:**
Spurious conflicts, broken merges/rebases, and manual resolution for cases that should auto-merge.

**Warning signs:**
- Non-overlapping edits still conflict
- Merge results pass JSON parsing but fail Blender restore
- Conflict rate is high on simple branch work
- Nested data changes collapse into generic “updated X sections” output

**Prevention:**
- Merge by semantic sections and field type
- Keep a datablock-aware conflict model in the manifest
- Resolve transforms, collections, materials, and animation separately
- Add targeted tests for nested and non-overlapping edits

**Phase:** Phase 3 (merge/rebase engine)

### 5) Mishandling linked libraries and library overrides
**What goes wrong:**
The system assumes all data is local and editable, but Blender linked data has override hierarchies, non-editable portions, and relink/resync edge cases.

**Why it happens:**
Linked libraries are hierarchy-driven. Blender docs note that override hierarchies matter, auto-resync can be costly, and some data can be lost if a referenced armature base disappears.

**Consequences:**
Lost editability, broken overrides after relink, expensive load-time resyncs, or missing pose data on restore.

**Warning signs:**
- Linked assets reopen with partial or non-editable state
- Relocating a library changes more than expected
- Load time spikes due to resync
- Pose/rig data disappears when base data is missing

**Prevention:**
- Treat linked assets as a separate compatibility class
- Preserve hierarchy/root collection structure
- Validate editable vs non-editable override regions
- Avoid assuming a local datablock can safely replace a linked one

**Phase:** Phase 4 (linked assets / override support)

### 6) Weak staging granularity and incomplete commit preflight
**What goes wrong:**
Users stage one visible object but forget its dependent members or manifest updates, and commit succeeds with an incomplete snapshot.

**Why it happens:**
Datablock groups are easy to under-stage unless the tool auto-collects the full group and rejects partial commits.

**Consequences:**
Snapshots that replay incorrectly, manifest/blocks divergence, and hard-to-debug missing history.

**Warning signs:**
- Commit succeeds after staging only one member of a group
- Manifest and block files disagree
- Preflight allows commit with missing members

**Prevention:**
- Auto-stage group members and manifest updates together
- Make preflight blockers explicit and structured
- Require integrity checks before commit

**Phase:** Phase 2 (staging + commit preflight)

## Moderate Pitfalls

### 1) Confusing user-facing branch state with Blender session state
**What goes wrong:**
The UI says “on branch,” but Blender is actually detached, viewing history, or carrying parked changes.

**Warning signs:**
- History panel and repo head disagree
- Detached checkout is not surfaced clearly
- Return-branch state is missing after viewing past commits

**Prevention:**
- Show branch, detached, viewing-past, and return-target state explicitly
- Keep UI state derived from repo integrity, not guesswork

**Phase:** Phase 2 (checkout UX) / Phase 5 (diagnostics polish)

### 2) Over-committing noisy internals
**What goes wrong:**
Internal helper fields, hidden data, or bootstrap artifacts end up in history and obscure real changes.

**Warning signs:**
- Hidden or dot-prefixed data shows up in diffs
- History is dominated by internal churn

**Prevention:**
- Filter helper data and bootstrap artifacts
- Keep hidden/internal blocks out of normal stage/commit paths

**Phase:** Phase 1 (serialization rules)

## Minor Pitfalls

### 1) Underestimating load/performance cost
**What goes wrong:**
Per-datablock files and integrity checks are correct but become too slow for real scenes.

**Warning signs:**
- Save/check passes feel laggy on big scenes
- Checkout or refresh gets progressively slower

**Prevention:**
- Cache derived state carefully
- Batch file IO
- Keep expensive validation behind targeted triggers

**Phase:** Phase 5 (performance hardening)

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Serialization / identity | Hash churn, unstable JSON, false diffs | Canonicalize output, normalize floats, use UUIDs |
| Staging / checkout | Partial dependency restore, dirty worktree after branch switch | Group-aware stage/restore, explicit parking, integrity checks |
| Merge / rebase | Text-style merge conflicts on structured data | Semantic three-way merge and manifest-level conflict tracking |
| Linked libraries / overrides | Lost editability or hierarchy breakage | Preserve override hierarchies and validate linked data assumptions |

## Sources

- Cozy Studio project brief: `.planning/PROJECT.md`
- Repository README: `README.md`
- Tests covering serialization, staging, checkout, merge/rebase, and conflict handling:
  - `tests/unit/test_serialization.py`
  - `tests/unit/test_merge_logic.py`
  - `tests/unit/test_semantic_diff.py`
  - `tests/integration/test_git_flow.py`
  - `tests/integration/test_group_stage_commit.py`
  - `tests/integration/test_merge_rebase.py`
- Blender Manual: Save & Load (autosave, backup versions, hidden data-blocks)
  - https://docs.blender.org/manual/en/latest/editors/preferences/save_load.html
- Blender Manual: Library Overrides (hierarchies, resync, editable/non-editable overrides)
  - https://docs.blender.org/manual/en/latest/files/linked_libraries/library_overrides.html
- Blender Manual: Make Single User / linked data tools
  - https://docs.blender.org/manual/en/latest/scene_layout/object/editing/relations/make_single_user.html
