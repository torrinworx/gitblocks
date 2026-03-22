# Architecture Patterns

**Domain:** Blender datablock version control
**Researched:** 2026-03-21

## Recommended Architecture

Blender UI/operators on top of a small core that handles serialization, history, diff, and restore. Git stays the storage/history engine; Blender-specific code should be kept at the edge.

### Component Boundaries

| Component | Responsibility | Communicates With |
|---|---|---|
| Blender UI layer | Panels, operators, user actions | History service, serialization service |
| History service | Init, commit, branch, checkout, merge/rebase orchestration | Git backend, state cache |
| Serialization service | Convert datablocks to/from readable files | Blender API, diff service |
| Diff service | Compare states and surface changes | History service, UI layer |
| Restore/recovery service | Rebuild scene state safely | Serialization service, Blender API |
| Git backend | Repo plumbing | History service |

### Data Flow

1. Blender edits datablocks.
2. Serialization writes changed datablocks to readable files.
3. Git records history and branches.
4. Diff/compare reads two states and summarizes changes.
5. Checkout/restore reconstructs Blender state from stored history.

## Patterns to Follow

### Pattern 1: Edge-adapter architecture
**What:** Keep Blender-specific code at the edges.
**When:** Always.
**Example:**
```typescript
// pseudo-code
uiAction -> service -> backend -> filesystem
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Blender logic everywhere
**What:** Letting UI code own serialization, Git, and restore details.
**Why bad:** Hard to test and easy to break autosave/recovery.
**Instead:** Put workflow logic in a core service layer.

## Scalability Considerations

| Concern | At 100 users | At 10K users | At 1M users |
|---|---|---|---|
| Repo size | Manageable | Needs pruning/indexing | Needs strong storage discipline |
| History lookup | Simple scans | Cached indexes help | Dedicated indexing likely needed |
| Diff cost | Fine | Background work helps | Incremental diff becomes important |

## Sources

- https://github.com/makehappyinstall/blender_git
- https://github.com/imaginelenses/blendit
- https://github.com/bkrmendy/cg_timeline
