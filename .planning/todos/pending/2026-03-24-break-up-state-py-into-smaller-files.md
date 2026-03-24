---
created: 2026-03-24T03:49:44.780Z
title: Break up state.py into smaller files
area: general
files:
  - bl_git/state.py
---

## Problem

`bl_git/state.py` is close to 1k lines and mixes capture, diff shaping, grouping, and UI-facing state logic in one file. That makes it harder to reason about, test, and safely change the repo/state flows.

## Solution

Investigate whether the file should be split into smaller focused modules, keeping behavior unchanged and preserving the existing add-on contracts.
