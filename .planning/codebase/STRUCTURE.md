# Codebase Structure

**Analysis Date:** 2026-03-22

## Directory Layout

```text
gitblocks/
├── __init__.py            # Blender add-on entry point and registration
├── auto_load.py           # Automatic submodule import and class registration
├── bl_git/                # Git repository orchestration and manifest/state logic
├── bl_types/              # Blender datablock adapters and serialization protocol
├── ui/                    # Panels, operators, UI state, property groups
├── utils/                 # Shared helpers for persistence, timers, redraw
├── tests/                 # Pytest suite split by unit, integration, and flow
├── blender_manifest.toml   # Blender extension metadata
├── requirements.txt       # Python dependencies installed inside Blender
├── pytest.ini             # Test markers and test root configuration
├── README.md              # User-facing project overview
└── .env.example           # Example environment configuration only
```

## Directory Purposes

**Root (`/`):**
- Purpose: package entry point, extension metadata, and top-level docs/config.
- Contains: `__init__.py`, `auto_load.py`, `README.md`, `requirements.txt`, `pytest.ini`, `blender_manifest.toml`.
- Key files: `__init__.py`, `auto_load.py`, `blender_manifest.toml`.

**`bl_git/`:**
- Purpose: all repo-specific behavior for capture, persistence, checkout, merge, and UI state generation.
- Contains: mixins in `blocks.py`, `bootstrap.py`, `checkout.py`, `diffs.py`, `manifest.py`, `merge.py`, `ops.py`, `state.py`, `tracking.py`, `json_io.py`, `constants.py`.
- Key files: `bl_git/__init__.py`, `bl_git/state.py`, `bl_git/ops.py`, `bl_git/merge.py`, `bl_git/checkout.py`.

**`bl_types/`:**
- Purpose: datablock-specific adapters and serialization helpers.
- Contains: `bl_*.py` modules for each supported Blender type, plus `replication/`, `mode_context.py`, `dump_anything.py`, and helper modules.
- Key files: `bl_types/__init__.py`, `bl_types/bl_object.py`, `bl_types/bl_mesh.py`, `bl_types/bl_scene.py`, `bl_types/replication/protocol.py`.

**`ui/`:**
- Purpose: Blender-facing panels and operators for repository setup and Git workflows.
- Contains: `panels.py`, `operators.py`, `props.py`, `lists.py`, `helpers.py`, `state.py`, `registration.py`.
- Key files: `ui/panels.py`, `ui/operators.py`, `ui/state.py`, `ui/props.py`.

**`utils/`:**
- Purpose: generic helpers reused across the add-on.
- Contains: `write.py`, `timers.py`, `redraw.py`.
- Key files: `utils/write.py`, `utils/timers.py`.

**`tests/`:**
- Purpose: unit, integration, and flow coverage for Git state, UI registration, serialization, and commit workflows.
- Contains: `tests/unit/`, `tests/integration/`, `tests/flow/`, `tests/conftest.py`, `tests/helpers.py`, `tests/runner.py`.
- Key files: `tests/conftest.py`, `tests/helpers.py`, `tests/runner.py`.

## Key File Locations

**Entry Points:**
- `__init__.py`: add-on registration, dependency installation, preferences.
- `auto_load.py`: imports submodules and registers Blender classes in dependency order.
- `tests/runner.py`: Blender-hosted pytest bootstrap.

**Configuration:**
- `blender_manifest.toml`: extension metadata and minimum Blender version.
- `requirements.txt`: pip packages expected inside Blender.
- `pytest.ini`: test roots and markers (`unit`, `integration`, `install`, `flow`).

**Core Logic:**
- `bl_git/__init__.py`: `BpyGit` composition and path setup.
- `bl_git/state.py`: UI snapshot and datablock capture state.
- `bl_git/ops.py`: init, stage, unstage, commit, and preflight checks.
- `bl_git/checkout.py`: branch switching, checkout, parked-change recovery.
- `bl_git/merge.py`: merge/rebase and conflict resolution.
- `bl_types/__init__.py`: translation protocol assembly.

**Testing:**
- `tests/unit/`: pure logic tests for serialization, merge logic, and grouping.
- `tests/integration/`: Blender/UI/Git integration coverage.
- `tests/flow/`: end-to-end scenario coverage.

## Naming Conventions

**Files:**
- Python modules use `snake_case.py` such as `ui/state.py` and `bl_git/checkout.py`.
- Datablock adapters use `bl_<type>.py` such as `bl_types/bl_mesh.py` and `bl_types/bl_camera.py`.

**Directories:**
- Feature areas use short package names like `ui/`, `utils/`, `bl_git/`, and `bl_types/`.
- Nested test tiers use `tests/unit/`, `tests/integration/`, and `tests/flow/`.

## Where to Add New Code

**New feature touching Blender UI:**
- Primary code: `ui/operators.py` for actions, `ui/panels.py` for layout, `ui/props.py` for WindowManager properties.
- Tests: `tests/integration/` for Blender registration or operator behavior.

**New repository behavior:**
- Primary code: `bl_git/ops.py`, `bl_git/checkout.py`, `bl_git/merge.py`, or `bl_git/state.py` depending on responsibility.
- Tests: `tests/unit/` for pure logic; `tests/integration/` for Blender-repo interactions.

**New datablock type adapter:**
- Implementation: `bl_types/bl_<name>.py` with `_type` and `_class` exports.
- Registration hook: add the module name to `bl_types/__init__.py::__all__`.

**Shared helpers:**
- Utilities: `utils/write.py`, `utils/redraw.py`, or `utils/timers.py`.

## Special Directories

**`bl_types/replication/`:**
- Purpose: protocol and exception layer extracted from the replication model.
- Generated: No.
- Committed: Yes.

**`tests/`:**
- Purpose: organized by runtime scope and pytest marker.
- Generated: No.
- Committed: Yes.

**`.planning/codebase/`:**
- Purpose: generated mapping documents for planning workflows.
- Generated: Yes.
- Committed: Not part of application runtime.

---

*Structure analysis: 2026-03-22*
