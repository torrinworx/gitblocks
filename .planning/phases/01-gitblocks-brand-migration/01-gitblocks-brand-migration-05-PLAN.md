---
phase: 01-gitblocks-brand-migration
plan: 05
type: execute
wave: 4
depends_on:
  - 01-gitblocks-brand-migration-03
files_modified:
  - tests/conftest.py
  - tests/helpers.py
  - tests/integration/test_addon_enable.py
  - tests/integration/test_git_init.py
  - tests/integration/test_git_flow.py
  - tests/integration/test_group_stage_commit.py
  - tests/integration/test_grouping.py
  - tests/integration/test_install_deps_operator.py
  - tests/integration/test_merge_rebase.py
  - tests/integration/test_mode_sensitive_commit.py
  - tests/integration/test_ui_registration.py
  - tests/integration/test_zip_install.py
  - tests/flow/test_flow_scenarios.py
  - tests/unit/test_group_commit.py
  - tests/unit/test_merge_logic.py
  - tests/unit/test_semantic_diff.py
  - tests/unit/test_serialization.py
autonomous: true
requirements:
  - BRAND-05
must_haves:
  truths:
    - "Tests assert the GitBlocks brand contract instead of Cozy Studio copy"
    - "Approved compatibility aliases remain covered"
    - "A final grep/test sweep proves the migration is clean"
  artifacts:
    - path: "tests/integration/test_ui_registration.py"
      provides: "GitBlocks UI registration expectations"
    - path: "tests/helpers.py"
      provides: "GitBlocks path assertions and repo setup helpers"
  key_links:
    - from: "tests"
      to: "runtime brand contract"
      via: "assertions and fixtures"
      pattern: "GitBlocks|\.gitblocks|compatibility alias"
---

<objective>
Update the test suite to expect GitBlocks branding, then prove the repo only keeps the legacy names that the compatibility policy explicitly allows.

Purpose: a brand migration is only real if the automated checks and fixtures agree with it.
Output: updated test expectations plus a clean verification sweep.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-CONTEXT.md
@.planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-03-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Update fixtures and helper assertions</name>
  <read_first>
    - tests/conftest.py
    - tests/helpers.py
    - tests/integration/test_ui_registration.py
    - tests/integration/test_git_init.py
  </read_first>
  <files>tests/conftest.py, tests/helpers.py, tests/integration/test_ui_registration.py, tests/integration/test_git_init.py</files>
  <action>Adjust the shared test fixtures and helper assertions so they check GitBlocks-branded UI text, GitBlocks-oriented working paths, and the approved legacy compatibility aliases. Keep the fixture logic itself unchanged unless it hard-codes a brand string.</action>
  <acceptance_criteria>
    - Helper assertions expect GitBlocks paths and labels.
    - UI registration tests check the new panel identifiers and copy.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "cozystudio_addon|Cozy Studio|cozystudio|\.cozystudio|GitBlocks|gitblocks" tests/conftest.py tests/helpers.py tests/integration/test_ui_registration.py tests/integration/test_git_init.py</automated>
  </verify>
  <done>Shared fixtures understand the new brand.</done>
</task>

<task type="auto">
  <name>Task 2: Update flow and integration expectations</name>
  <read_first>
    - tests/integration/test_git_flow.py
    - tests/integration/test_group_stage_commit.py
    - tests/integration/test_grouping.py
    - tests/integration/test_install_deps_operator.py
    - tests/integration/test_merge_rebase.py
    - tests/integration/test_mode_sensitive_commit.py
    - tests/integration/test_zip_install.py
    - tests/flow/test_flow_scenarios.py
  </read_first>
  <files>tests/integration/test_git_flow.py, tests/integration/test_group_stage_commit.py, tests/integration/test_grouping.py, tests/integration/test_install_deps_operator.py, tests/integration/test_merge_rebase.py, tests/integration/test_mode_sensitive_commit.py, tests/integration/test_zip_install.py, tests/flow/test_flow_scenarios.py, tests/unit/test_group_commit.py, tests/unit/test_merge_logic.py, tests/unit/test_semantic_diff.py, tests/unit/test_serialization.py</files>
  <action>Update the expectation strings and path assertions that still mention Cozy Studio or `.cozystudio`. Keep the assertions focused on behavior: GitBlocks-branded copy should pass, and the explicit compatibility aliases documented in research should still be accepted where the saved data path requires them.</action>
  <acceptance_criteria>
    - Flow and integration tests assert the GitBlocks brand where the user sees it.
    - Path assertions reference the canonical `.gitblocks` namespace or the documented compatibility fallback.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "Cozy Studio|cozystudio|\.cozystudio|GitBlocks|gitblocks" tests/integration tests/flow tests/unit</automated>
  </verify>
  <done>The automated test suite matches the new brand policy.</done>
</task>

<task type="auto">
  <name>Task 3: Run the final verification sweep</name>
  <read_first>
    - tests/conftest.py
    - tests/helpers.py
    - tests/integration/test_ui_registration.py
    - .planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-04-SUMMARY.md
  </read_first>
  <files>tests/conftest.py, tests/helpers.py, tests/integration/test_ui_registration.py, tests/integration/test_git_init.py, tests/integration/test_git_flow.py, tests/integration/test_group_stage_commit.py, tests/integration/test_grouping.py, tests/integration/test_install_deps_operator.py, tests/integration/test_merge_rebase.py, tests/integration/test_mode_sensitive_commit.py, tests/integration/test_zip_install.py, tests/flow/test_flow_scenarios.py, tests/unit/test_group_commit.py, tests/unit/test_merge_logic.py, tests/unit/test_semantic_diff.py, tests/unit/test_serialization.py</files>
  <action>Run the focused test set and a repo-wide grep sweep. The goal is to prove that only intentional compatibility aliases remain: GitBlocks should be the public brand, `.gitblocks` should be the canonical storage namespace, and any `cozystudio` references left behind must be justified in the research doc.</action>
  <acceptance_criteria>
    - The chosen pytest subset passes.
    - The grep sweep only finds legacy names that the research doc explicitly blesses as compatibility aliases.
  </acceptance_criteria>
  <verify>
    <automated>python -m pytest tests/integration/test_ui_registration.py tests/integration/test_git_init.py tests/integration/test_git_flow.py tests/integration/test_merge_rebase.py -q</automated>
  </verify>
  <done>The brand migration is proven by tests and grep.</done>
</task>

</tasks>

<verification>
Require two things before calling the phase done: the targeted pytest subset passes, and a repo-wide grep only shows intentional legacy aliases.
</verification>

<success_criteria>
- The test suite encodes the GitBlocks brand contract.
- The final grep sweep shows only approved compatibility holdouts.
- The phase can ship without another manual search for brand strings.
</success_criteria>

<output>
After completion, create `.planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-05-SUMMARY.md`
</output>
