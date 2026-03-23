---
phase: 03-multi-version-blender-test-harness
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/blender_versions.py
  - tests/unit/test_blender_versions.py
autonomous: true
requirements: [TEST-01, TEST-02]
must_haves:
  truths:
    - "The harness can resolve a Blender version into an official archive URL and checksum URL"
    - "Downloaded Blender builds are cached under a stable local versioned directory"
    - "Repeated resolution reuses the cache instead of changing the install path"
  artifacts:
    - path: tests/blender_versions.py
      provides: "Shared Blender version registry, URL, checksum, and cache helpers"
    - path: tests/unit/test_blender_versions.py
      provides: "Resolver and cache behavior coverage"
  key_links:
    - from: tests/blender_versions.py
      to: https://download.blender.org/release/
      via: "official archive URL construction"
    - from: tests/blender_versions.py
      to: tests/unit/test_blender_versions.py
      via: "shared helper contract under test"
---

<objective>
Define the Blender version registry and cache/download contract so the harness can fetch official releases predictably.

Purpose: This gives later plans one shared source of truth for version selection, download URLs, checksum validation, and cache layout.
Output: A reusable helper module plus focused unit tests for version resolution and cache behavior.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/03-multi-version-blender-test-harness/03-RESEARCH.md
@test.py
@tests/runner.py
@.env.example

<interfaces>
From `test.py`:
```python
def load_env(env_path: Path):
def read_env(primary: str, default: str) -> str:
def main():
```

From `tests/runner.py`:
```python
def ensure_pytest_installed():
def parse_requirements(path: Path):
def disable_addon(name: str):
def remove_existing_addons(name: str):
def sanitize_target_directory(target: Path):
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Write the Blender version resolver contract</name>
  <files>tests/unit/test_blender_versions.py, tests/blender_versions.py</files>
  <read_first>
    - tests/runner.py
    - test.py
    - .env.example
    - .planning/phases/03-multi-version-blender-test-harness/03-RESEARCH.md
  </read_first>
  <behavior>
    - Test that version `5.1.0` maps to `https://download.blender.org/release/Blender5.1/blender-5.1.0-linux-x64.tar.xz`
    - Test that the checksum URL for the same version ends with `blender-5.1.0.sha256`
    - Test that the cache root defaults to `~/.cache/gitblocks/blender` unless `GITBLOCKS_BLENDER_CACHE_DIR` overrides it
    - Test that invalid or empty version selectors raise a clear error instead of silently guessing
  </behavior>
  <action>Create `tests/unit/test_blender_versions.py` first with failing expectations, then implement `tests/blender_versions.py` with the helper functions and dataclass/structs needed to satisfy the contract. Keep the helper standard-library only: `pathlib`, `os`, `hashlib`, `tarfile`, and `urllib.request` are fine; avoid adding third-party dependencies just for version management.</action>
  <acceptance_criteria>
    - `tests/blender_versions.py` exports helpers for archive URL, checksum URL, cache root, and version resolution
    - `pytest tests/unit/test_blender_versions.py -q` passes
    - The helper uses the official Blender archive base and does not hardcode a single installed path
  </acceptance_criteria>
  <verify>python3 -m pytest tests/unit/test_blender_versions.py -q</verify>
  <done>The repo has a shared version/cache contract that later runner changes can import without guessing.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Add cache reuse and checksum-verified download behavior</name>
  <files>tests/blender_versions.py, tests/unit/test_blender_versions.py</files>
  <read_first>
    - tests/blender_versions.py
    - tests/unit/test_blender_versions.py
    - .planning/phases/03-multi-version-blender-test-harness/03-RESEARCH.md
  </read_first>
  <behavior>
    - Test that an existing cached install is returned without downloading again
    - Test that the downloader verifies the official `.sha256` file before extraction
    - Test that installed versions are listed from the cache in a deterministic order
    - Test that the extracted binary path is stable for the same version and cache root
  </behavior>
  <action>Implement the download/install path in `tests/blender_versions.py` so it fetches the official archive, verifies the checksum, extracts to the versioned cache directory, and returns the Blender binary path. Preserve the single-version fallback behavior by treating the cache as an addition to, not a replacement for, `GITBLOCKS_BLENDER_BIN`.</action>
  <acceptance_criteria>
    - A missing version is downloaded once and then served from cache on the next resolution
    - `.sha256` verification fails loudly on checksum mismatch
    - The cache directory shape is stable and version-scoped
  </acceptance_criteria>
  <verify>python3 -m pytest tests/unit/test_blender_versions.py -q</verify>
  <done>The harness can download, verify, and reuse Blender archives from the official source.</done>
</task>

</tasks>

<verification>
- Unit tests prove URL generation, cache layout, and checksum validation.
- The helper remains importable from the root harness without requiring Blender to be running.
</verification>

<success_criteria>
- The phase has a single shared version/cache contract for later harness wiring.
- Official Blender downloads are addressed through stable release and checksum URLs.
- Cache reuse is deterministic and independent of the current working directory.
</success_criteria>

<output>
After completion, create `.planning/phases/03-multi-version-blender-test-harness/03-multi-version-blender-test-harness-01-SUMMARY.md`
</output>
