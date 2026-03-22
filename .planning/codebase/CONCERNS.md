# Codebase Concerns

**Analysis Date:** 2026-03-22

## Tech Debt

**Runtime dependency bootstrap:**
- `__init__.py` installs packages with `pip` at runtime and upgrades `pip` inside Blender.
- Impact: startup depends on network access and mutates the user's Blender Python environment.
- Fix approach: ship wheels or require a prebuilt environment; avoid automatic `pip` upgrades.

**Monolithic state/UI layers:**
- `bl_git/state.py`, `ui/operators.py`, `bl_types/bl_object.py`, and `bl_types/dump_anything.py` are very large.
- Impact: changes are hard to isolate and regression risk stays high.
- Fix approach: split capture, diffing, UI state, and serialization into smaller modules.

## Known Bugs

**Tracked datablocks can miss UUIDs:**
- `bl_git/tracking.py` contains a direct bug note that new icospheres do not receive `cozystudio_uuid`.
- Impact: new datablocks can be skipped by capture, leaving block files incomplete.
- Fix approach: repair the assignment/subscription path and add a regression test for new primitive creation.

**Incomplete object restore paths:**
- `bl_types/bl_object.py` has `load_data(...): pass` and raises `Exception('No pose data yet (Fixed in a near futur)')` for missing pose data.
- Impact: object reconstruction can fail for armatures and pose-driven scenes.
- Fix approach: implement the missing path or fail earlier with a supported error.

**Manifest integrity is shallow:**
- `bl_git/manifest.py` checks keys and file presence, but not hash consistency or dependency validity.
- Impact: corrupted block contents can survive validation until a later checkout or commit.
- Fix approach: validate hashes against block JSON and dependency references.

## Security Considerations

**Runtime code installation:**
- `__init__.py` runs `pip install --upgrade pip` and installs `requirements.txt` from inside Blender.
- Impact: the add-on fetches and executes code from the network during normal use.
- Fix approach: avoid self-installation; use bundled wheels or an explicit setup step.

**Manifest permissions mismatch:**
- `blender_manifest.toml` declares no `[permissions]` even though runtime code uses filesystem and subprocess access in `__init__.py` and `bl_git/bootstrap.py`.
- Impact: packaging/review can fail, and required capabilities are not explicit.
- Fix approach: declare file/network permissions and document each requirement.

## Performance Bottlenecks

**Full-scene capture loop:**
- `bl_git/state.py` scans all tracked datablocks, serializes them, hashes them with `DeepHash`, and rebuilds UI state on timer-driven checks.
- Impact: large scenes add CPU and GC churn, which hurts responsiveness.
- Fix approach: track dirtier subsets and avoid rebuilding full state on every tick.

**Repeated diff/repo recomputation:**
- `bl_git/diffs.py` and `bl_git/state.py` rebuild staged/unstaged groups, branch lists, recent refs, and history during refresh.
- Impact: even small edits can trigger expensive repo and Blender traversals.
- Fix approach: separate repo metadata refresh from scene capture and cache unchanged sections.

**Blocking bootstrap writes:**
- `bl_git/bootstrap.py` calls `bpy.ops.wm.save_as_mainfile(..., copy=True)` when the bootstrap `.blend` is missing.
- Impact: initialization can block the UI and write a full copy unexpectedly.
- Fix approach: make bootstrap creation explicit or deferred.

## Fragile Areas

**Blender workaround code:**
- `bl_types/bl_collection.py` flushes history after load, `bl_types/bl_scene.py` contains an "ugly fix" for curve mapping, and `bl_types/bl_gpencil.py` uses a HACK to force geometry updates.
- Impact: these paths are tightly coupled to Blender internals and version changes.
- Safe modification: treat them as compatibility hotspots and change them only with integration coverage.

**Optimistic merge logic:**
- `bl_git/merge.py` uses tier-based merge rules and falls back to conflict markers for many overlaps.
- Impact: non-trivial merges often degrade to manual conflict resolution even when a narrower merge would work.
- Fix approach: add type-specific merge strategies or narrow automatic merging to safer datablocks.

**Type registry assumptions:**
- `bl_types/replication/protocol.py` and `auto_load.py` assume every registered implementation exists and exposes the expected methods.
- Impact: an unknown `type_id` or missing implementation can raise an AttributeError instead of a controlled error.
- Fix approach: validate registrations at startup and return explicit unsupported-type errors.

## Scaling Limits

**Polling-based UUID tracking:**
- `bl_git/tracking.py` assigns UUIDs by repeatedly iterating Blender collections.
- Impact: this scales poorly as datablock count grows.
- Fix approach: batch assignment work and move toward event-driven updates where Blender permits.

**Single-pass scene serialization:**
- `bl_types/bl_object.py` and `bl_types/bl_scene.py` serialize transforms, modifiers, constraints, render settings, sequencer data, and more in one pass.
- Impact: capture cost grows with scene complexity, not only with the changed data.
- Fix approach: split coarse scene capture into smaller dependency-aware subgraphs.

## Dependencies at Risk

**Runtime dependency chain:**
- `requirements.txt` pins `GitPython`, `gitdb`, `deepdiff`, and `typing_extensions`, and `__init__.py` imports them dynamically.
- Impact: startup fails if any wheel is unavailable or incompatible with the Blender Python ABI.
- Fix approach: vendor wheels or ship them with the extension package.

## Test Coverage Gaps

**Core runtime paths lack focused unit tests:**
- Current unit coverage is concentrated in `tests/unit/test_serialization.py` and `tests/unit/test_merge_logic.py`; most other coverage is integration-heavy under `tests/integration/*` and `tests/flow/*`.
- Impact: regressions in `bl_git/state.py`, `bl_git/checkout.py`, `bl_git/ops.py`, `ui/operators.py`, and `bl_types/*` can slip through.
- Fix approach: add fast unit tests for manifest validation, checkout/restore, UUID tracking, and operator preflight logic.

---

*Concerns audit: 2026-03-22*
