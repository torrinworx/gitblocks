# Phase 01: GitBlocks Brand Migration - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning
**Source:** User request

<domain>
## Phase Boundary

Audit every `Cozy Studio` / `cozystudio` / `cozy` variation in the add-on and migrate the brand to GitBlocks or gitblocks-style variants, without breaking compatibility for existing repos or saved data.

</domain>

<decisions>
## Implementation Decisions

- The canonical public brand is **GitBlocks**.
- User-facing labels, docs, and packaging should move to GitBlocks or gitblocks-style variants.
- Legacy `cozystudio` names may remain only as compatibility aliases where required for saved data, repository paths, or installed add-on behavior.
- Preserve autosave and repo-state behavior.

## the agent's Discretion

- Whether to keep some Blender registration identifiers (`cozystudio_*`) as compatibility shims or rename them immediately.
- Whether `.gitblocks` or `gitblocks` is the canonical on-disk namespace as long as the compatibility policy is explicit.

</decisions>

<deferred>
## Deferred Ideas

None — this phase is specifically about branding migration and compatibility policy.

</deferred>
