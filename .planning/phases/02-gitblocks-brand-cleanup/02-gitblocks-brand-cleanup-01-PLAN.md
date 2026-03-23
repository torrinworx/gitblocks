---
phase: 02-gitblocks-brand-cleanup
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - branding.py
  - __init__.py
  - ui/operators.py
  - ui/panels.py
  - ui/props.py
  - ui/lists.py
autonomous: true
requirements:
  - BRAND-06
must_haves:
  truths:
    - "GitBlocks is the only public brand exposed in addon metadata and UI copy"
    - "Blender operator namespaces and panel identifiers no longer use legacy brand prefixes"
    - "WindowManager property names and list actions use GitBlocks-only identifiers"
  artifacts:
    - path: "branding.py"
      provides: "Single source of truth for GitBlocks brand constants"
      contains: "BRAND_NAME = \"GitBlocks\""
    - path: "__init__.py"
      provides: "Addon metadata and install operator registration"
      exports: ["bl_info", "register", "unregister"]
    - path: "ui/operators.py"
      provides: "GitBlocks operator classes and bl_idname values"
      contains: "bl_idname = \"gitblocks."
  key_links:
    - from: "branding.py"
      to: "ui/operators.py"
      via: "shared brand constants"
      pattern: "BRAND_NAME|BRAND_SLUG|UI_LOG_PREFIX"
    - from: "ui/operators.py"
      to: "Blender registration"
      via: "operator class names and bl_idname strings"
      pattern: 'bl_idname = "gitblocks\.'
---

<objective>
Make GitBlocks the only runtime-visible brand by renaming public addon metadata, operator namespaces, panel IDs, and UI labels away from the legacy brand.

Purpose: the public add-on surface should read as one brand end-to-end.
Output: updated runtime/UI modules with GitBlocks-only identifiers.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@branding.py
@__init__.py
@ui/operators.py
@ui/panels.py
@ui/props.py
@ui/lists.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Collapse public brand constants to GitBlocks</name>
  <read_first>
    - branding.py
    - __init__.py
  </read_first>
  <files>branding.py, __init__.py</files>
  <action>Delete the legacy brand constants and alias exports in branding.py, then update __init__.py so bl_info, the install-deps operator class, and the addon preferences class all use GitBlocks naming only. Keep the dependency install flow unchanged; this task is only about the brand surface and registration names.</action>
  <acceptance_criteria>
    - branding.py defines GitBlocks-only brand constants.
    - __init__.py no longer defines any class or bl_idname with the legacy brand prefix.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "cozystudio|Cozy Studio|COZYSTUDIO|cozystudio_addon" branding.py __init__.py</automated>
  </verify>
  <done>The addon metadata and core registration surface are GitBlocks-only.</done>
</task>

<task type="auto">
  <name>Task 2: Rename operator namespaces to gitblocks</name>
  <read_first>
    - ui/operators.py
    - branding.py
  </read_first>
  <files>ui/operators.py</files>
  <action>Rename every operator class, bl_idname, and operator invocation in ui/operators.py from the legacy namespace to the GitBlocks namespace. Update error text and button labels so they speak GitBlocks consistently, and remove any compatibility alias registration or fallback call paths.</action>
  <acceptance_criteria>
    - ui/operators.py contains gitblocks operator IDs instead of the legacy namespace.
    - Operator call sites inside ui/operators.py reference the new namespace only.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "cozystudio|Cozy Studio|COZYSTUDIO|bpy\.ops\.cozystudio|bl_idname = \"cozystudio\." ui/operators.py</automated>
  </verify>
  <done>The operator namespace is fully renamed and internally self-consistent.</done>
</task>

<task type="auto">
  <name>Task 3: Rename UI panel and property identifiers</name>
  <read_first>
    - ui/panels.py
    - ui/props.py
    - ui/lists.py
    - branding.py
  </read_first>
  <files>ui/panels.py, ui/props.py, ui/lists.py</files>
  <action>Rename panel identifiers, WindowManager properties, list actions, and redraw hooks to GitBlocks-only names. Keep the UI layout and behavior identical, but replace the legacy prefix everywhere it appears in registration, property access, and operator wiring.</action>
  <acceptance_criteria>
    - ui/panels.py uses GitBlocks-prefixed panel IDs and operator names.
    - ui/props.py registers GitBlocks-prefixed WindowManager properties.
    - ui/lists.py no longer references the legacy operator namespace.
  </acceptance_criteria>
  <verify>
    <automated>rg -n "cozystudio|Cozy Studio|COZYSTUDIO|cozystudio_" ui/panels.py ui/props.py ui/lists.py</automated>
  </verify>
  <done>The visible Blender UI registration surface no longer carries legacy brand names.</done>
</task>

</tasks>

<verification>
Run the focused GitBlocks runtime/UI grep sweep and confirm no legacy brand strings remain in the touched runtime files.
</verification>

<success_criteria>
- The addon metadata is branded GitBlocks end-to-end.
- The public Blender operator namespace is GitBlocks-only.
- The visible UI registration surface contains no legacy brand strings.
</success_criteria>

<output>
After completion, create `.planning/phases/02-gitblocks-brand-cleanup/02-gitblocks-brand-cleanup-01-SUMMARY.md`
</output>
