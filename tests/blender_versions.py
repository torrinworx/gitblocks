"""Shared Blender version resolution and cache helpers."""

from __future__ import annotations

import hashlib
import os
import re
import tarfile
from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, urlopen


ARCHIVE_BASE_URL = "https://download.blender.org/release/"
_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class BlenderVersionError(ValueError):
    pass


@dataclass(frozen=True)
class BlenderVersionInfo:
    version: str
    release_dir: str
    archive_url: str
    checksum_url: str
    cache_root: Path

    @property
    def install_dir(self) -> Path:
        return self.cache_root / self.release_dir / f"blender-{self.version}-linux-x64"

    @property
    def binary_path(self) -> Path:
        return self.install_dir / "blender"

    @property
    def archive_path(self) -> Path:
        return self.cache_root / self.release_dir / f"blender-{self.version}-linux-x64.tar.xz"

    @property
    def checksum_path(self) -> Path:
        return self.cache_root / self.release_dir / f"blender-{self.version}.sha256"


def _normalize_version(version: str) -> str:
    selector = (version or "").strip()
    if not selector:
        raise BlenderVersionError("Blender version selector cannot be empty")
    if selector.lower() == "latest":
        raise BlenderVersionError("Blender version selector must be an explicit version")
    if not _VERSION_RE.match(selector):
        raise BlenderVersionError(f"Invalid Blender version selector: {selector!r}")
    return selector


def _release_dir(version: str) -> str:
    major, minor, _patch = _normalize_version(version).split(".")
    return f"Blender{major}.{minor}"


def archive_url_for_version(version: str) -> str:
    normalized = _normalize_version(version)
    release_dir = _release_dir(normalized)
    filename = f"blender-{normalized}-linux-x64.tar.xz"
    return f"{ARCHIVE_BASE_URL}{release_dir}/{filename}"


def checksum_url_for_version(version: str) -> str:
    normalized = _normalize_version(version)
    release_dir = _release_dir(normalized)
    filename = f"blender-{normalized}.sha256"
    return f"{ARCHIVE_BASE_URL}{release_dir}/{filename}"


def cache_root() -> Path:
    override = os.environ.get("GITBLOCKS_BLENDER_CACHE_DIR", "").strip()
    return Path(override).expanduser() if override else Path.home() / ".cache" / "gitblocks" / "blender"


def resolve_version(version: str, cache_dir: Path | None = None) -> BlenderVersionInfo:
    normalized = _normalize_version(version)
    root = Path(cache_dir) if cache_dir is not None else cache_root()
    return BlenderVersionInfo(
        version=normalized,
        release_dir=_release_dir(normalized),
        archive_url=archive_url_for_version(normalized),
        checksum_url=checksum_url_for_version(normalized),
        cache_root=root.expanduser(),
    )


def installed_versions(cache_dir: Path | None = None) -> list[str]:
    root = Path(cache_dir) if cache_dir is not None else cache_root()
    if not root.exists():
        return []
    versions = []
    for archive_dir in sorted(root.glob("Blender*")):
        if not archive_dir.is_dir():
            continue
        for install_dir in sorted(archive_dir.glob("blender-*-linux-x64")):
            if (install_dir / "blender").exists():
                version = install_dir.name.removeprefix("blender-").removesuffix("-linux-x64")
                versions.append(version)
    return sorted(versions)


def _download_text(url: str) -> str:
    request = Request(url, headers=_REQUEST_HEADERS)
    with urlopen(request) as response:
        return response.read().decode("utf-8")


def _download_file(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers=_REQUEST_HEADERS)
    with urlopen(request) as response, destination.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    return destination


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _expected_checksum(checksum_text: str, archive_name: str) -> str:
    for line in checksum_text.strip().splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[-1] == archive_name:
            return parts[0].strip()
    first_line = checksum_text.strip().splitlines()[0]
    return first_line.split()[0].strip()


def _verify_checksum(archive_path: Path, checksum_text: str) -> None:
    expected = _expected_checksum(checksum_text, archive_path.name)
    actual = _sha256(archive_path)
    if actual != expected:
        raise BlenderVersionError(
            f"Checksum mismatch for {archive_path.name}: expected {expected}, got {actual}"
        )


def _extract_archive(archive_path: Path, install_dir: Path) -> None:
    install_dir.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, mode="r:xz") as archive:
        archive.extractall(path=install_dir.parent)


def ensure_installed(version: str, cache_dir: Path | None = None) -> Path:
    info = resolve_version(version, cache_dir=cache_dir)
    if info.binary_path.exists():
        return info.binary_path

    checksum_text = _download_text(info.checksum_url)
    archive_path = _download_file(info.archive_url, info.archive_path)
    _verify_checksum(archive_path, checksum_text)
    _extract_archive(archive_path, info.install_dir)

    if not info.binary_path.exists():
        raise BlenderVersionError(f"Blender binary was not extracted to {info.binary_path}")
    return info.binary_path
