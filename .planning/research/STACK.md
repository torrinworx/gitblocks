# Stack Research

**Project:** Cozy Studio
**Researched:** 2026-03-21
**Confidence:** MEDIUM

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended | Confidence |
|------------|---------|---------|-----------------|------------|
| Blender add-on runtime (`bpy`) | Blender 4.2+ | UI, operators, handlers, datablock access | Cozy Studio has to run inside Blender; this is the only layer that can safely read/write datablocks and participate in Blender UX. | HIGH |
| Python stdlib (`json`, `pathlib`, `dataclasses`, `subprocess`, `typing`) | Blender-bundled Python | Core app logic and file IO | Keep the runtime dependency-light; the standard library is enough for canonical JSON, filesystem work, and command dispatch. | HIGH |
| GitPython + system Git | GitPython 3.1.46 / Git 2.x | Repository operations | GitPython gives a clean Python API for repo state while still exposing `repo.git` for real Git commands; Git remains the history engine. | HIGH |
| Blender extension packaging (`blender_manifest.toml` + `wheels/`) | Current Blender extension format | Distribution | Blender docs require extensions to be self-contained and recommend bundling dependencies as wheels. | HIGH |

### Supporting Libraries

| Library | Version | Purpose | When to Use | Confidence |
|---------|---------|---------|-------------|------------|
| deepdiff | 8.6.1 | Semantic diffing / hash-based comparisons | Use for UI diffs, change detection, and merge assistance; keep JSON as the storage format. | HIGH |
| gitdb | transitive via GitPython | Git object plumbing | Bundle it with GitPython; don’t depend on it separately unless you have a very specific reason. | MEDIUM |
| pytest | 8.x | Unit and integration testing | Use for both pure-Python unit tests and Blender background integration tests. | HIGH |
| pytest-order | 1.x | Ordered integration scenarios | Use only for Blender flow tests that depend on a specific repo/setup sequence. | HIGH |
| ruff | 0.11+ | Linting and formatting | Use in CI and local dev; do not ship it with the add-on. | MEDIUM |

### Development Tools

| Tool | Purpose | Notes | Confidence |
|------|---------|-------|------------|
| Blender background test runner (`--factory-startup --background --python tests/runner.py`) | End-to-end test host | Best fit for validating real bpy behavior, add-on registration, and repo workflow in a clean Blender session. | HIGH |
| Blender extension wheel bundler | Packaging | Build platform-specific extension zips when needed; put pure-Python deps under `./wheels/` and list them in the manifest. | HIGH |
| Git CLI | Troubleshooting / fallback | Still useful to verify GitPython behavior and to debug edge cases outside the add-on. | HIGH |

## Installation

```bash
# Runtime
# Do not pip-install into the add-on at user runtime.
# Bundle dependencies as wheels and ship them in the Blender extension.

# Dev
python -m pip install pytest pytest-order ruff
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative | Confidence |
|-------------|-------------|-------------------------|------------|
| GitPython + system Git | pygit2 | Only if you need libgit2-specific APIs and can accept compiled wheels plus extra binary maintenance. | MEDIUM |
| stdlib `json` | `orjson` | Only if profiling proves JSON write speed is a bottleneck; otherwise the extra wheel cost is not worth it. | HIGH |
| Bundled wheels | Runtime `pip install` | Never for end users; only acceptable in dev tooling. | HIGH |

## What NOT to Use

| Avoid | Why | Use Instead | Confidence |
|-------|-----|-------------|------------|
| Runtime `pip install` inside the add-on | Breaks Blender’s self-contained extension model and can fail under offline / restricted environments. | Bundle dependencies as wheels in `./wheels/` and declare them in `blender_manifest.toml`. | HIGH |
| `pygit2` as the default Git layer | It is libgit2 bindings, so you inherit a compiled dependency and a bigger cross-platform wheel matrix. | GitPython + system Git. | MEDIUM |
| Binary serialization for history data | It fights the product’s readable-diff goal. | Canonical JSON. | HIGH |
| Touching `bpy` from background threads | Blender APIs are main-thread sensitive. | Do IO/Git work off-thread only; marshal UI/bpy work back through operators/timers. | HIGH |
| Writing repo state into the add-on directory | Blender docs warn extension directories may not be writable and upgrades can wipe local files. | Store state in the project/repo workspace. | HIGH |

## Stack Patterns by Variant

**If you want the safest default:**
- Use GitPython + stdlib JSON + bundled wheels.
- Because it stays close to Blender’s extension model and keeps packaging predictable.

**If JSON write speed becomes a real bottleneck:**
- Add `orjson` as an optional wheel.
- Because the default should stay readable and simple until profiling proves otherwise.

**If remote sync is added later:**
- Gate it behind `bpy.app.online_access` and declare `network` permission.
- Because Blender expects add-ons to respect user online-access settings.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| GitPython 3.1.46 | Blender 4.2+ / bundled Python matching the wheel tag | Pure Python, but it still needs the system `git` executable for real repo operations. |
| deepdiff 8.6.1 | Blender 4.2+ / bundled Python matching the wheel tag | Pure Python, so it is straightforward to bundle. |
| Wheels in `./wheels/` | The target Blender build’s Python ABI | Blender docs use wheel tags like `cp313`; always build wheels for the Blender version you ship. |

## Sources

- https://docs.blender.org/manual/en/dev/advanced/extensions/addons.html — self-contained extensions, internet access, bundled deps
- https://docs.blender.org/manual/en/dev/advanced/extensions/python_wheels.html — wheel bundling, manifest wiring, platform-specific packaging
- https://gitpython.readthedocs.io/en/stable/ — GitPython current docs and API surface
- https://www.pygit2.org/ — pygit2 is libgit2 bindings; useful as the main alternative considered
- `/home/torrin/Data/Repos/Personal/cozystudio.io/gitblocks/requirements.txt` — current runtime dependencies
- `/home/torrin/Data/Repos/Personal/cozystudio.io/gitblocks/blender_manifest.toml` — current Blender extension target and packaging constraints

---
*Stack research for: Cozy Studio*
*Researched: 2026-03-21*
