# Testing Patterns

**Analysis Date:** 2026-03-21

## Test Framework

**Runner:**
- `pytest`.
- Config: `pytest.ini` (`testpaths = tests`, markers defined for `unit`, `integration`, `install`, and `flow`).

**Assertion Library:**
- Native `assert` statements.

**Run Commands:**
```bash
python test.py
```
```bash
pytest tests -m "not install"
```
```bash
pytest tests -m install
```

## Test File Organization

**Location:**
- Unit tests live in `tests/unit/`.
- Blender integration tests live in `tests/integration/`.
- End-to-end flow tests live in `tests/flow/`.
- Shared helpers live in `tests/helpers.py`.

**Naming:**
- Test files use `test_*.py`.
- Test functions use `test_*` and usually describe the scenario in the name, for example `tests/integration/test_merge_rebase.py::test_merge_conflict_marks_manifest`.

**Structure:**
```text
tests/
├── conftest.py
├── helpers.py
├── unit/
├── integration/
└── flow/
```

## Test Structure

**Suite Organization:**
```python
@pytest.mark.order(20)
def test_merge_no_conflict_applies_theirs():
    ui_mod = importlib.import_module(f"{ADDON_MODULE}.ui")
    git_inst = init_git_repo_for_test(ui_mod)
    clear_manifest_conflicts(git_inst)
    ...
    result = bpy.ops.cozystudio.merge("EXEC_DEFAULT", ref_name="feature", strategy="manual")
    assert merge_result.get("ok")
```

**Patterns:**
- Integration tests use Blender fixtures and real add-on registration through `tests/conftest.py` and `tests/helpers.py`.
- Many tests create a temporary Blender project, then call `init_git_repo_for_test(ui_mod)` to normalize repo state.
- Tests assert on both return values and repository contents, especially `.cozystudio/manifest.json` and `.cozystudio/blocks/*.json`.

## Mocking

**Framework:**
- No mocking framework is detected.

**Patterns:**
```python
inst = BpyGit.__new__(BpyGit)
merged, conflict = inst._three_way_merge_json(base, ours, theirs)
```

**What to Mock:**
- Prefer not to mock Blender or Git. Use real `bpy`, temporary directories, and real Git repositories.

**What NOT to Mock:**
- Do not mock `bpy.ops`, repo state, or filesystem writes unless a helper specifically isolates a pure function.

## Fixtures and Helpers

**Test Data:**
```python
def create_test_object(name="CozyTestObject"):
    mesh = bpy.data.meshes.new(name + "Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj
```

**Location:**
- `tests/helpers.py` contains object creation, UUID waits, addon installation, repo initialization, and cleanup helpers.
- `tests/conftest.py` provides session-scoped fixtures: `addon_enabled`, `ui_module`, and `git_repo`.

## Coverage

**Requirements:**
- No coverage threshold is detected.

**View Coverage:**
- Not configured in the repository.

## Test Types

**Unit Tests:**
- Focus on pure helpers and static methods in `bl_git/`.
- Examples: `tests/unit/test_serialization.py`, `tests/unit/test_merge_logic.py`, `tests/unit/test_group_commit.py`, and `tests/unit/test_semantic_diff.py`.

**Integration Tests:**
- Exercise Blender add-on registration, Git repo setup, staging, commit, branch switching, merge, rebase, and conflict resolution.
- Examples: `tests/integration/test_git_flow.py`, `tests/integration/test_merge_rebase.py`, `tests/integration/test_group_stage_commit.py`.

**E2E Tests:**
- `tests/flow/test_flow_scenarios.py` is marked as flow coverage.

## Common Patterns

**Async / Wait Loops:**
```python
start = time.time()
while time.time() - start < timeout:
    git_inst = getattr(ui_mod, "git_instance", None)
    if git_inst is not None:
        return git_inst
    time.sleep(0.1)
```
- Helpers in `tests/helpers.py` poll Blender and file state instead of using event mocks.

**Order Markers:**
- Use `@pytest.mark.order(...)` heavily in `tests/integration/` to enforce scenario sequencing.
- Install-related tests use `@pytest.mark.install` and are separated from the rest by `tests/runner.py`.

**Error Testing:**
- Assert on operator return codes (`"FINISHED"`, `"CANCELLED"`, `"RUNNING_MODAL"`) and on structured payloads from methods like `commit_preflight()`.

**State Cleanup:**
- Clear conflict markers with `tests/helpers.py::clear_manifest_conflicts` and remove temporary branches with `repo.git.branch("-D", ...)`.

## Test Execution Model

**Blender Harness:**
- `test.py` launches Blender in background mode and runs `tests/runner.py`.
- `tests/runner.py` installs missing test dependencies, prepares a clean project directory, and runs `pytest` twice: once for `install` tests and once for the remaining suite.

---

*Testing analysis: 2026-03-21*
