# Architecture

**Analysis Date:** 2026-03-22

## Pattern Overview

**Overall:** Blender add-on with layered Git-backed datablock serialization.

**Key Characteristics:**
- Root add-on lifecycle lives in `__init__.py`, with automatic class discovery in `auto_load.py`.
- UI code reads a cached `BpyGit.ui_state` snapshot instead of querying Git directly from draw methods.
- Datablock capture/restore is split between `bl_git/` orchestration and `bl_types/` type adapters.

## Layers

**Addon entry layer:**
- Purpose: register/unregister Blender classes, install Python deps, and bootstrap auto-loading.
- Location: `__init__.py`
- Contains: add-on metadata, dependency installer operator, add-on preferences, registration hooks.
- Depends on: `auto_load.py`, `ui/`, `utils/timers.py`.
- Used by: Blender add-on enable/disable flow.

**UI layer:**
- Purpose: present repository status, staged/unstaged changes, history, branches, and conflicts.
- Location: `ui/`
- Contains: panels, operators, property definitions, UI lists, state cache, registration glue.
- Depends on: `bl_git.BpyGit` through `ui.state.git_instance`, `bpy` UI APIs.
- Used by: Blender 3D View sidebar panels and operators.

**Git orchestration layer:**
- Purpose: manage repo lifecycle, manifests, diff tracking, commit, checkout, merge, and rebase.
- Location: `bl_git/`
- Contains: `BpyGit` composition, mixins for ops/state/checkout/merge/blocks/manifest/diffs/bootstrap/tracking.
- Depends on: `gitpython`, `deepdiff`, `utils/write.py`, `utils/redraw.py`, `bl_types/`.
- Used by: `ui/operators.py`, `ui/state.py`, tests.

**Serialization layer:**
- Purpose: translate Blender datablocks to/from JSON-safe dictionaries.
- Location: `bl_types/`
- Contains: `DataTranslationProtocol`, `ReplicatedDatablock`, `BlObject`, `BlMesh`, `BlImage`, `BlCamera`, and similar modules.
- Depends on: `bpy`, `deepdiff`-adjacent helpers, `mode_context.py`, `dump_anything.py`.
- Used by: `bl_git.tracking.Track` and `BpyGit._current_state()` / `deserialize()`.

**Utility layer:**
- Purpose: persistence helpers, redraw helpers, timers, and shared JSON writers.
- Location: `utils/`
- Contains: `WriteDict`/`WriteList`, `Timers`, panel redraw helper.
- Depends on: `bpy`, standard library.
- Used by: `bl_git/`, `__init__.py`, `ui/`.

## Data Flow

**Repository bootstrap:**
1. Blender enables the add-on through `__init__.py:register()`.
2. `ui/registration.py` schedules `ui.state.check_and_init_git()` and `ui.state.init_git_on_load()`.
3. `ui.state.check_and_init_git()` resolves the current `.blend` folder and constructs `bl_git.BpyGit` when `.git` exists.
4. `BpyGit.__init__()` creates the protocol from `bl_types.get_data_translation_protocol()`, starts `bl_git.tracking.Track`, and loads `.cozystudio/manifest.json` when present.

**Capture and persistence:**
1. `BpyGit._check()` walks all registered datablock implementations and captures each datablock via `DataTranslationProtocol.capture()`.
2. Captured datablocks are normalized to JSON with `bl_git.json_io.serialize_json_data()` and hashed with `DeepHash`.
3. `bl_git.state.StateMixin._current_state()` builds `entries`, `blocks`, `groups`, and capture issues.
4. `bl_git.ops.OpsMixin.commit()` writes `.cozystudio/blocks/<uuid>.json` and updates `.cozystudio/manifest.json` through `utils.write.WriteDict`.

**Checkout / merge / rebase:**
1. `bl_git.checkout.CheckoutMixin` parks Cozy-managed changes with git stash before branch or commit switches.
2. `bl_git.checkout.CheckoutMixin._restore_from_manifest()` topologically sorts block UUIDs and reconstructs Blender datablocks from JSON.
3. `bl_git.merge.MergeMixin` loads manifests and block files from base/ours/theirs refs, then merges per UUID.
4. Conflicts are recorded in the manifest and surfaced through `ui.state.ui_state`.

**State Management:**
- UI-facing state is centralized in `ui.state.git_instance.ui_state`.
- Persistent Git metadata is kept in `BpyGit.manifest`, `BpyGit.state`, `BpyGit.diffs`, and `BpyGit.last_*` fields.
- The UI never recomputes Git state directly; it reads from the cached snapshot built by `BpyGit.refresh_ui_state()`.

## Key Abstractions

**`BpyGit` (`bl_git/__init__.py`):**
- Purpose: single repository controller for capture, staging, checkout, merge, and UI refresh.
- Pattern: composed mixin object with repo paths rooted at the current `.blend` directory.

**`DataTranslationProtocol` (`bl_types/replication/protocol.py`):**
- Purpose: route datablock operations to the correct `bl_*` implementation.
- Pattern: type-name keyed registry that calls `construct`, `dump`, `load`, `resolve`, and `resolve_deps`.

**`ReplicatedDatablock` (`bl_types/replication/protocol.py`):**
- Purpose: contract for per-datablock adapters.
- Pattern: each adapter module sets `_type` and `_class` so `bl_types.__init__.py` can register it.

**`Track` (`bl_git/tracking.py`):**
- Purpose: assign and maintain `cozystudio_uuid` values on supported datablocks.
- Pattern: periodic timer loop over all registered protocol implementations.

**`WriteDict` (`utils/write.py`):**
- Purpose: JSON-backed dictionary for manifest persistence.
- Pattern: mutating dict writes immediately unless `autowrite` is disabled.

## Entry Points

**Add-on load/unload:**
- Location: `__init__.py`
- Triggers: Blender enabling/disabling the add-on.
- Responsibilities: dependency checks, class registration, auto-load registration, timer cleanup.

**Automatic UI state init:**
- Location: `ui/registration.py` and `ui/state.py`
- Triggers: Blender timers and `load_post` handler.
- Responsibilities: create `BpyGit` once the file path is known and refresh panels when repo state changes.

**Auto-registration of classes:**
- Location: `auto_load.py`
- Triggers: add-on registration after dependencies are present.
- Responsibilities: import all submodules, topologically sort Blender classes, register panels/operators/property groups.

## Error Handling

**Strategy:**
- Use explicit blocker reports for UI actions and return structured `{"ok": ...}` results from Git operations.
- Fail closed on missing repo state, unresolved conflicts, or invalid manifest integrity.

**Patterns:**
- `bpy.types.Operator.report()` for user-facing feedback in `ui/operators.py` and `__init__.py`.
- Printed tracebacks in lower-level Git helpers when recovery is possible.

## Cross-Cutting Concerns

**Logging:** `print()` plus occasional `logging` in `bl_types/utils.py`.
**Validation:** manifest integrity checks in `bl_git/manifest.py` and commit preflight in `bl_git/ops.py`.
**Authentication:** not detected.

---

*Architecture analysis: 2026-03-22*
