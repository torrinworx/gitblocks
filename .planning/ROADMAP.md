# Cozy Studio Roadmap

## Phases

- [ ] **Phase 1: Bootstrap Safety** - Initialize Cozy Studio repos in Blender and surface blockers before any repo action runs.
- [ ] **Phase 2: Datablock Capture & Review** - Serialize datablocks, restore history, and show staged/unstaged changes in Blender.
- [ ] **Phase 3: Commit & Branch History** - Commit tracked changes and navigate commits/branches safely from inside Blender.
- [ ] **Phase 4: Merge & Rebase Recovery** - Merge and rebase branches while surfacing conflicts through the add-on workflow.

## Phase Details

### Phase 1: Bootstrap Safety
**Goal**: Users can start a Cozy Studio repository in Blender and see setup problems before any repo action runs.
**Depends on**: Nothing (first phase)
**Requirements**: BOOT-01, BOOT-02
**Success Criteria** (what must be TRUE):
1. User can initialize a Cozy Studio repository from inside Blender.
2. When dependencies or setup are missing, the add-on shows a clear blocker before repo actions run.
3. After initialization, the add-on clearly reflects that the repository is ready for Git actions.
**Plans**: TBD

### Phase 2: Datablock Capture & Review
**Goal**: Users can see, review, and restore datablock-level history inside Blender.
**Depends on**: Phase 1
**Requirements**: DATA-01, DATA-02, DATA-03, UI-01
**Success Criteria** (what must be TRUE):
1. Supported datablock edits are written as per-datablock JSON block files.
2. Users can inspect staged and unstaged datablock changes before committing.
3. Users can restore supported datablocks from stored block data when checking out history.
4. Repository status, history, and change groups appear in the Blender UI without freezing the panel.
**Plans**: TBD

### Phase 3: Commit & Branch History
**Goal**: Users can record meaningful history and move between commits and branches without leaving Blender.
**Depends on**: Phase 2
**Requirements**: HIST-01, HIST-02, HIST-03
**Success Criteria** (what must be TRUE):
1. User can commit tracked changes from Blender.
2. When preconditions fail, the add-on shows clear blockers instead of creating a bad commit.
3. User can check out earlier commits and branches and the scene matches the selected history.
4. User can create branches from commits inside Blender.
**Plans**: TBD

### Phase 4: Merge & Rebase Recovery
**Goal**: Users can merge and rebase branches while seeing and resolving conflicts in the add-on workflow.
**Depends on**: Phase 3
**Requirements**: CONF-01, CONF-02
**Success Criteria** (what must be TRUE):
1. User can merge branches from inside Blender.
2. When automatic merge resolution fails, conflicts are surfaced clearly in the UI.
3. User can rebase branches from inside Blender.
4. Conflicts during rebase can be resolved through the add-on workflow.
**Plans**: TBD

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Bootstrap Safety | 0/1 | Not started | - |
| 2. Datablock Capture & Review | 0/1 | Not started | - |
| 3. Commit & Branch History | 0/1 | Not started | - |
| 4. Merge & Rebase Recovery | 0/1 | Not started | - |
