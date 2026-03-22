# Coding Conventions

**Analysis Date:** 2026-03-21

## Naming Patterns

**Files:**
- Module files use short, topic-based names such as `bl_git/ops.py`, `bl_git/merge.py`, `ui/operators.py`, and `tests/integration/test_git_flow.py`.
- Test files use `test_*.py` under `tests/unit/`, `tests/integration/`, and `tests/flow/`.

**Functions:**
- Use `snake_case` for functions and methods, including helpers such as `bl_git/json_io.py::serialize_json_data` and `tests/helpers.py::wait_for_uuid`.
- Prefix internal helpers with `_`, for example `ui/helpers.py::_group_diffs` and `ui/operators.py::_require_git`.
- Use `@staticmethod` for small pure utilities such as `bl_git/merge.py::_group_stage_paths` and `ui/operators.py::_sanitize_branch_name`.

**Classes:**
- Use `PascalCase` for classes.
- Blender operators and panels follow Blender-style prefixes: `COZYSTUDIO_OT_*` in `ui/operators.py` and `COZYSTUDIO_PT_*` in `ui/panels.py`.
- Property containers use descriptive names such as `COZYSTUDIO_CommitItem` in `ui/props.py`.

**Constants:**
- Use `ALL_CAPS` for module constants and manifest keys, as in `bl_git/constants.py` and `ui/operators.py`.

## Code Style

**Formatting:**
- Standard Python formatting is used: 4-space indentation, blank-line separation between top-level definitions, and explicit imports.
- No formatter config is detected in `.prettierrc`, `eslint.config.*`, or `biome.json`; keep edits consistent with nearby files.

**Typing:**
- Type hints are used selectively on public helpers and collection parameters, for example `bl_git/ops.py::stage(self, changes: list[str])` and `ui/helpers.py::_status_abbrev(status: str)`.
- Most code relies on runtime checks rather than full type coverage.

**Data Shape:**
- Structured state is represented with dictionaries returned from methods such as `bl_git/state.py::_empty_ui_state` and `bl_git/ops.py::commit_preflight`.
- Preserve existing key names like `ok`, `errors`, `warnings`, `blockers`, `conflicts`, and `ui_state`.

## Import Organization

**Order:**
1. Standard library imports.
2. Third-party imports such as `bpy`, `git`, and `deepdiff`.
3. Local package imports.

**Path Aliases:**
- No alias system is detected; imports are relative within the package, for example `from ..utils.timers import timers` in `bl_git/__init__.py`.

## Error Handling

**Patterns:**
- Use broad `try/except` blocks around Blender and Git APIs that may fail in runtime contexts, as seen in `bl_git/__init__.py`, `bl_git/bootstrap.py`, and `ui/operators.py`.
- Prefer structured return values over exceptions for user-facing operations. `bl_git/ops.py::commit_preflight` returns a result dictionary, and operators in `ui/operators.py` inspect `result.get("ok")`, `blockers`, and `errors`.
- For operator failures, call `self.report({"ERROR"}, ...)` or `self.report({"WARNING"}, ...)` before returning `{"CANCELLED"}`.
- For debugging and fallback paths, use `print(...)` and `traceback.print_exc()` / `traceback.format_exc()` as in `bl_git/merge.py` and `ui/operators.py`.

**Validation:**
- Validate Blender and Git preconditions before mutating state, especially in `ui/operators.py::_require_git`, `ui/operators.py::_sync_preflight`, and `ui/operators.py::_integration_preflight`.
- Return `None`, `False`, or empty collections when input is missing instead of raising from helper methods.

## Logging

**Framework:**
- Console prints are used instead of a logging framework.

**Patterns:**
- User-facing actions emit short status messages via Blender reports in `ui/operators.py`.
- Internal failures print tagged messages such as `[BpyGit] ...` or `[CozyStudio] ...` in `bl_git/__init__.py`, `bl_git/ops.py`, and the add-on root `__init__.py`.

## Comments

**When to Comment:**
- Use comments for operational context, not for restating code, as in `tests/runner.py` and `bl_git/tracking.py`.
- Keep comments close to special-case Blender or Git behavior.

**JSDoc/TSDoc:**
- Not used. Docstrings appear selectively on modules and a few helpers, for example `tests/runner.py` and `bl_git/bootstrap.py`.

## Function Design

**Size:**
- Prefer small single-purpose helpers. Larger workflows are split across mixins in `bl_git/` and operator classes in `ui/operators.py`.

**Parameters:**
- Pass explicit context values and paths; functions typically accept plain values, repo objects, or lists of relative paths.
- Public methods often accept simple strings such as branch names, refs, and commit hashes.

**Return Values:**
- Return dictionaries for operations that need status, errors, blockers, or conflict payloads.
- Return `{"FINISHED"}` / `{"CANCELLED"}` from Blender operators.

## Module Design

**Exports:**
- Package roots expose a small public surface through `__all__`, such as `bl_git/__init__.py` and `ui/__init__.py`.
- UI package state is re-exported lazily from `ui/__init__.py` via `__getattr__`.

**Barrel Files:**
- `bl_git/__init__.py` re-exports `BpyGit` and JSON helpers.
- `ui/__init__.py` re-exports `register`, `unregister`, and selected state attributes.

## Blender-Specific Patterns

**State:**
- Global add-on state is centralized in `ui/state.py` and `bl_git/__init__.py`.
- Runtime UI state is stored on `BpyGit.ui_state` and refreshed through `bl_git/state.py::refresh_ui_state`.

**Registration:**
- Register properties and handlers in dedicated modules (`ui/registration.py`, `ui/props.py`, and add-on `__init__.py`) instead of inline setup.

---

*Convention analysis: 2026-03-21*
