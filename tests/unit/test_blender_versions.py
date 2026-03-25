from pathlib import Path

import pytest

from tests.blender_versions import (
    BlenderCompatibilityResult,
    BlenderVersionError,
    BlenderInstallEvent,
    archive_url_for_version,
    cache_root,
    checksum_url_for_version,
    check_blender_compatibility,
    ensure_installed,
    installed_versions,
    SUPPORTED_BLENDER_VERSIONS,
    resolve_version,
)


def test_version_maps_to_official_archive_url():
    assert archive_url_for_version("5.1.0") == (
        "https://download.blender.org/release/Blender5.1/"
        "blender-5.1.0-linux-x64.tar.xz"
    )


def test_checksum_url_uses_matching_release_file():
    assert checksum_url_for_version("5.1.0").endswith("blender-5.1.0.sha256")


def test_cache_root_defaults_and_can_be_overridden(monkeypatch, tmp_path):
    monkeypatch.delenv("GITBLOCKS_BLENDER_CACHE_DIR", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert cache_root() == Path(tmp_path) / ".cache" / "gitblocks" / "blender"

    custom = tmp_path / "custom-cache"
    monkeypatch.setenv("GITBLOCKS_BLENDER_CACHE_DIR", str(custom))
    assert cache_root() == custom


@pytest.mark.parametrize("selector", ["", "   ", "latest"])
def test_invalid_version_selectors_raise_clear_error(selector):
    with pytest.raises(BlenderVersionError, match="version"):
        resolve_version(selector)


def test_existing_cache_is_returned_without_downloading(monkeypatch, tmp_path):
    info = resolve_version("5.1.0", cache_dir=tmp_path)
    info.binary_path.parent.mkdir(parents=True, exist_ok=True)
    info.binary_path.write_text("blender-binary", encoding="utf-8")

    monkeypatch.setattr("tests.blender_versions._download_text", lambda *_: (_ for _ in ()).throw(AssertionError("download_text should not be called")))
    monkeypatch.setattr("tests.blender_versions._download_file", lambda *_: (_ for _ in ()).throw(AssertionError("download_file should not be called")))

    assert info.binary_path == info.binary_path
    assert info.binary_path.exists()
    assert info.binary_path == resolve_version("5.1.0", cache_dir=tmp_path).binary_path


def test_ensure_installed_emits_download_progress_and_completion(monkeypatch, tmp_path):
    events = []
    info = resolve_version("5.1.0", cache_dir=tmp_path)
    checksum_text = f"deadbeef  {info.archive_path.name}\n"

    class FakeResponse:
        def __init__(self, payload: bytes):
            self._payload = payload
            self._offset = 0
            self.headers = {"Content-Length": str(len(payload))}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self, size=-1):
            if size is None or size < 0:
                size = len(self._payload) - self._offset
            if self._offset >= len(self._payload):
                return b""
            chunk = self._payload[self._offset : self._offset + size]
            self._offset += len(chunk)
            return chunk

    def fake_urlopen(request):
        if request.full_url.endswith(".sha256"):
            return FakeResponse(checksum_text.encode("utf-8"))
        return FakeResponse(b"archive-bytes")

    def fake_extract(archive_path, install_dir):
        install_dir.mkdir(parents=True, exist_ok=True)
        (install_dir / "blender").write_text("ok", encoding="utf-8")

    monkeypatch.setattr("tests.blender_versions.urlopen", fake_urlopen)
    monkeypatch.setattr("tests.blender_versions._sha256", lambda *_: "deadbeef")
    monkeypatch.setattr("tests.blender_versions._extract_archive", fake_extract)

    assert ensure_installed("5.1.0", cache_dir=tmp_path, progress=events.append).name == "blender"
    assert events[0] == BlenderInstallEvent(
        kind="start",
        version="5.1.0",
        archive_name=info.archive_path.name,
        detail="checksum",
    )
    assert any(event.kind == "progress" for event in events)
    assert events[-1] == BlenderInstallEvent(
        kind="complete",
        version="5.1.0",
        archive_name=info.archive_path.name,
        detail="ready",
        path=info.binary_path,
    )


def test_ensure_installed_emits_cache_hit_without_downloading(monkeypatch, tmp_path):
    info = resolve_version("5.1.0", cache_dir=tmp_path)
    info.binary_path.parent.mkdir(parents=True, exist_ok=True)
    info.binary_path.write_text("blender-binary", encoding="utf-8")

    monkeypatch.setattr("tests.blender_versions._download_text", lambda *_: (_ for _ in ()).throw(AssertionError("download_text should not be called")))
    monkeypatch.setattr("tests.blender_versions._download_file", lambda *_: (_ for _ in ()).throw(AssertionError("download_file should not be called")))

    events = []
    assert ensure_installed("5.1.0", cache_dir=tmp_path, progress=events.append) == info.binary_path
    assert events == [
        BlenderInstallEvent(
            kind="cache-hit",
            version="5.1.0",
            archive_name=info.archive_path.name,
            detail="ready",
            path=info.binary_path,
        )
    ]


