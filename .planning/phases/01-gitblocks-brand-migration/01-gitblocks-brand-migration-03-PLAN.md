---
phase: 01-gitblocks-brand-migration
plan: 03
type: execute
wave: 3
depends_on:
  - 01-gitblocks-brand-migration-02
files_modified:
  - bl_git/__init__.py
  - bl_git/blocks.py
  - bl_git/diffs.py
  - bl_git/manifest.py
  - bl_git/checkout.py
  - bl_git/ops.py
  - ui/helpers.py
  - ui/state.py
autonomous: true
requirements:
  - BRAND-04
must_haves:
  truths:
    - "The canonical on-disk namespace is GitBlocks-first"
    - "Existing .cozystudio repos still open through compatibility logic"
    - "UI refresh hooks point at the renamed panel identifiers"
  artifacts:
    - path: "bl_git/__init__.py"
      provides: "Canonical repo namespace and path attributes"
    - path: "ui/helpers.py"
      provides: "GitBlocks-aware block path parsing"
    - path: "bl_git/checkout.py"
      provides: "GitBlocks panel redraw hooks"
  key_links:
    - from: "BpyGit path setup"
      to: "block file I/O"
      via: "shared namespace constants"
      pattern: "\.gitblocks|\.cozystudio compatibility"
---

<objective>
Move backend storage/path handling and refresh hooks onto the GitBlocks namespace while keeping read compatibility for legacy repositories.

Purpose: this is the migration that protects saved projects. Users must be able to open old repos, but new writes should land in the GitBlocks namespace.
Output: backend helpers and redraw hooks that understand both the legacy and canonical namespaces.
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
@.planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-01-SUMMARY.md
@.planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-02-SUMMARY.md

<interfaces>
Key backend surfaces to update:

From `bl_git/__init__.py`:
```python
self.cozystudio_path
self.blockspath
self.manifestpath
```

From `bl_git/blocks.py`:
```python
_load_block_data()
_read()
```

From `bl_git/manifest.py` and `bl_git/diffs.py`:
```python
path filters and manifest serialization paths
```

From `ui/helpers.py` and `ui/state.py`:
```python
block path parsing and redraw hooks
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Migrate repo path handling to GitBlocks-first storage</name>
  <read_first>
    - bl_git/__init__.py
    - bl_git/blocks.py
    - bl_git/diffs.py
    - bl_git/manifest.py
    - ui/helpers.py
  </read_first>
  <files>bl_git/__init__.py, bl_git/blocks.py, bl_git/diffs.py, bl_git/manifest.py, ui/helpers.py</files>
  <action>Introduce GitBlocks-aware path constants and helpers, then update the backend to prefer `.gitblocks/blocks/` and `.gitblocks/manifest.json` while still reading legacy `.cozystudio` data when present. Keep the compatibility behavior explicit in the code so the repo can open old projects without special handling elsewhere.</action>
  <acceptance_criteria>
    - New writes use the GitBlocks namespace.
    - Legacy `.cozystudio` repos still load through compatibility code.
    - Block-path parsing understands the new namespace.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "\.cozystudio/blocks/|\.gitblocks/blocks/|cozystudio_path|manifestpath|blockspath" bl_git ui</automated>
  </verify>
  <done>Backend storage is GitBlocks-first and backward compatible.</done>
</task>

<task type="auto">
  <name>Task 2: Repoint backend redraw hooks at the new panel identifiers</name>
  <read_first>
    - bl_git/checkout.py
    - bl_git/ops.py
    - bl_git/merge.py
    - ui/state.py
    - branding.py
  </read_first>
  <files>bl_git/checkout.py, bl_git/ops.py, bl_git/merge.py, ui/state.py</files>
  <action>Replace hard-coded `COZYSTUDIO_PT_*` redraw targets with brand-derived panel identifiers so backend refresh logic still works after the panel classes are renamed. Do not alter the behavior of the redraw flow; only the identifiers should change.</action>
  <acceptance_criteria>
    - No backend redraw call still references `COZYSTUDIO_PT_*`.
    - UI refreshes continue to target the history, changes, and branches panels.
  </acceptance_criteria>
  <verify>
    <automated>rg -n 'COZYSTUDIO_PT_' bl_git ui</automated>
  </verify>
  <done>Backend redraw hooks follow the GitBlocks panel ids.</done>
</task>

</tasks>

<verification>
Run a repo-wide search to ensure the only remaining legacy namespace references are the ones explicitly allowed by the compatibility policy.
</verification>

<success_criteria>
- The addon stores and resolves data using the GitBlocks namespace first.
- Legacy `.cozystudio` projects still open.
- Backend refresh behavior still reaches the correct panels.
</success_criteria>

<output>
After completion, create `.planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-03-SUMMARY.md`
</output>
