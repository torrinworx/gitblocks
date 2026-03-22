# Technology Stack

**Analysis Date:** 2026-03-21

## Languages

**Primary:**
- Python 3.x - Core add-on code in `__init__.py`, `bl_git/`, `bl_types/`, `ui/`, `utils/`, and `tests/`

**Secondary:**
- TOML - Blender extension metadata in `blender_manifest.toml`
- INI - Pytest configuration in `pytest.ini`

## Runtime

**Environment:**
- Blender 4.5.3 with embedded Python - Declared in `__init__.py` via `bl_info` and targeted by `test.py`

**Package Manager:**
- pip - Used by `__init__.py`, `tests/runner.py`, and the install-dependencies operator
- Lockfile: missing

## Frameworks

**Core:**
- Blender add-on API (`bpy`) - UI, operators, timers, handlers, properties, file I/O, and repo lifecycle in `__init__.py`, `ui/`, and `bl_git/`
- GitPython - Git repository operations in `bl_git/__init__.py`, `bl_git/ops.py`, `bl_git/checkout.py`, `bl_git/merge.py`, and `ui/operators.py`

**Testing:**
- pytest - Test runner configured in `pytest.ini` and executed from `tests/runner.py`
- pytest-order - Test ordering used in `tests/integration/*.py`

**Build/Dev:**
- `auto_load.py` - Dynamic Blender class registration and dependency ordering
- `test.py` / `tests/runner.py` - Blender-based test launcher and environment bootstrap

## Key Dependencies

**Critical:**
- `GitPython==3.1.45` - Git repository, commit, branch, stash, fetch, and merge operations
- `deepdiff==8.6.1` - Hashing and change detection for datablock serialization in `bl_git/state.py` and `bl_git/merge.py`

**Infrastructure:**
- `gitdb==4.0.12` - GitPython backend dependency
- `typing_extensions==4.9.0` - Type hint compatibility in the add-on codebase

## Configuration

**Environment:**
- Runtime configuration is loaded from `test.py` using `.env` if present, with defaults documented in `.env.example`
- Required local paths are read from environment variables such as `COZYSTUDIO_BLENDER_BIN` and `COZYSTUDIO_TEST_DIR`
- Dependency presence is checked at add-on startup in `__init__.py` before registering `auto_load.py`

**Build:**
- Blender extension metadata lives in `blender_manifest.toml`
- Test selection is controlled by markers in `pytest.ini`
- Auto-registration order is derived from class dependencies in `auto_load.py`

## Platform Requirements

**Development:**
- Blender desktop installation with Python access to `bpy`
- Git command-line behavior available through GitPython-backed repository access
- Ability to install Python packages into Blender's interpreter via `sys.executable`

**Production:**
- Blender add-on / extension package installed into Blender's add-on or extensions paths
- Project data stored in a local Git repository rooted at the `.blend` file directory

---

*Stack analysis: 2026-03-21*
