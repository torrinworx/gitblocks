# Research Summary: Cozy Studio

**Domain:** Blender datablock version control
**Researched:** 2026-03-21
**Overall confidence:** MEDIUM

## Executive Summary

The Blender version-control ecosystem is small but clear about the baseline: users want to initialize a project/repo, create versions, browse history, switch branches, and restore older states without leaving Blender. Products in this space generally succeed or fail on whether they make those flows feel native and safe inside the editor.

The strongest pattern is moving away from full `.blend` snapshots toward something more reviewable: datablock serialization, checkpointing, or semantic diffs. That is the main source of differentiation because it turns version control from “file backup” into “understandable project history.”

For Cozy Studio, the roadmap should lead with the baseline Git workflow in Blender, then layer in datablock-level review and recovery. Merge/rebase and conflict resolution are valuable, but they only pay off after the core read/write/checkout model is stable.

## Key Findings

**Stack:** Blender add-on + Git-backed history + readable datablock serialization.
**Architecture:** Blender UI layer over a repository/history/serialization core, with diff and restore flows built around datablocks.
**Critical pitfall:** Full-file `.blend` snapshots and autosave-hostile workflows make the product feel generic or unsafe.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Core Git workflow in Blender** - baseline expectations; proves the product is usable.
   - Addresses: repo init, commit, history, checkout/restore, branch switching
   - Avoids: leaving Blender for basic VCS actions

2. **Readable datablock history** - turns the product into a real Blender-native VCS.
   - Addresses: datablock serialization, diff/compare, staging/unstaging
   - Avoids: full-file snapshot bloat and opaque history

3. **Advanced review and recovery** - strongest differentiators once the base is stable.
   - Addresses: semantic diff, per-object timelines, visual compare, merge/rebase, conflict resolution
   - Avoids: shipping sophisticated UX before the history model is trustworthy

**Phase ordering rationale:**
- Git-like navigation must exist before users will trust richer diffs.
- Serialization must come before semantic review because all comparison features depend on stable data.
- Merge/rebase should wait until checkout, diff, and recovery are robust.

**Research flags for phases:**
- Phase 1: low research burden; mostly UX and workflow polish.
- Phase 2: medium research burden; serialization and data identity details matter.
- Phase 3: high research burden; semantic diff and merge conflict handling are hard.

## Confidence Assessment

| Area | Confidence | Notes |
|---|---|---|
| Stack | MEDIUM | Public repos show the common Blender/Python/Git pattern, but implementation choices vary. |
| Features | MEDIUM | Several public add-ons expose overlapping baseline flows. |
| Architecture | MEDIUM | The core component split is consistent across products, but details are inferred. |
| Pitfalls | MEDIUM | Strongly supported by product patterns and Cozy Studio’s own scope notes. |

## Gaps to Address

- Exact user expectations for staging UX in Blender.
- How often teams want merge/rebase inside Blender versus outside.
- Whether storage modes should be productized or hidden behind defaults.
