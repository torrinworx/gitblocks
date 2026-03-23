---
created: 2026-03-23T17:35:47.197Z
title: Add individual test shorthand
area: testing
files:
  - tests/runner.py
  - tests/unit/test_test_entrypoint.py
  - README.md
---

## Problem

Focused test runs are too awkward right now, and the current full-suite output clogs the context window for future sessions. We need a shorthand for running individual tests or feature-specific slices so future LLMs can target only the relevant checks instead of replaying the entire test system.

## Solution

Add a documented shortcut or runner entry point for selecting individual tests or modules, keep the console output concise, and document the pattern in the repo so future agents can reliably run targeted tests without the full suite noise.
