from pathlib import Path

import pytest

from tests.blender_versions import (
    BlenderVersionError,
    archive_url_for_version,
    cache_root,
    checksum_url_for_version,
    ensure_installed,
    installed_versions,
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


def test_checksum_is_verified_before_extraction(monkeypatch, tmp_path):
    info = resolve_version("5.1.0", cache_dir=tmp_path)
    call_order = []

    monkeypatch.setattr("tests.blender_versions._download_text", lambda url: call_order.append(("checksum", url)) or "deadbeef  blender-5.1.0-linux-x64.tar.xz")
    monkeypatch.setattr("tests.blender_versions._download_file", lambda url, destination: call_order.append(("archive", url, destination)) or destination)
    monkeypatch.setattr("tests.blender_versions._verify_checksum", lambda archive_path, checksum_text: call_order.append(("verify", archive_path, checksum_text)))

    def fake_extract(archive_path, install_dir):
        call_order.append(("extract", archive_path, install_dir))
        install_dir.mkdir(parents=True, exist_ok=True)
        (install_dir / "blender").write_text("ok", encoding="utf-8")

    monkeypatch.setattr("tests.blender_versions._extract_archive", fake_extract)
    monkeypatch.setattr("tests.blender_versions._sha256", lambda path: "deadbeef")

    assert ensure_installed("5.1.0", cache_dir=tmp_path).name == "blender"
    assert [step[0] for step in call_order] == ["checksum", "archive", "verify", "extract"]


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
