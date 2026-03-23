---
created: 2026-03-23T17:06:25.106Z
title: Add Blender compatibility preflight
area: testing
files:
  - tests/runner.py
  - pytest.ini
  - bl_types/dump_anything.py
  - bl_types/bl_material.py
  - bl_types/bl_world.py
---

## Problem

Blender 5.1 is surfacing thousands of deprecation warnings during the test run, which makes it harder to spot real compatibility regressions. The current test harness goes straight from install checks into the full suite, so API changes can stay hidden until they spread across many tests.

## Solution

Add a lightweight compatibility preflight stage before the full suite, ideally with a small smoke set and deprecation warnings treated as errors. Keep the check close to Blender runtime behavior so it catches API shifts early without changing the main test flow.
