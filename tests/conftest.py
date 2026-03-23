import importlib
from pathlib import Path

import pytest
from .helpers import enable_addon, init_git_repo_for_test

try:
    import bpy  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - Blender-only dependency
    bpy = None


ADDON_MODULE = "gitblocks_addon"


@pytest.fixture(scope="session")
def addon_enabled():
    if bpy is None:
        pytest.skip("Blender bpy module is not available")
    enable_addon(ADDON_MODULE)
    return importlib.import_module(ADDON_MODULE)


@pytest.fixture(scope="session")
def ui_module():
    return importlib.import_module(f"{ADDON_MODULE}.ui")


@pytest.fixture(scope="session")
def git_repo(addon_enabled, ui_module):
    return init_git_repo_for_test(ui_module)
