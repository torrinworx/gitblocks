---
phase: 01-gitblocks-brand-migration
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - .planning/phases/01-gitblocks-brand-migration/01-RESEARCH.md
autonomous: true
requirements:
  - BRAND-01
  - BRAND-02
must_haves:
  truths:
    - "Every legacy brand reference is classified by surface area"
    - "The canonical GitBlocks naming policy is written down"
    - "Compatibility-only holdouts are explicitly called out"
  artifacts:
    - path: ".planning/phases/01-gitblocks-brand-migration/01-RESEARCH.md"
      provides: "Brand inventory and migration map"
  key_links:
    - from: "repo-wide grep results"
      to: "migration policy"
      via: "classification matrix"
      pattern: "cozystudio|Cozy Studio|cozy|COZYSTUDIO_"
---

<objective>
Build the brand inventory and decide the canonical GitBlocks migration policy before any code changes.

Purpose: this phase needs a single source of truth for what gets renamed now, what keeps a compatibility alias, and what must not change yet.
Output: `.planning/phases/01-gitblocks-brand-migration/01-RESEARCH.md` with an inventory table, compatibility notes, and the proposed brand contract.
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

<interfaces>
The executor should derive the inventory from these current surfaces:

- `README.md` — product-facing Cozy Studio copy
- `ui/panels.py` — visible panel labels and categories
- `ui/operators.py` — operator text and user-visible errors
- `ui/props.py` — property names and descriptions
- `ui/helpers.py` — `.cozystudio/blocks/` path parsing
- `bl_git/__init__.py` — on-disk repo namespace and carryover prefix
- `tests/` — current expectations for module names, panel ids, and paths
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Inventory every legacy brand surface</name>
  <read_first>
    - README.md
    - bl_types/README.md
    - ui/panels.py
    - ui/operators.py
    - ui/props.py
    - ui/helpers.py
    - bl_git/__init__.py
    - tests/integration/test_ui_registration.py
  </read_first>
  <files>.planning/phases/01-gitblocks-brand-migration/01-RESEARCH.md</files>
  <action>Run a repository-wide search for `Cozy Studio`, `cozystudio`, `cozy`, `COZYSTUDIO_`, `cozystudio_addon`, and `.cozystudio/`. Group matches by surface area (UI text, operator identifiers, filesystem paths, docs, tests, harness scripts) and write the inventory table into the research doc. Call out any references that are user-visible versus compatibility-only.</action>
  <acceptance_criteria>
    - The research doc lists every legacy brand surface that appears in the add-on.
    - The doc separates user-facing brand text from compatibility-only identifiers.
  </acceptance_criteria>
  <verify>
    <automated>rg -n -i "cozy studio|cozystudio|cozy\b|cozystudio_addon|\.cozystudio/|COZYSTUDIO_" README.md bl_types ui bl_git tests .env.example test.py</automated>
  </verify>
  <done>The brand inventory is complete and grouped by migration surface.</done>
</task>

<task type="auto">
  <name>Task 2: Define the GitBlocks migration contract</name>
  <read_first>
    - .planning/phases/01-gitblocks-brand-migration/01-RESEARCH.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md
  </read_first>
  <files>.planning/phases/01-gitblocks-brand-migration/01-RESEARCH.md</files>
  <action>Turn the raw inventory into a concrete migration strategy. Document the canonical brand name, slug, filesystem namespace, legacy fallback rules, and which identifiers stay frozen for compatibility. Make the policy explicit enough that later implementation plans can follow it without guessing.</action>
  <acceptance_criteria>
    - The research doc names the canonical GitBlocks brand contract.
    - The research doc explicitly documents legacy compatibility rules for `cozystudio` holdouts.
  </acceptance_criteria>
  <verify>
    <automated>python - <<'PY'
from pathlib import Path
text = Path('.planning/phases/01-gitblocks-brand-migration/01-RESEARCH.md').read_text(encoding='utf-8')
assert 'GitBlocks' in text
assert 'cozystudio' in text.lower()
print('ok')
PY</automated>
  </verify>
  <done>A migration contract exists that later implementation plans can consume directly.</done>
</task>

<task type="auto">
  <name>Task 3: Validate the research is exhaustive enough</name>
  <read_first>
    - .planning/phases/01-gitblocks-brand-migration/01-RESEARCH.md
    - .planning/ROADMAP.md
  </read_first>
  <files>.planning/phases/01-gitblocks-brand-migration/01-RESEARCH.md</files>
  <action>Cross-check the research against the live repo search results and tighten the notes until every major legacy surface has an owner: UI copy, backend paths, redraw ids, docs, harness scripts, and tests. If a reference is intentionally deferred, mark it as a compatibility alias instead of leaving it ambiguous.</action>
  <acceptance_criteria>
    - Every major legacy brand surface has a migration decision in the research doc.
    - Any deferred reference is labeled as an intentional compatibility alias.
  </acceptance_criteria>
  <verify>
    <automated>python - <<'PY'
from pathlib import Path
text = Path('.planning/phases/01-gitblocks-brand-migration/01-RESEARCH.md').read_text(encoding='utf-8')
for needle in ['UI', 'paths', 'tests', 'docs', 'compatibility']:
    assert needle.lower() in text.lower()
print('ok')
PY</automated>
  </verify>
  <done>The research doc is ready to feed the implementation plans.</done>
</task>

</tasks>

<verification>
Confirm the research doc reads like a migration spec, not a loose note dump: inventory table, canonical brand policy, and compatibility exceptions must all be present.
</verification>

<success_criteria>
- The phase produces a usable migration contract.
- The research doc can be handed to later implementation plans without more repo spelunking.
- Every legacy brand surface is categorized.
</success_criteria>

<output>
After completion, create `.planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-01-SUMMARY.md`
</output>
