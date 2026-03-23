---
phase: 03-multi-version-blender-test-harness
plan: 02
type: execute
wave: 2
depends_on:
  - 03-multi-version-blender-test-harness-01
files_modified:
  - test.py
  - tests/runner.py
  - .env.example
  - README.md
  - tests/integration/test_blender_matrix.py
autonomous: true
requirements: [TEST-03, TEST-04]
must_haves:
  truths:
    - "The harness still runs when no new selectors are configured"
    - "Users can choose one Blender version or a version matrix from CLI or environment"
    - "Each requested Blender version produces its own result instead of being silently merged"
  artifacts:
    - path: test.py
      provides: "CLI entrypoint that resolves Blender selectors and launches the runner"
    - path: tests/runner.py
      provides: "Blender-side harness execution and per-version dispatch"
    - path: tests/integration/test_blender_matrix.py
      provides: "Selector precedence and matrix-flow coverage"
  key_links:
    - from: test.py
      to: tests/blender_versions.py
      via: "shared selector resolution"
    - from: tests/runner.py
      to: test.py
      via: "propagated version selection and test-dir arguments"
---

<objective>
Wire the test harness to pick Blender versions from CLI or environment, then document and verify the multi-version workflow.

Purpose: This turns the version contract into a usable local workflow without breaking the existing single-version path.
Output: Updated entrypoints, documented cache/selector settings, and integration coverage for matrix selection.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/03-multi-version-blender-test-harness/03-RESEARCH.md
@.planning/phases/03-multi-version-blender-test-harness/03-multi-version-blender-test-harness-01-PLAN.md
@test.py
@tests/runner.py
@.env.example
@README.md

<interfaces>
From `test.py`:
```python
def load_env(env_path: Path):
def read_env(primary: str, default: str) -> str:
def main():
```

From `tests/runner.py`:
```python
def ensure_pytest_installed():
def parse_requirements(path: Path):
def disable_addon(name: str):
def remove_existing_addons(name: str):
def sanitize_target_directory(target: Path):
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add Blender version selectors to the harness entrypoint</name>
  <files>test.py, tests/runner.py</files>
  <read_first>
    - test.py
    - tests/runner.py
    - tests/blender_versions.py
    - .planning/phases/03-multi-version-blender-test-harness/03-multi-version-blender-test-harness-01-PLAN.md
  </read_first>
  <behavior>
    - Test that `GITBLOCKS_BLENDER_BIN` still wins when it is set
    - Test that `--blender-version 5.1.0` resolves through the shared helper when no direct binary override exists
    - Test that `--blender-versions 5.0.1,5.1.0` expands to a matrix instead of one run
    - Test that no selector changes the current single-binary fallback path
  </behavior>
  <action>Refactor `test.py` to parse `--blender-version` and `--blender-versions`, then route both the single-run and matrix-run cases through `tests/blender_versions.py`. Keep `GITBLOCKS_BLENDER_BIN` as the strongest override, but let version selectors resolve into cached binaries when no explicit path is provided. Update `tests/runner.py` so the selected version or version list reaches the Blender-side launch path and each run gets the correct target directory.</action>
  <acceptance_criteria>
    - `python3 test.py --help` shows the new Blender version flags
    - Existing `GITBLOCKS_BLENDER_BIN` behavior is unchanged
    - Matrix selection produces one run per requested version
  </acceptance_criteria>
  <verify>python3 -m pytest tests/integration/test_blender_matrix.py -q</verify>
  <done>The harness can choose a version or matrix without losing the old path-based override.</done>
</task>

<task type="auto">
  <name>Task 2: Document the cache and version workflow</name>
  <files>.env.example, README.md</files>
  <read_first>
    - .env.example
    - README.md
    - test.py
    - .planning/phases/03-multi-version-blender-test-harness/03-RESEARCH.md
  </read_first>
  <action>Update the example env file and the user-facing README so the new workflow is obvious: document `GITBLOCKS_BLENDER_CACHE_DIR`, `GITBLOCKS_BLENDER_VERSION`, and `GITBLOCKS_BLENDER_VERSIONS`; show a single-version command and a version-matrix command; and explain that Blender archives come from the official `download.blender.org/release/` archive.</action>
  <acceptance_criteria>
    - `.env.example` contains the new cache and selector env vars
    - `README.md` contains one single-version example and one multi-version example
    - The docs still mention `GITBLOCKS_BLENDER_BIN` as the direct fallback
  </acceptance_criteria>
  <verify>grep -n "GITBLOCKS_BLENDER_CACHE_DIR\|GITBLOCKS_BLENDER_VERSION\|GITBLOCKS_BLENDER_VERSIONS\|download.blender.org/release" .env.example README.md</verify>
  <done>The workflow is documented for people who need to add or select Blender versions locally.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Add matrix integration coverage and smoke verification</name>
  <files>tests/integration/test_blender_matrix.py</files>
  <read_first>
    - test.py
    - tests/runner.py
    - tests/blender_versions.py
    - .planning/phases/03-multi-version-blender-test-harness/03-multi-version-blender-test-harness-01-PLAN.md
    - .planning/phases/03-multi-version-blender-test-harness/03-multi-version-blender-test-harness-02-PLAN.md
  </read_first>
  <behavior>
    - Test selector precedence from env and CLI
    - Test that the default path still works when no selectors are present
    - Test that a matrix request produces one expected launch record per version
  </behavior>
  <action>Create `tests/integration/test_blender_matrix.py` so the harness has coverage for selector precedence, fallback behavior, and matrix dispatch. Keep the assertions focused on the command-building logic and the handoff between `test.py` and `tests/runner.py`; do not require an actual Blender download for the test to pass.</action>
  <acceptance_criteria>
    - The matrix test file covers env precedence, CLI precedence, and fallback behavior
    - The tests do not require network access or a live Blender archive during CI-style verification
    - Selector bugs fail the new test file before they can reach the runner
  </acceptance_criteria>
  <verify>python3 -m pytest tests/integration/test_blender_matrix.py -q</verify>
  <done>The harness has regression coverage for single-version and multi-version dispatch.</done>
</task>

</tasks>

<verification>
- `pytest` passes for the resolver unit tests and the matrix integration test.
- `grep` confirms the docs expose the new cache and selector env vars.
- The old single-path harness still works when no new selector is configured.
</verification>

<success_criteria>
- Users can download and cache multiple Blender versions from the official archive.
- The harness can target a specific Blender version or a version matrix without editing source code.
- Existing `GITBLOCKS_BLENDER_BIN` workflows still work unchanged.
</success_criteria>

<output>
After completion, create `.planning/phases/03-multi-version-blender-test-harness/03-multi-version-blender-test-harness-02-SUMMARY.md`
</output>
