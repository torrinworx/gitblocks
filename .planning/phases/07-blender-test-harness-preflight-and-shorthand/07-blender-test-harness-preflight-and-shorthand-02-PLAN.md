---
phase: 07-blender-test-harness-preflight-and-shorthand
plan: 02
type: execute
wave: 2
depends_on:
  - 07-blender-test-harness-preflight-and-shorthand-01
files_modified:
  - test.py
  - tests/runner.py
  - tests/unit/test_test_entrypoint.py
  - tests/unit/test_runner_selection.py
  - README.md
  - .env.example
autonomous: true
requirements: [TEST-11, TEST-12]
must_haves:
  truths:
    - "Unsupported Blender selections fail before any Blender subprocess starts."
    - "A shorthand test selector can be provided from CLI or env and reaches the inner pytest -k filter."
    - "Supported version selection still launches the same Blender matrix as before."
    - "README and .env.example show the new preflight and shorthand usage."
  artifacts:
    - path: test.py
      provides: "Outer harness preflight gate plus shorthand forwarding into Blender command construction"
      min_lines: 380
    - path: tests/runner.py
      provides: "Inner harness parser support for a single-test shorthand and pytest -k forwarding"
      min_lines: 360
    - path: tests/unit/test_test_entrypoint.py
      provides: "Outer-harness coverage for the compatibility gate and forwarded shorthand selector"
      min_lines: 260
    - path: tests/unit/test_runner_selection.py
      provides: "Parser and selection coverage for the new shorthand argument"
      min_lines: 80
    - path: README.md
      provides: "User-facing command examples for preflight and single-test shorthand"
      min_lines: 50
    - path: .env.example
      provides: "Environment examples for the supported Blender matrix and test filter"
      min_lines: 10
  key_links:
    - from: test.py
      to: tests/blender_versions.py
      via: "compatibility preflight before any run planning"
      pattern: "check_blender_compatibility"
    - from: test.py
      to: tests/runner.py
      via: "forwarded `--test` selector"
      pattern: "--test|GITBLOCKS_TEST_FILTER"
    - from: tests/runner.py
      to: pytest.main
      via: "`-k` filter for the selected single-test shorthand"
      pattern: "-k"
---

<objective>
Wire the compatibility gate into the outer harness, add a single-test shorthand that reaches the inner pytest run, and document both flows.

Purpose: This keeps unsupported Blender versions from wasting time and makes it easy to target one test without editing command lines.
Output: Updated harness plumbing in `test.py` and `tests/runner.py`, plus unit tests and docs that pin the new CLI/env behavior.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.env.example
@README.md
@.planning/phases/07-blender-test-harness-preflight-and-shorthand/07-blender-test-harness-preflight-and-shorthand-01-PLAN.md

<interfaces>
From `test.py`:

```python
@dataclass(frozen=True)
class BlenderRun:
    blender_bin: Path
    test_dir: Path
    version: str | None = None

def plan_blender_runs(argv: list[str], *, addon_root: Path, env: dict[str, str] | None = None, resolver=ensure_installed, progress=None) -> list[BlenderRun]
def build_blender_command(addon_root: Path, run: BlenderRun, log_file: Path | None = None) -> list[str]
def render_run_header(run: BlenderRun) -> str
def main()
```

From `tests/runner.py`:

```python
def build_parser()
def parse_runner_args(argv: list[str] | None = None)
def run_pytest_phase(tests_dir: Path, stage: str, extra_args: list[str] | None = None, current_version: str | None = None, current_run_index: int = 1, run_count: int = 1, log_file: Path | None = None)
def main(argv: list[str] | None = None)
```

From `tests/unit/test_runner_selection.py`:

