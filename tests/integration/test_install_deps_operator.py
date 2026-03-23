import importlib

import bpy
import pytest

from ..helpers import ensure_install_operator, wait_for_install_finished

ADDON_MODULE = "gitblocks_addon"


@pytest.mark.order(2)
@pytest.mark.install
def test_install_deps_operator():
    if ADDON_MODULE not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module=ADDON_MODULE)

    gitblocks = importlib.import_module(ADDON_MODULE)
    ensure_install_operator(gitblocks)

    gitblocks.MISSING_DEPENDENCIES[:] = gitblocks.check_dependencies()

    assert hasattr(bpy.ops.gitblocks, "install_deps")
    result = bpy.ops.gitblocks.install_deps("EXEC_DEFAULT")
    assert "RUNNING_MODAL" in result or "FINISHED" in result, \
        f"install_deps returned {result}"

    completed = wait_for_install_finished(gitblocks, timeout=300.0)
    assert completed, "Dependency install did not complete in time"

    assert gitblocks.DEPENDENCIES_INSTALLED, "Dependencies should report as installed"
    assert not gitblocks.MISSING_DEPENDENCIES, \
        f"Still missing after install: {gitblocks.MISSING_DEPENDENCIES}"
    assert gitblocks.auto_load_was_registered
