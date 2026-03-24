---
created: 2026-03-24T03:49:01.290Z
title: Handle missing repo during refresh_ui_state
area: general
files:
  - bl_git/state.py:641
  - bl_git/diffs.py:99
  - bl_git/ops.py:266
---

## Problem

If the Git repo disappears while the Blender add-on is running, `_check()` can keep flowing into `refresh_ui_state()` and crash on an unresolved commit SHA. That freezes Blender instead of degrading cleanly.

## Solution

Guard the refresh/check path against missing or invalid repo state, and short-circuit UI diff refresh when HEAD/objects cannot be resolved. Prefer a non-fatal status message over raising from the timer/check loop.
