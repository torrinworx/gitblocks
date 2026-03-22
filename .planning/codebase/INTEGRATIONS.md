# External Integrations

**Analysis Date:** 2026-03-21

## APIs & External Services

**Blender API:**
- Blender `bpy` - Add-on registration, UI panels, operators, timers, handlers, properties, and file ops across `__init__.py`, `ui/`, `bl_git/`, and `bl_types/`
  - SDK/Client: `bpy`
  - Auth: not applicable

**Git:**
- Git repositories - Full repo lifecycle, commits, branches, merges, rebases, stash, fetch, reflog, and object reads in `bl_git/__init__.py`, `bl_git/ops.py`, `bl_git/checkout.py`, `bl_git/merge.py`, and `ui/operators.py`
  - SDK/Client: `GitPython` (`git.Repo`)
  - Auth: local repository access; remote authentication handled by the user's Git configuration outside this codebase

**Python package installation:**
- PyPI / pip - Dependency bootstrap for add-on runtime in `__init__.py` and test bootstrap in `tests/runner.py`
  - SDK/Client: `subprocess` + `sys.executable -m pip`
  - Auth: not applicable

## Data Storage

**Databases:**
- None detected

**File Storage:**
- Local filesystem - Project state is stored under `.cozystudio/manifest.json` and `.cozystudio/blocks/*.json` in the project root resolved from `bpy.path.abspath("//")` in `bl_git/__init__.py`
- Bootstrap `.blend` copy - Created by `bl_git/bootstrap.py` with `bpy.ops.wm.save_as_mainfile(..., copy=True)`

**Caching:**
- In-memory state only - UI state and tracked datablock metadata live on `BpyGit.ui_state` and module globals in `ui/state.py`

## Authentication & Identity

**Auth Provider:**
- None detected
  - Implementation: Git remote operations rely on the user's existing Git credential configuration; no in-app login flow is present

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logs:**
- Console prints and Blender operator reports are used for status and errors in `__init__.py`, `bl_git/`, and `ui/operators.py`

## CI/CD & Deployment

**Hosting:**
- Blender extension/add-on distribution; install paths are exercised in `tests/integration/test_zip_install.py` and `tests/runner.py`

**CI Pipeline:**
- None detected in-repo

## Environment Configuration

**Required env vars:**
- `COZYSTUDIO_BLENDER_BIN` - Blender executable path used by `test.py`
- `COZYSTUDIO_TEST_DIR` - Temporary test directory used by `test.py`
- `COZYSTUDIO_KEEP_TEST_DIR` - Present in `.env.example`; consumed by the test harness only if set

**Secrets location:**
- None detected

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

## Blender-Hosted Integration Points

- Add-on lifecycle: `__init__.py`, `ui/registration.py`, `auto_load.py`
- Timed polling: `ui/state.py`, `utils/timers.py`
- UI refresh triggers: `utils/redraw.py` and redraw calls from `bl_git/ops.py`, `bl_git/checkout.py`, and `bl_git/merge.py`
- Preference/extension install flow: `__init__.py`, `tests/integration/test_install_deps_operator.py`, and `tests/integration/test_zip_install.py`

---

*Integration audit: 2026-03-21*
