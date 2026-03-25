---
phase: 260324-twt-investigate-why-the-test-system-creates-
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - test.py
  - tests/runner.py
  - tests/unit/test_test_entrypoint.py
autonomous: true
requirements:
  - TEST-09
  - TEST-10
must_haves:
  truths:
    - "Running the harness no longer creates gitblocks-test-summary.json"
    - "The outer runner still reports per-version results and overall exit code"
    - "The Blender-side runner still emits live TUI output and logs without JSON aggregation"
  artifacts:
    - path: "test.py"
      provides: "Outer harness execution and final reporting"
      contains: "no summary_path_for_run/load_run_summary path"
    - path: "tests/runner.py"
      provides: "Blender-side pytest execution"
      contains: "no write_run_summary/SUMMARY_FILENAME path"
    - path: "tests/unit/test_test_entrypoint.py"
      provides: "Harness behavior coverage"
      contains: "no SUMMARY_FILENAME assertions"
  key_links:
    - from: "test.py"
      to: "tests/runner.py"
      via: "subprocess call + exit code only"
      pattern: "subprocess\.call\(|sys\.exit\(overall_exit_code\)"
    - from: "tests/runner.py"
      to: "stdout/log file"
      via: "live TUI output and timestamped logs"
      pattern: "run_pytest_phase\(|log_file"
---

<objective>
Remove the file-backed `gitblocks-test-summary.json` aggregation layer from the test harness while keeping the existing test execution, logging, and readable console output intact.

Purpose: eliminate a redundant artifact and the coupling between the outer harness and Blender-side runner.
Output: updated harness code plus tests that prove the summary file is gone.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/PROJECT.md
@test.py
@tests/runner.py
@tests/unit/test_test_entrypoint.py
@tests/unit/test_runner_tui.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Remove summary-file plumbing from the harness</name>
  <files>test.py, tests/runner.py</files>
  <action>Delete the `SUMMARY_FILENAME` / summary JSON write-read path entirely: remove `summary_path_for_run`, `load_run_summary`, and `write_run_summary`, drop the `summary_path.unlink(...)` and summary parsing in `main`, and ensure the outer harness now relies only on subprocess exit codes and live stdout/log output. Keep the existing matrix execution, version headers, and log-file behavior unchanged; do not replace the JSON file with another artifact.</action>
  <verify><automated>python -m py_compile test.py tests/runner.py</automated></verify>
  <done>No code path in the harness creates, deletes, or reads `gitblocks-test-summary.json`.</done>
</task>

<task type="auto">
  <name>Task 2: Update tests to match the fileless harness</name>
  <files>tests/unit/test_test_entrypoint.py</files>
  <action>Rewrite the entrypoint coverage so it asserts the harness still prints per-version headers, keeps the final exit code behavior, and forwards log/test selection without depending on any summary file. Remove the old `SUMMARY_FILENAME` fixtures and JSON payload assertions; add explicit coverage that the no-selector and single-version flows still work after the summary layer is gone.</action>
  <verify><automated>pytest tests/unit/test_test_entrypoint.py tests/unit/test_runner_tui.py -q</automated></verify>
  <done>The unit suite passes without any `gitblocks-test-summary.json` assertions or dependencies.</done>
</task>

</tasks>

<verification>
- No `gitblocks-test-summary.json` artifact is produced anywhere in the harness flow.
- The outer runner still exits based on the Blender subprocess result.
- Existing TUI/log output remains readable and test-covered.
</verification>

<success_criteria>
- The harness no longer uses a JSON summary file between `test.py` and `tests/runner.py`.
- The updated tests pass and prove the summary feature is removed.
- The plan stays self-contained with no new checkpoints.
</success_criteria>

<output>
After completion, create `.planning/quick/260324-twt-investigate-why-the-test-system-creates-/260324-twt-SUMMARY.md`
</output>
