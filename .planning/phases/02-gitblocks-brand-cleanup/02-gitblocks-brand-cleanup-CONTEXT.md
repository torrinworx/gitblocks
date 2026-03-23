# Phase 02: GitBlocks Brand Cleanup - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning
**Source:** User request

<domain>
## Phase Boundary

Remove the remaining legacy Cozy Studio / cozystudio / cozy brand surfaces and compatibility aliases so the repo presents GitBlocks naming only across runtime code, storage helpers, tests, docs, and harnesses.

</domain>

<decisions>
## Implementation Decisions

- GitBlocks is the only supported public, runtime, and storage brand in this phase.
- Legacy `cozystudio` identifiers are removed instead of preserved as compatibility aliases.
- Rename Blender operator IDs, WindowManager properties, storage helpers, datablock metadata, test harness names, and docs to GitBlocks naming.
- Preserve autosave and repo-state behavior while changing identifiers.

## the agent's Discretion

- Exact rename sequence and helper factoring.
- Whether to introduce temporary migration helpers if they do not reintroduce legacy brand strings into the repository.

</decisions>

<deferred>
## Deferred Ideas

None — this phase is the cleanup pass.

</deferred>
