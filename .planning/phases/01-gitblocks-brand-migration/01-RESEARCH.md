# Phase 01 Plan 01: GitBlocks Brand Migration Research

## Legacy Brand Inventory

| Surface area | Current references | Visibility | Migration decision | Notes |
| --- | --- | --- | --- | --- |
| Product docs | `README.md` headings, body copy, quick-start, install steps use “Cozy Studio” | User-visible | Rename to GitBlocks | This is the clearest public-brand surface and should move first. |
| UI panel labels | `ui/panels.py` panel titles/category strings and welcome text use “Cozy Studio” / “Cozy” | User-visible | Rename to GitBlocks | Panel chrome is part of the Blender-facing product identity. |
| Operator text + errors | `ui/operators.py` descriptions and `self.report(...)` strings say “Cozy Studio” / “Cozy” | User-visible | Rename to GitBlocks | These are user-facing messages, not compatibility identifiers. |
| Property labels | `ui/props.py` property descriptions mention “Cozy” | User-visible | Rename to GitBlocks | Keep property *keys* stable for compatibility; change only copy. |
| Filesystem namespace | `.cozystudio/`, `.cozystudio/blocks/`, `.cozystudio/manifest.json` in `bl_git/*`, `ui/helpers.py`, tests | Compatibility + user-visible path | Keep legacy alias; introduce GitBlocks namespace as canonical | Existing repos/saved data depend on the current path layout. |
| Add-on module/import name | `cozystudio_addon` in tests and harnesses | Compatibility-only | Freeze for now as alias | Renaming this immediately would break imports, install expectations, and test harnesses. |
| Blender operator namespace | `bpy.ops.cozystudio.*` in runtime and tests | Compatibility-only | Freeze for now as alias | External scripts and tests target this namespace. |
| Blender registration IDs | `COZYSTUDIO_PT_*`, `COZYSTUDIO_UL_*`, `COZYSTUDIO_CommitItem` | Compatibility-only | Freeze for now as alias | Blender class IDs are part of registration and should not churn mid-migration. |
| WindowManager properties | `cozystudio_commit_message`, `cozystudio_branch_*`, `cozystudio_integration_*`, `cozystudio_conflict_strategy` | Compatibility-only | Freeze for now as alias | These keys are persisted UI state and are referenced throughout the codebase. |
| Datablock metadata | `cozystudio_uuid` in `bl_git/*`, `bl_types/*`, tests | Compatibility-only | Freeze for now as alias | Renaming would break serialized datablock compatibility. |
| Carryover marker | `cozystudio-carryover` in `bl_git/__init__.py` | Compatibility-only | Freeze for now as alias | Internal stash naming is part of repo-state continuity. |
| Redraw targets | `COZYSTUDIO_PT_*` names in `redraw(...)` calls | Compatibility-only | Freeze for now as alias | These are registration-linked identifiers, not prose. |
| Harness / env names | `COZYSTUDIO_BLENDER_BIN`, `COZYSTUDIO_TEST_DIR`, `COZYSTUDIO_KEEP_TEST_DIR` in `.env.example` and `test.py` | Compatibility-only | Freeze for now as alias | Test harness naming can be migrated later without affecting runtime behavior. |

## Compatibility Notes

- User-facing Cozy wording is legacy brand language and should be removed from UI/docs in favor of GitBlocks.
- Machine-facing identifiers that are part of saved data, Blender registration, or test harness entry points remain frozen for this phase.
- The search results show `cozystudio` is not just branding; it also names persistent paths, datablock metadata, and Blender API surfaces. Those need explicit compatibility handling instead of blind rename.
- Existing `tests/` expectations currently anchor the compatibility layer, so later implementation phases must update tests in lockstep with any runtime rename.

## Proposed Brand Contract

### Canonical brand

- **Public brand:** `GitBlocks`
- **Public slug:** `gitblocks`
- **Primary user-facing copy:** GitBlocks / gitblocks-style variants only

### Canonical storage and namespace policy

- **Canonical new-project namespace:** `.gitblocks/`
- **Compatibility alias:** `.cozystudio/` remains readable and writable for existing repositories and saved data during the migration window
- **Block storage layout:** `.gitblocks/blocks/{uuid}.json` as the target shape for new workspaces, with `.cozystudio/blocks/{uuid}.json` accepted as legacy input
- **Manifest path:** `.gitblocks/manifest.json` as canonical, with `.cozystudio/manifest.json` supported as a legacy alias

### Frozen compatibility identifiers

The following names stay frozen for this phase and should be treated as compatibility-only, not public branding:

- `cozystudio_addon`
- `bpy.ops.cozystudio.*`
- `COZYSTUDIO_PT_*`, `COZYSTUDIO_UL_*`, and other `COZYSTUDIO_` Blender class IDs
- `cozystudio_*` WindowManager properties
- `cozystudio_uuid`
- `cozystudio-carryover`

### Migration rules

1. **Rename public prose immediately**: docs, panel labels, operator descriptions, and user-visible warnings should say GitBlocks.
2. **Preserve compatibility for persisted data**: all legacy `.cozystudio/` paths and `cozystudio_uuid` fields must continue to load existing projects.
3. **Keep API identifiers stable until a dedicated compatibility-removal plan**: operator namespaces, Blender IDs, and harness names stay untouched unless a later phase explicitly migrates them.
4. **Prefer dual-read / single-write for storage migration**: new workspaces should target the GitBlocks namespace, but legacy repos must still round-trip through the Cozy Studio paths.

## Migration Map

| Legacy surface | Decision | Replacement / follow-up |
| --- | --- | --- |
| Cozy Studio docs and UI copy | Rename now | GitBlocks prose throughout |
| `.cozystudio/` repo layout | Compatibility alias | Canonical `.gitblocks/` for new workspaces |
| `cozystudio_addon` module name | Freeze | Add GitBlocks alias later if packaging requires it |
| `bpy.ops.cozystudio.*` | Freeze | Potential future alias layer, not part of this phase |
| `COZYSTUDIO_*` class IDs | Freeze | Potential future alias layer, not part of this phase |
| `cozystudio_uuid` metadata | Freeze | Must remain loadable for existing datablocks |
| `COZYSTUDIO_*` redraw hooks | Freeze | Keep aligned with registered class IDs |

## Repository Notes

- The current codebase is a mixed brand state: public copy says Cozy Studio, while the implementation already assumes a `cozystudio` persistence namespace.
- Later implementation phases should separate “rename the UI” from “migrate saved-state contracts” so compatibility regressions are easier to control.
- This phase is intentionally documentation-first; no runtime behavior changes are required here.
