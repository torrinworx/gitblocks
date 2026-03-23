---
phase: 02-gitblocks-brand-cleanup
plan: 02
type: execute
wave: 2
depends_on:
  - 02-gitblocks-brand-cleanup-01
files_modified:
  - bl_git/paths.py
  - bl_git/__init__.py
  - bl_git/blocks.py
  - bl_git/manifest.py
  - bl_git/state.py
  - bl_git/checkout.py
  - bl_git/tracking.py
  - bl_types/bl_datablock.py
  - ui/helpers.py
autonomous: true
requirements:
  - BRAND-07
must_haves:
  truths:
    - "Canonical storage helpers only expose GitBlocks namespace values"
    - "Block, manifest, and carryover logic no longer read or write legacy brand paths"
    - "Datablock metadata helpers resolve using GitBlocks identifiers only"
  artifacts:
    - path: "bl_git/paths.py"
      provides: "Canonical namespace and relpath helpers"
      contains: "CANONICAL_NAMESPACE = \".gitblocks\""
    - path: "bl_git/__init__.py"
      provides: "BpyGit initialization and path roots"
      contains: "self.gitblocks_path"
    - path: "bl_types/bl_datablock.py"
      provides: "UUID resolution helpers"
      contains: "gitblocks_uuid"
  key_links:
    - from: "bl_git/paths.py"
      to: "bl_git/blocks.py"
      via: "block_relpath / manifest_relpath helpers"
      pattern: 'block_relpath\(|manifest_relpath\('
    - from: "bl_git/state.py"
      to: "bl_types/bl_datablock.py"
      via: "datablock UUID lookup and state serialization"
      pattern: "gitblocks_uuid|uuid"
---

<objective>
Remove the remaining persistence and internal identifier compatibility surfaces so storage, manifest loading, and datablock lookup all use GitBlocks naming only.

Purpose: the on-disk and internal data model must no longer depend on legacy brand aliases.
Output: updated storage helpers and identifier plumbing with GitBlocks-only names.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@bl_git/paths.py
@bl_git/__init__.py
@bl_git/blocks.py
@bl_git/manifest.py
@bl_git/state.py
@bl_git/checkout.py
@bl_git/tracking.py
@bl_types/bl_datablock.py
@ui/helpers.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Make GitBlocks the only storage namespace</name>
  <read_first>
    - bl_git/paths.py
    - bl_git/__init__.py
    - bl_git/blocks.py
    - bl_git/manifest.py
  </read_first>
  <files>bl_git/paths.py, bl_git/__init__.py, bl_git/blocks.py, bl_git/manifest.py</files>
  <action>Remove every legacy namespace constant and fallback path in the storage helpers. namespace_roots should return the GitBlocks namespace only, block_relpath and manifest_relpath should default to GitBlocks, and block/manifest load-write logic should stop checking .cozystudio paths or namespace overrides.</action>
  <acceptance_criteria>
    - bl_git/paths.py defines a single canonical namespace.
    - bl_git/blocks.py and bl_git/manifest.py no longer branch on legacy namespace paths.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "cozystudio|LEGACY_NAMESPACE|LEGACY_BLOCKS_PREFIX|LEGACY_MANIFEST_REL|\.cozystudio" bl_git/paths.py bl_git/__init__.py bl_git/blocks.py bl_git/manifest.py</automated>
  </verify>
  <done>Storage helpers only read and write GitBlocks paths.</done>
</task>

<task type="auto">
  <name>Task 2: Rename internal IDs and datablock metadata</name>
  <read_first>
    - bl_git/state.py
    - bl_git/checkout.py
    - bl_git/tracking.py
    - bl_types/bl_datablock.py
    - ui/helpers.py
  </read_first>
  <files>bl_git/state.py, bl_git/checkout.py, bl_git/tracking.py, bl_types/bl_datablock.py, ui/helpers.py</files>
  <action>Rename the internal metadata fields, UUID helpers, carryover markers, and lookup code to GitBlocks naming. Update state serialization, checkout restore, tracking assignment, and UI helper cache lookups so they no longer reference any legacy brand-prefixed attribute or field.</action>
  <acceptance_criteria>
    - state.py emits GitBlocks-prefixed workflow and metadata fields.
    - checkout.py and tracking.py no longer read or write legacy brand-prefixed identifiers.
    - bl_types/bl_datablock.py resolves datablocks using the renamed UUID field.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "cozystudio|cozystudio_uuid|cozystudio-carryover|cozystudio_" bl_git/state.py bl_git/checkout.py bl_git/tracking.py bl_types/bl_datablock.py ui/helpers.py</automated>
  </verify>
  <done>The internal data model and UUID plumbing are GitBlocks-only.</done>
</task>

</tasks>

<verification>
Confirm the storage namespace, manifest loading, and datablock metadata paths contain no legacy brand strings.
</verification>

<success_criteria>
- New workspaces and internal data helpers use GitBlocks names only.
- Manifest and checkout code do not contain legacy namespace fallbacks.
- UUID and carryover metadata use the renamed GitBlocks identifiers.
</success_criteria>

<output>
After completion, create `.planning/phases/02-gitblocks-brand-cleanup/02-gitblocks-brand-cleanup-02-SUMMARY.md`
</output>
