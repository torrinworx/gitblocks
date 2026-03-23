import importlib

import bpy
import pytest

ADDON_MODULE = "gitblocks_addon"

expected_ops = [
    "gitblocks.setup_project",
    "gitblocks.commit",
    "gitblocks.checkout_commit",
    "gitblocks.checkout_branch",
    "gitblocks.reapply_parked_changes",
    "gitblocks.merge",
    "gitblocks.rebase",
    "gitblocks.resolve_conflict",
    "gitblocks.resolve_conflict_version",
    "gitblocks.run_diagnostics",
    "gitblocks.select_block",
    "gitblocks.add_file",
    "gitblocks.unstage_file",
    "gitblocks.add_group",
    "gitblocks.unstage_group",
    "gitblocks.revert_change",
    "gitblocks.install_deps",
]
expected_panels = [
    "GITBLOCKS_PT_main",
    "GITBLOCKS_PT_changes",
    "GITBLOCKS_PT_history",
    "GITBLOCKS_PT_branches",
    "GITBLOCKS_PT_conflicts",
]


@pytest.mark.order(3)
def test_all_gitblocks_ui_classes_registered():
    assert (
        ADDON_MODULE in bpy.context.preferences.addons
    ), f"{ADDON_MODULE} must be enabled before running UI registration tests."

    importlib.import_module(f"{ADDON_MODULE}.ui")

    missing_ops = [
        op for op in expected_ops if not hasattr(bpy.ops.gitblocks, op.split(".")[-1])
    ]
    assert not missing_ops, f"Missing operators: {missing_ops}"

    missing_panels = [pid for pid in expected_panels if not hasattr(bpy.types, pid)]
    assert not missing_panels, f"Missing panels: {missing_panels}"
    assert hasattr(bpy.types.WindowManager, "gitblocks_commit_message")

    for pid in expected_panels:
        panel_cls = getattr(bpy.types, pid)
        assert hasattr(panel_cls, "draw"), f"Panel {pid} has no draw() method"
