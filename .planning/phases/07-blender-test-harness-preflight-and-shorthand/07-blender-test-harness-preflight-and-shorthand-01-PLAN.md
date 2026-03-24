---
phase: 07-blender-test-harness-preflight-and-shorthand
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - tests/unit/test_blender_versions.py
  - tests/blender_versions.py
autonomous: true
requirements: [TEST-11]
must_haves:
  truths:
    - "Unsupported Blender version selections are rejected before any Blender subprocess launches."
    - "Supported Blender selections still resolve normally through the existing cache/download flow."
    - "The failure message names the selected unsupported version(s) and the supported matrix."
  artifacts:
    - path: tests/blender_versions.py
      provides: "Compatibility result dataclass and preflight helper for selected Blender versions"
      min_lines: 300
    - path: tests/unit/test_blender_versions.py
      provides: "Deterministic coverage for supported, unsupported, and mixed-version compatibility results"
      min_lines: 220
  key_links:
    - from: tests/blender_versions.py
      to: test.py
      via: "shared compatibility helper used before run planning"
      pattern: "check_blender_compatibility"
    - from: tests/unit/test_blender_versions.py
      to: tests/blender_versions.py
      via: "exact result/message assertions"
      pattern: "BlenderCompatibilityResult|check_blender_compatibility"
---

<objective>
Make unsupported Blender selections fail fast before any matrix work begins, while keeping the current supported-version install/download flow unchanged.

Purpose: This gives the outer harness a clear compatibility gate instead of a late subprocess failure.
Output: A compatibility result helper in `tests/blender_versions.py` and pinned unit coverage in `tests/unit/test_blender_versions.py`.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
@.env.example
@README.md
@.planning/phases/06-testing-runner-progress-and-logging/06-testing-runner-progress-and-logging-SUMMARY.md

<interfaces>
From `tests/blender_versions.py`:

```python
class BlenderVersionError(ValueError)

@dataclass(frozen=True)
class BlenderInstallEvent:
    kind: str
    version: str
    archive_name: str | None = None
    detail: str | None = None
    bytes_downloaded: int | None = None
    total_bytes: int | None = None
    path: Path | None = None

@dataclass(frozen=True)
class BlenderVersionInfo:
    version: str
    release_dir: str
    archive_url: str
    checksum_url: str
    cache_root: Path

def resolve_version(version: str, cache_dir: Path | None = None) -> BlenderVersionInfo
def ensure_installed(version: str, cache_dir: Path | None = None, progress=None) -> Path

SUPPORTED_BLENDER_VERSIONS = ("4.1.0", "4.5.1", "5.1.0")

@dataclass(frozen=True)
class BlenderCompatibilityResult:
    selected_versions: tuple[str, ...]
    supported_versions: tuple[str, ...]
    unsupported_versions: tuple[str, ...]
    ok: bool
    message: str

def check_blender_compatibility(selected_versions: Sequence[str], supported_versions: Sequence[str] | None = None) -> BlenderCompatibilityResult
```
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Write the compatibility contract tests first</name>
  <files>tests/unit/test_blender_versions.py</files>
  <read_first>
    - tests/unit/test_blender_versions.py
    - tests/blender_versions.py
    - .env.example
    - README.md
    - .planning/phases/06-testing-runner-progress-and-logging/06-testing-runner-progress-and-logging-SUMMARY.md
  </read_first>
  <behavior>
    - Test 1: a supported list such as `("4.1.0", "5.1.0")` must be treated as compatible.
    - Test 2: a single unsupported version such as `"4.0.2"` must fail and mention both the bad version and the supported matrix `4.1.0, 4.5.1, 5.1.0`.
    - Test 3: a mixed list such as `("4.1.0", "4.0.2")` must report only the unsupported entry and still preserve the original selection order.
  </behavior>
  <action>
    Add failing unit tests only. Define the exact contract for `BlenderCompatibilityResult` and `check_blender_compatibility(...)` using the supported Blender matrix that already appears in `.env.example` (`4.1.0`, `4.5.1`, `5.1.0`). Do not implement the helper yet.
  </action>
  <acceptance_criteria>
    - `tests/unit/test_blender_versions.py` contains explicit assertions for supported, unsupported, and mixed version lists.
    - The test file names the supported matrix exactly as `4.1.0, 4.5.1, 5.1.0`.
    - The new tests fail because the compatibility helper is not implemented yet.
  </acceptance_criteria>
  <verify>
    <automated>python -m pytest tests/unit/test_blender_versions.py -q</automated>
  </verify>
  <done>The compatibility contract is locked by red tests that describe the exact supported-versus-unsupported behavior.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Implement the compatibility helper to satisfy the tests</name>
  <files>tests/blender_versions.py</files>
  <read_first>
    - tests/blender_versions.py
    - tests/unit/test_blender_versions.py
    - .env.example
    - README.md
  </read_first>
  <behavior>
    - Test 1: `check_blender_compatibility(("4.1.0", "5.1.0"))` must return `ok=True` and no unsupported versions.
    - Test 2: `check_blender_compatibility(("4.0.2",))` must return `ok=False` and a human-readable message that names `4.0.2` and the supported matrix.
    - Test 3: mixed selections must keep the original order in `selected_versions` while isolating only the unsupported entries in `unsupported_versions`.
  </behavior>
  <action>
    Add `SUPPORTED_BLENDER_VERSIONS = ("4.1.0", "4.5.1", "5.1.0")`, a frozen `BlenderCompatibilityResult` dataclass, and `check_blender_compatibility(...)` in `tests/blender_versions.py`. The helper should default to the supported matrix above, preserve the original selection order, and produce a single plain-English failure message that the outer harness can print verbatim. Keep `GITBLOCKS_BLENDER_BIN` out of this helper so direct-binary overrides can bypass the preflight later.
  </action>
  <acceptance_criteria>
    - `tests/blender_versions.py` exports `SUPPORTED_BLENDER_VERSIONS`, `BlenderCompatibilityResult`, and `check_blender_compatibility`.
    - The helper returns `ok=True` for `4.1.0` / `4.5.1` / `5.1.0` selections.
    - The helper returns `ok=False` and a readable message for unsupported selections.
  </acceptance_criteria>
  <verify>
    <automated>python -m pytest tests/unit/test_blender_versions.py -q</automated>
  </verify>
  <done>The compatibility helper exists, passes the supported-version cases, and emits the exact failure text the harness will reuse.</done>
</task>

</tasks>

<verification>
Run the compatibility unit module and confirm it passes with the supported matrix hard-coded in the helper.
</verification>

<success_criteria>
- `tests/blender_versions.py` can classify supported and unsupported Blender selections without starting Blender.
- `tests/unit/test_blender_versions.py` pins the compatibility contract with deterministic assertions.
- The supported matrix is explicit and matches the phase docs/examples.
</success_criteria>

<output>
After completion, create `.planning/phases/07-blender-test-harness-preflight-and-shorthand/07-blender-test-harness-preflight-and-shorthand-SUMMARY.md`
</output>
