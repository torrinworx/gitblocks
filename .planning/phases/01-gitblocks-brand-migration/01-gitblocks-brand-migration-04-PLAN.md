---
phase: 01-gitblocks-brand-migration
plan: 04
type: execute
wave: 4
depends_on:
  - 01-gitblocks-brand-migration-03
files_modified:
  - README.md
  - bl_types/README.md
  - .env.example
  - test.py
  - tests/runner.py
autonomous: true
requirements:
  - BRAND-05
must_haves:
  truths:
    - "The public docs describe the add-on as GitBlocks"
    - "The local test harness asks for GitBlocks-named env vars"
    - "Doc copy no longer teaches Cozy Studio branding"
  artifacts:
    - path: "README.md"
      provides: "GitBlocks product copy"
    - path: ".env.example"
      provides: "GitBlocks-named local test env vars"
    - path: "tests/runner.py"
      provides: "GitBlocks test runner banner and usage text"
  key_links:
    - from: "README.md"
      to: "GitBlocks brand contract"
      via: "public-facing documentation"
      pattern: "GitBlocks|gitblocks"
---

<objective>
Update the public docs and test harness copy so the project reads as GitBlocks everywhere a developer or user would look first.

Purpose: docs and local scripts are the quickest place to feel the rebrand, and they must match the runtime UI so the migration feels complete.
Output: updated README copy, updated harness scripts, and GitBlocks-named env examples.
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
  <name>Task 1: Rebrand the public docs</name>
  <read_first>
    - README.md
    - bl_types/README.md
    - .planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-CONTEXT.md
  </read_first>
  <files>README.md, bl_types/README.md</files>
  <action>Rewrite the README and the `bl_types` README so the product name, feature descriptions, and usage examples read as GitBlocks. Keep any historical references only where they help explain compatibility or provenance.</action>
  <acceptance_criteria>
    - The main README headline and product copy say GitBlocks.
    - The `bl_types` README no longer frames Cozy Studio as the primary brand.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "Cozy Studio|cozystudio|GitBlocks|gitblocks" README.md bl_types/README.md</automated>
  </verify>
  <done>Public-facing docs are rebranded.</done>
</task>

<task type="auto">
  <name>Task 2: Rename the local harness copy to GitBlocks</name>
  <read_first>
    - .env.example
    - test.py
    - tests/runner.py
  </read_first>
  <files>.env.example, test.py, tests/runner.py</files>
  <action>Change the local test harness to prefer `GITBLOCKS_BLENDER_BIN`, `GITBLOCKS_TEST_DIR`, and GitBlocks-oriented messages. Keep the old `COZYSTUDIO_*` names as fallbacks if the compatibility policy from research says they are still needed, but make the docs and prompts lead with GitBlocks.</action>
  <acceptance_criteria>
    - `.env.example` advertises GitBlocks-named env vars first.
    - `test.py` and `tests/runner.py` print GitBlocks-oriented messages.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "COZYSTUDIO_|GITBLOCKS_|cozystudio_addon|GitBlocks|gitblocks" .env.example test.py tests/runner.py</automated>
  </verify>
  <done>The local harness copy matches the new brand.</done>
</task>

</tasks>

<verification>
Confirm the docs and harness read like GitBlocks tooling, and that any remaining legacy naming is clearly marked as compatibility-only.
</verification>

<success_criteria>
- Docs teach the GitBlocks brand.
- The local harness points developers at GitBlocks env vars and messages.
- Any legacy copy is clearly transitional, not the primary brand.
</success_criteria>

<output>
After completion, create `.planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-04-SUMMARY.md`
</output>
