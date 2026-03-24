import shutil
import tempfile
import zipfile
from pathlib import Path

import bpy
import pytest

from tests.helpers import addon_install_root


ADDON_MODULE = "gitblocks_addon"


@pytest.mark.order(0)
@pytest.mark.install
def test_zip_install_addon():
    if ADDON_MODULE in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_disable(module=ADDON_MODULE)

    install_root = addon_install_root()
    if install_root.name == "addons":
        addon_dir = install_root / ADDON_MODULE
        if addon_dir.exists():
            if addon_dir.is_symlink() or addon_dir.is_file():
                addon_dir.unlink(missing_ok=True)
            else:
                shutil.rmtree(addon_dir, ignore_errors=True)
    else:
        for repo in install_root.parent.iterdir():
            addon_dir = repo / ADDON_MODULE
            if addon_dir.exists():
                if addon_dir.is_symlink() or addon_dir.is_file():
                    addon_dir.unlink(missing_ok=True)
                else:
                    shutil.rmtree(addon_dir, ignore_errors=True)

    addon_src = Path(__file__).resolve().parents[2]
    staging_root = Path(tempfile.mkdtemp(prefix="gitblocks_addon_zip_"))
    staging_addon = staging_root / ADDON_MODULE
    shutil.copytree(
        addon_src,
        staging_addon,
        ignore=shutil.ignore_patterns(
            ".git",
            "__pycache__",
            ".pytest_cache",
            "blender",
        ),
    )

    zip_path = staging_root / f"{ADDON_MODULE}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_handle:
        for item in staging_addon.rglob("*"):
            zip_handle.write(item, item.relative_to(staging_root))

    install_result = bpy.ops.preferences.addon_install(
        filepath=str(zip_path), overwrite=True
    )
    assert "FINISHED" in install_result, f"addon_install returned {install_result}"

    enable_result = bpy.ops.preferences.addon_enable(module=ADDON_MODULE)
    assert "FINISHED" in enable_result or "CANCELLED" in enable_result, \
        f"addon_enable returned {enable_result}"

    assert ADDON_MODULE in bpy.context.preferences.addons
    assert hasattr(bpy.ops.gitblocks, "install_deps")
