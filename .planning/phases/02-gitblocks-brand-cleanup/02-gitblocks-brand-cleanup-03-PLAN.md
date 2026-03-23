---
phase: 02-gitblocks-brand-cleanup
plan: 03
type: execute
wave: 3
depends_on:
  - 02-gitblocks-brand-cleanup-01
  - 02-gitblocks-brand-cleanup-02
files_modified:
  - tests/conftest.py
  - tests/helpers.py
  - tests/runner.py
  - tests/integration/test_ui_registration.py
  - tests/integration/test_addon_enable.py
  - tests/integration/test_git_init.py
  - tests/integration/test_git_flow.py
  - tests/integration/test_group_stage_commit.py
  - tests/integration/test_grouping.py
  - tests/integration/test_install_deps_operator.py
  - tests/integration/test_merge_rebase.py
  - tests/integration/test_mode_sensitive_commit.py
  - tests/integration/test_zip_install.py
  - tests/flow/test_flow_scenarios.py
  - tests/unit/test_group_commit.py
  - tests/unit/test_merge_logic.py
  - tests/unit/test_semantic_diff.py
  - tests/unit/test_serialization.py
autonomous: true
requirements:
  - BRAND-06
  - BRAND-07
must_haves:
  truths:
    - "Test fixtures import the GitBlocks addon module and enable it successfully"
    - "Integration and flow tests assert GitBlocks operator namespaces, paths, and labels"
    - "Unit tests expect the renamed identifiers and storage behavior"
  artifacts:
    - path: "tests/conftest.py"
      provides: "GitBlocks addon module fixture"
      contains: "ADDON_MODULE = \"gitblocks_addon\""
    - path: "tests/helpers.py"
      provides: "Test repo and UUID helpers"
      contains: "gitblocks_uuid"
    - path: "tests/runner.py"
      provides: "Blender-backed test harness"
      contains: "GitBlocks test environment"
  key_links:
    - from: "tests/helpers.py"
      to: "bl_types/bl_datablock.py"
      via: "UUID lookup helpers"
      pattern: "gitblocks_uuid"
    - from: "tests/runner.py"
      to: "addon package install"
      via: "extension copy + enable flow"
      pattern: "gitblocks_addon"
---

<objective>
Update the test suite and Blender harness to match the renamed GitBlocks identifiers everywhere the user or automation can observe them.

Purpose: the cleanup is only real if the tests and harness enforce the new naming contract.
Output: updated test fixtures, integration tests, unit tests, and runner expectations.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@tests/conftest.py
@tests/helpers.py
@tests/runner.py
@tests/integration/test_ui_registration.py
@tests/integration/test_addon_enable.py
@tests/integration/test_git_init.py
@tests/integration/test_git_flow.py
@tests/integration/test_group_stage_commit.py
@tests/integration/test_grouping.py
@tests/integration/test_install_deps_operator.py
@tests/integration/test_merge_rebase.py
@tests/integration/test_mode_sensitive_commit.py
@tests/integration/test_zip_install.py
@tests/flow/test_flow_scenarios.py
@tests/unit/test_group_commit.py
@tests/unit/test_merge_logic.py
@tests/unit/test_semantic_diff.py
@tests/unit/test_serialization.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Repoint fixtures and the Blender test harness</name>
  <read_first>
    - tests/conftest.py
    - tests/helpers.py
    - tests/runner.py
  </read_first>
  <files>tests/conftest.py, tests/helpers.py, tests/runner.py</files>
  <action>Rename the addon module and helper constants to GitBlocks names, update the Blender test harness to install and copy the GitBlocks package, and replace any legacy UUID helper access with the renamed field. Keep the test environment bootstrapping behavior identical aside from the brand rename.</action>
  <acceptance_criteria>
    - conftest.py imports the GitBlocks addon module name.
    - runner.py installs and copies the GitBlocks addon package name.
    - helpers.py resolves datablock UUIDs using the renamed field.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "cozystudio_addon|cozystudio_uuid|cozystudio|Cozy Studio|COZYSTUDIO" tests/conftest.py tests/helpers.py tests/runner.py</automated>
  </verify>
  <done>The shared test harness only knows GitBlocks names.</done>
</task>

<task type="auto">
  <name>Task 2: Update integration and flow suites</name>
  <read_first>
    - tests/integration/test_ui_registration.py
    - tests/integration/test_addon_enable.py
    - tests/integration/test_git_init.py
    - tests/integration/test_git_flow.py
    - tests/integration/test_group_stage_commit.py
    - tests/integration/test_grouping.py
    - tests/integration/test_install_deps_operator.py
    - tests/integration/test_merge_rebase.py
    - tests/integration/test_mode_sensitive_commit.py
    - tests/integration/test_zip_install.py
    - tests/flow/test_flow_scenarios.py
  </read_first>
  <files>tests/integration/test_ui_registration.py, tests/integration/test_addon_enable.py, tests/integration/test_git_init.py, tests/integration/test_git_flow.py, tests/integration/test_group_stage_commit.py, tests/integration/test_grouping.py, tests/integration/test_install_deps_operator.py, tests/integration/test_merge_rebase.py, tests/integration/test_mode_sensitive_commit.py, tests/integration/test_zip_install.py, tests/flow/test_flow_scenarios.py</files>
  <action>Replace every legacy addon, operator, property, and path expectation with GitBlocks names. Keep the same behavior coverage, but rewrite the assertions so they validate the renamed operator namespace, renamed storage helpers, and GitBlocks-branded UI text.</action>
  <acceptance_criteria>
    - All integration and flow tests import and call GitBlocks names.
    - Assertions no longer reference the legacy addon module or operator namespace.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "cozystudio_addon|bpy\.ops\.cozystudio|cozystudio_uuid|\.cozystudio|Cozy Studio|cozystudio" tests/integration tests/flow</automated>
  </verify>
  <done>The behavior coverage is aligned to the renamed runtime contract.</done>
</task>

<task type="auto">
  <name>Task 3: Update unit expectations for renamed identifiers</name>
  <read_first>
    - tests/unit/test_group_commit.py
    - tests/unit/test_merge_logic.py
    - tests/unit/test_semantic_diff.py
    - tests/unit/test_serialization.py
  </read_first>
  <files>tests/unit/test_group_commit.py, tests/unit/test_merge_logic.py, tests/unit/test_semantic_diff.py, tests/unit/test_serialization.py</files>
  <action>Switch the unit tests to import the renamed package symbols and assert the GitBlocks-only identifier fields and storage layout. Keep the business expectations identical; only the brand and namespace assertions should change.</action>
  <acceptance_criteria>
    - Unit tests import the renamed addon/package modules.
    - Serialization and merge tests assert the renamed identifier fields.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "cozystudio_addon|cozystudio_uuid|cozystudio|\.cozystudio|Cozy Studio|COZYSTUDIO" tests/unit</automated>
  </verify>
  <done>The unit suite no longer expects legacy brand identifiers.</done>
</task>

</tasks>

<verification>
Run the focused pytest subset and confirm the test tree itself contains no legacy brand strings.
</verification>

<success_criteria>
- The test harness and fixtures import the GitBlocks package names.
- Integration/flow/unit suites assert GitBlocks-only identifiers.
- The test tree has no remaining legacy brand references.
</success_criteria>

<output>
After completion, create `.planning/phases/02-gitblocks-brand-cleanup/02-gitblocks-brand-cleanup-03-SUMMARY.md`
</output>
