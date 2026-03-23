---
created: 2026-03-23T17:35:47.197Z
title: Add multi-version Blender test harness
area: testing
files:
  - tests/runner.py
  - tests/helpers.py
  - tests/unit/test_runner_selection.py
  - tests/unit/test_blender_versions.py
---

## Problem

The test runner only exercises one Blender version at a time, and the current flow makes it hard to validate compatibility across multiple installed versions. We also need a sequential harness that can read a `VERSIONS` env var, manage downloads/install state, run one Blender version at a time, show which version is active in the console, and report failures per version without blocking the whole matrix on non-setup test failures.

## Solution

Add a single-file harness for sequential multi-version runs. It should parse `VERSIONS=4.1,4.5,5.1,...`, manage each Blender install independently, keep output clearly labeled by version, and summarize failures at the end. Update failure handling so setup/install problems still stop the run, but ordinary test failures do not prevent later tests or later versions from running.
