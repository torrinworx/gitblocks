---
phase: 01-gitblocks-brand-migration
plan: 02
type: execute
wave: 2
depends_on:
  - 01-gitblocks-brand-migration-01
files_modified:
  - branding.py
  - __init__.py
  - ui/props.py
  - ui/panels.py
  - ui/operators.py
  - ui/lists.py
autonomous: true
requirements:
  - BRAND-03
must_haves:
  truths:
    - "The add-on reports GitBlocks as the public brand"
    - "Panels and operator text show GitBlocks instead of Cozy Studio"
    - "A shared brand contract exists for all runtime UI code"
  artifacts:
    - path: "branding.py"
      provides: "Canonical brand constants and compatibility aliases"
    - path: "ui/panels.py"
      provides: "GitBlocks panel labels and category text"
    - path: "ui/operators.py"
      provides: "GitBlocks user-facing operator copy"
  key_links:
    - from: "branding.py"
      to: "runtime UI"
      via: "shared constants"
      pattern: "GitBlocks|gitblocks|cozystudio compatibility"
---

<objective>
Move the add-on’s visible runtime branding to GitBlocks with a shared source of truth.

Purpose: this is the user-facing rename pass — the thing people see when they open the add-on, read labels, or trigger operators.
Output: a runtime brand contract plus updated panels, operators, property labels, and addon metadata.
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

<interfaces>
Key runtime surfaces to update from the brand contract:

From `__init__.py`:
```python
bl_info["name"]
```

From `ui/panels.py`:
```python
bl_label
bl_category
```

From `ui/operators.py`:
```python
bl_description
report(...)
```

From `ui/props.py`:
```python
PropertyGroup labels and descriptions
```

From `ui/lists.py`:
```python
UIList class name and display text
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add the shared GitBlocks brand contract</name>
  <read_first>
    - __init__.py
    - ui/panels.py
    - ui/operators.py
    - ui/props.py
    - ui/lists.py
  </read_first>
  <files>branding.py, __init__.py</files>
  <action>Create a centralized brand module that defines the canonical public name (`GitBlocks`), the slug (`gitblocks`), and explicit legacy alias values for compatibility. Wire `bl_info` and any top-level addon text in `__init__.py` to those constants so the add-on identifies itself as GitBlocks immediately.</action>
  <acceptance_criteria>
    - `branding.py` exports the canonical GitBlocks strings.
    - `__init__.py` reports GitBlocks as the add-on name.
  </acceptance_criteria>
  <verify>
    <automated>python - <<'PY'
from pathlib import Path
text = Path('branding.py').read_text(encoding='utf-8') + Path('__init__.py').read_text(encoding='utf-8')
assert 'GitBlocks' in text
assert 'cozystudio' in text.lower()
print('ok')
PY</automated>
  </verify>
  <done>The brand contract exists and the addon entrypoint uses it.</done>
</task>

<task type="auto">
  <name>Task 2: Rebrand the visible Blender UI</name>
  <read_first>
    - branding.py
    - ui/panels.py
    - ui/operators.py
    - ui/props.py
    - ui/lists.py
  </read_first>
  <files>ui/props.py, ui/panels.py, ui/operators.py, ui/lists.py</files>
  <action>Update every user-facing label, description, header, and status string in the Blender UI to use GitBlocks wording. Keep any stable Blender registration identifiers that must not change for compatibility, but make the actual text the user sees read as GitBlocks. Route those strings through the new brand contract instead of hard-coded Cozy Studio literals.</action>
  <acceptance_criteria>
    - Panel headers and categories read GitBlocks.
    - Operator descriptions and user-facing messages no longer say Cozy Studio.
    - The runtime UI gets its brand text from `branding.py`, not from scattered literals.
  <verify>
    <automated>rg -n "Cozy Studio|cozystudio|CozyStudio|cozy\b" ui/__init__.py ui/panels.py ui/operators.py ui/props.py ui/lists.py branding.py</automated>
  </verify>
  <done>The visible Blender UI is branded as GitBlocks.</done>
</task>

</tasks>

<verification>
Run the Blender UI registration tests and confirm the new brand text is present in the panels, operator reports, and addon metadata.
</verification>

<success_criteria>
- The addon UI presents GitBlocks branding everywhere users interact with it.
- Runtime strings are sourced from a shared brand contract.
- No unintentional Cozy Studio copy remains in the UI layer.
</success_criteria>

<output>
After completion, create `.planning/phases/01-gitblocks-brand-migration/01-gitblocks-brand-migration-02-SUMMARY.md`
</output>
