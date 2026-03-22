# Cozy Studio State

## Project Reference

- **Core value**: Let Blender projects use trustworthy Git history at datablock granularity without breaking autosave or forcing a non-Blender workflow.
- **Current focus**: Phase 1 bootstrap safety is planned and ready for implementation.

## Current Position

- **Milestone**: Initial roadmap
- **Phase**: Phase 1 planned
- **Status**: Ready for implementation
- **Progress**: 0%

## Performance Metrics

- **Requirements mapped**: 11/11
- **Phases defined**: 4
- **Coverage gaps**: 0

## Accumulated Context

- Cozy Studio is a Blender add-on for Git-style version control at datablock granularity.
- Autosave must remain enabled and unaffected.
- Research recommends the order: core Git workflow, datablock review, then merge/rebase recovery.
- Requirement categories in scope: Bootstrap, Datablocks, History, Conflicts, UI State.

## Session Continuity

- **Next action**: Implement Phase 1 bootstrap safety work.
- **After Phase 1**: Run `/gsd-transition`.
- **Traceability**: REQUIREMENTS.md already maps every v1 requirement to a phase.
