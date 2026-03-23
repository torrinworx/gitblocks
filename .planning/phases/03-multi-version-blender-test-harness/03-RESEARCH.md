---
phase: 03-multi-version-blender-test-harness
type: research
status: complete
tags: [blender, testing, harness, download, cache]
---

# Phase 03 Research

## Sources

- Blender previous versions page: every released Blender version is available for download.
- Blender release notes page: current stable and LTS releases are published on predictable versioned paths.
- Official archive search results: `download.blender.org/release/Blender5.1/` exposes release tarballs plus `.sha256` / `.md5` files.

## Findings

- Official archive base: `https://download.blender.org/release/`.
- Release directories are versioned by major/minor, eg `Blender5.1`.
- Linux release archives use the `blender-{full_version}-linux-x64.tar.xz` naming pattern.
- Checksum files are published next to the archives, so the harness can verify downloads before unpacking.
- The existing harness already prefers a single `GITBLOCKS_BLENDER_BIN` from `.env`, so the new system should keep that as the highest-priority fallback.

## Implications

- Add a version resolver helper that both `test.py` and `tests/runner.py` can share.
- Introduce cache-root and version-selector env vars instead of replacing the existing path-based workflow.
- Validate downloads against official checksum files before extraction.
