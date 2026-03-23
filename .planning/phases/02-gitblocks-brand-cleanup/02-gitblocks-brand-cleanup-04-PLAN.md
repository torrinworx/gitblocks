---
phase: 02-gitblocks-brand-cleanup
plan: 04
type: execute
wave: 4
depends_on:
  - 02-gitblocks-brand-cleanup-01
  - 02-gitblocks-brand-cleanup-02
  - 02-gitblocks-brand-cleanup-03
files_modified:
  - README.md
  - blender_manifest.toml
  - AGENTS.md
  - .env.example
  - test.py
  - .planning/PROJECT.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
autonomous: true
requirements:
  - BRAND-06
  - BRAND-07
must_haves:
  truths:
    - "User-facing docs and harness instructions use GitBlocks naming only"
    - "Roadmap and requirements traceability point to the brand cleanup phase"
    - "A repo-wide search proves no legacy brand strings remain in implementation and documentation files outside the planning artifacts"
  artifacts:
    - path: "README.md"
      provides: "Project overview and user-facing brand copy"
      contains: "GitBlocks"
    - path: "blender_manifest.toml"
      provides: "Addon packaging metadata"
      contains: "GitBlocks"
    - path: ".planning/ROADMAP.md"
      provides: "Phase plan with cleanup requirements"
      contains: "02-gitblocks-brand-cleanup"
  key_links:
    - from: "README.md"
      to: "blender_manifest.toml"
      via: "shared public brand name"
      pattern: "GitBlocks"
    - from: ".planning/ROADMAP.md"
      to: ".planning/REQUIREMENTS.md"
      via: "requirement traceability"
      pattern: "BRAND-06|BRAND-07"
---

<objective>
Finish the cleanup by updating docs, packaging metadata, and planning traceability, then prove the repository no longer contains legacy brand strings in the files that ship or guide the add-on.

Purpose: the repo should present one consistent brand everywhere a user, contributor, or automation will look.
Output: GitBlocks-aligned docs plus a final repo-wide zero-legacy sweep.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@README.md
@blender_manifest.toml
@AGENTS.md
@.env.example
@test.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Rebrand docs, metadata, and planning records</name>
  <read_first>
    - README.md
    - blender_manifest.toml
    - AGENTS.md
    - .env.example
    - test.py
    - .planning/PROJECT.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
  </read_first>
  <files>README.md, blender_manifest.toml, AGENTS.md, .env.example, test.py, .planning/PROJECT.md, .planning/ROADMAP.md, .planning/REQUIREMENTS.md</files>
  <action>Replace the remaining public brand copy, packaging text, setup hints, and planning traceability with GitBlocks wording. Update the roadmap section to list the brand cleanup phase and its plan files, and make the requirements traceability point to the cleanup phase for BRAND-06 and BRAND-07.</action>
  <acceptance_criteria>
    - README.md and blender_manifest.toml describe GitBlocks only.
    - The roadmap lists phase 02-gitblocks-brand-cleanup and its plans.
    - Requirements traceability maps BRAND-06 and BRAND-07 to phase 02.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "cozystudio|Cozy Studio|cozy\b|COZYSTUDIO|cozystudio_addon" README.md blender_manifest.toml AGENTS.md .env.example test.py .planning/PROJECT.md .planning/ROADMAP.md .planning/REQUIREMENTS.md</automated>
  </verify>
  <done>The shipped docs and planning traceability are GitBlocks-branded.</done>
</task>

<task type="auto">
  <name>Task 2: Run the final zero-legacy sweep</name>
  <read_first>
    - README.md
    - blender_manifest.toml
    - AGENTS.md
    - test.py
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
  </read_first>
  <files>README.md, blender_manifest.toml, AGENTS.md, .env.example, test.py, .planning/PROJECT.md, .planning/ROADMAP.md, .planning/REQUIREMENTS.md</files>
  <action>Run the repo-wide grep sweep and the Blender-backed test command after all renames land. If any legacy brand string remains in implementation, docs, or harness files, remove it and rerun the same sweep until the search is clean. Do not reintroduce compatibility aliases.</action>
  <acceptance_criteria>
    - The repo-wide grep returns no remaining legacy brand matches in implementation, docs, or harness files.
    - The Blender-backed test command passes after the renames.
  </acceptance_criteria>
  <verify>
    <automated>rg -n --glob '!.planning/**' "cozystudio|Cozy Studio|cozy\b|COZYSTUDIO|cozystudio_addon" . && python test.py</automated>
  </verify>
  <done>The cleanup is proven by search and test verification.</done>
</task>

</tasks>

<verification>
Require both a clean repo-wide legacy-string sweep and a passing Blender-backed test run before closing the phase.
</verification>

<success_criteria>
- The repo ships with GitBlocks naming only.
- The roadmap and requirements document the cleanup phase.
- The final search and test sweep pass without legacy brand holdouts.
</success_criteria>

<output>
After completion, create `.planning/phases/02-gitblocks-brand-cleanup/02-gitblocks-brand-cleanup-04-SUMMARY.md`
</output>