def test_checksum_is_verified_before_extraction(monkeypatch, tmp_path):
    info = resolve_version("5.1.0", cache_dir=tmp_path)
    call_order = []

    monkeypatch.setattr("tests.blender_versions._download_text", lambda url, **kwargs: call_order.append(("checksum", url, kwargs)) or "deadbeef  blender-5.1.0-linux-x64.tar.xz")
    monkeypatch.setattr("tests.blender_versions._download_file", lambda url, destination, **kwargs: call_order.append(("archive", url, destination, kwargs)) or destination)
    monkeypatch.setattr("tests.blender_versions._verify_checksum", lambda archive_path, checksum_text: call_order.append(("verify", archive_path, checksum_text)))

    def fake_extract(archive_path, install_dir):
        call_order.append(("extract", archive_path, install_dir))
        install_dir.mkdir(parents=True, exist_ok=True)
        (install_dir / "blender").write_text("ok", encoding="utf-8")

    monkeypatch.setattr("tests.blender_versions._extract_archive", fake_extract)
    monkeypatch.setattr("tests.blender_versions._sha256", lambda path: "deadbeef")

    assert ensure_installed("5.1.0", cache_dir=tmp_path).name == "blender"
    assert [step[0] for step in call_order] == ["checksum", "archive", "verify", "extract"]


def test_checksum_matching_uses_the_requested_archive_name(tmp_path, monkeypatch):
    info = resolve_version("4.1.0", cache_dir=tmp_path)

    checksum_text = (
        "b0d7286f79b54a9aa0c5cfb1c36e85aa674bae1ca776f8e6d52b5a22c6626598  "
        "blender-4.1.0-windows-x64.msix\n"
        "d2ac5390f4a9cb9416c8eb23bdd8fa8e49e68165a889575fd8f56563f5cccaf1  "
        "blender-4.1.0-linux-x64.tar.xz\n"
    )

    monkeypatch.setattr("tests.blender_versions._download_text", lambda *_ , **__: checksum_text)
    monkeypatch.setattr("tests.blender_versions._download_file", lambda *_ , **__: info.archive_path)
    monkeypatch.setattr("tests.blender_versions._extract_archive", lambda archive_path, install_dir: (install_dir.mkdir(parents=True, exist_ok=True), (install_dir / "blender").write_text("ok", encoding="utf-8")))
    monkeypatch.setattr("tests.blender_versions._sha256", lambda *_: "d2ac5390f4a9cb9416c8eb23bdd8fa8e49e68165a889575fd8f56563f5cccaf1")

    assert ensure_installed("4.1.0", cache_dir=tmp_path).name == "blender"


def test_installed_versions_are_sorted_deterministically(tmp_path):
    first = tmp_path / "Blender5.0" / "blender-5.0.1-linux-x64"
    second = tmp_path / "Blender5.1" / "blender-5.1.0-linux-x64"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    (first / "blender").write_text("ok", encoding="utf-8")
    (second / "blender").write_text("ok", encoding="utf-8")

    assert installed_versions(tmp_path) == ["5.0.1", "5.1.0"]


def test_resolved_binary_path_is_stable_for_version_and_cache_root(tmp_path):
    info_one = resolve_version("5.1.0", cache_dir=tmp_path)
    info_two = resolve_version("5.1.0", cache_dir=tmp_path)

    assert info_one.binary_path == info_two.binary_path


def test_supported_blender_versions_are_compatible():
    result = check_blender_compatibility(("4.1.0", "5.1.0"))

    assert result == BlenderCompatibilityResult(
        selected_versions=("4.1.0", "5.1.0"),
        supported_versions=SUPPORTED_BLENDER_VERSIONS,
        unsupported_versions=(),
        ok=True,
        message="All selected Blender versions are supported: 4.1.0, 5.1.0",
    )


def test_unsupported_blender_version_names_the_matrix():
    result = check_blender_compatibility(("4.0.2",))

    assert result == BlenderCompatibilityResult(
        selected_versions=("4.0.2",),
        supported_versions=SUPPORTED_BLENDER_VERSIONS,
        unsupported_versions=("4.0.2",),
        ok=False,
        message=f"Unsupported Blender version(s): 4.0.2. Supported versions: {', '.join(SUPPORTED_BLENDER_VERSIONS)}",
    )


def test_mixed_blender_versions_preserve_selection_order_and_isolate_unsupported_entries():
    result = check_blender_compatibility(("4.1.0", "4.0.2"))

    assert result.selected_versions == ("4.1.0", "4.0.2")
    assert result.unsupported_versions == ("4.0.2",)
    assert result.ok is False
    assert result.message == f"Unsupported Blender version(s): 4.0.2. Supported versions: {', '.join(SUPPORTED_BLENDER_VERSIONS)}"