```python
def test_runner_parses_version_argument()
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add the outer-harness preflight gate and CLI plumbing</name>
  <files>test.py, tests/unit/test_test_entrypoint.py</files>
  <read_first>
    - test.py
    - tests/unit/test_test_entrypoint.py
    - tests/blender_versions.py
    - .planning/phases/07-blender-test-harness-preflight-and-shorthand/07-blender-test-harness-preflight-and-shorthand-01-PLAN.md
    - .env.example
    - README.md
  </read_first>
  <behavior>
    - Test 1: supported version selections still produce the same `BlenderRun` list and command construction as before.
    - Test 2: unsupported version selections print `GitBlocks compatibility preflight failed:` plus the helper message and exit before any Blender subprocess starts.
    - Test 3: a `--test commit_preflight` CLI value or `GITBLOCKS_TEST_FILTER=commit_preflight` env value is threaded onto the Blender command while `GITBLOCKS_BLENDER_BIN` still wins as the direct override.
  </behavior>
  <action>
    Extend `test.py` so it reads a shorthand test selector from `--test` and `GITBLOCKS_TEST_FILTER`, preserves the current version-selection logic, and calls `check_blender_compatibility(...)` before the matrix starts whenever the run is not using a direct `GITBLOCKS_BLENDER_BIN` override. If the compatibility result is not `ok`, print the helper message verbatim under a `GitBlocks compatibility preflight failed:` prefix and `sys.exit(1)` before any Blender subprocess launches.
  </action>
  <acceptance_criteria>
    - `test.py` imports and uses `check_blender_compatibility` before launching Blender.
    - The preflight failure path exits before `subprocess.call` runs.
    - The outer harness command builder carries the single-test shorthand through to the Blender invocation.
  </acceptance_criteria>
  <verify>
    <automated>python -m pytest tests/unit/test_test_entrypoint.py -q</automated>
  </verify>
  <done>The outer harness now blocks unsupported Blender selections early and can forward a shorthand test selector without changing the current matrix behavior.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Forward the shorthand selector inside Blender</name>
  <files>tests/runner.py, tests/unit/test_runner_selection.py</files>
  <read_first>
    - tests/runner.py
    - tests/unit/test_runner_selection.py
    - test.py
    - .planning/phases/07-blender-test-harness-preflight-and-shorthand/07-blender-test-harness-preflight-and-shorthand-02-PLAN.md
  </read_first>
  <behavior>
    - Test 1: `tests.runner.build_parser()` must accept `--test commit_preflight`.
    - Test 2: the install phase must remain untouched by the shorthand selector.
    - Test 3: the `not install` pytest phase must receive `-k commit_preflight` while preserving the version-specific target directory rules.
  </behavior>
  <action>
    Teach `tests/runner.py` to accept a `--test` expression, keep the install phase unchanged, and pass `-k <expression>` only to the `not install` phase. Preserve the existing `--blender-version` behavior and the version-specific target-directory logic in `select_target_directory(...)`.
  </action>
  <acceptance_criteria>
    - The runner parser exposes `--test` in its help text.
    - The install phase does not receive the shorthand filter.
    - The test phase passes `-k commit_preflight` to pytest when the shorthand is present.
  </acceptance_criteria>
  <verify>
    <automated>python -m pytest tests/unit/test_runner_selection.py -q</automated>
  </verify>
  <done>The inner harness can now target a single test via a shorthand selector without changing the install phase.</done>
</task>

<task type="auto">
  <name>Task 3: Refresh the docs and env examples</name>
  <files>README.md, .env.example</files>
  <read_first>
    - README.md
    - .env.example
    - test.py
    - tests/runner.py
  </read_first>
  <action>
    Update the Blender harness section so the supported matrix matches `4.1.0,4.5.1,5.1.0`, add a `GITBLOCKS_TEST_FILTER=commit_preflight` example, and describe that unsupported Blender selections fail fast before the matrix starts. Keep the existing `GITBLOCKS_BLENDER_BIN` override guidance intact.
  </action>
  <acceptance_criteria>
    - README.md mentions the supported matrix `4.1.0,4.5.1,5.1.0`.
    - README.md mentions `GITBLOCKS_TEST_FILTER` and the single-test shorthand.
    - .env.example includes the same supported matrix and a test-filter example.
  </acceptance_criteria>
  <verify>
    <automated>grep -n "4.1.0,4.5.1,5.1.0\|GITBLOCKS_TEST_FILTER\|fail fast" README.md .env.example</automated>
  </verify>
  <done>The user-facing docs and examples match the new compatibility gate and shorthand selector.</done>
</task>

</tasks>

<verification>
Run the compatibility unit tests, the harness-selection tests, and a quick docs grep to confirm the new examples and failure wording landed together.
</verification>

<success_criteria>
- `test.py` blocks unsupported Blender selections before any subprocess launches.
- `tests/runner.py` accepts a shorthand test selector and forwards it only to the test phase.
- `README.md` and `.env.example` show the updated matrix and filter examples.
</success_criteria>

<output>
After completion, create `.planning/phases/07-blender-test-harness-preflight-and-shorthand/07-blender-test-harness-preflight-and-shorthand-SUMMARY.md`
</output>
