from pathlib import Path

from tests import harness


def test_help_includes_blender_version_flags():
    parser = harness.build_parser()
    help_text = parser.format_help()

    assert "--blender-version" in help_text
    assert "--blender-versions" in help_text


def test_direct_binary_override_wins_over_version_selectors(monkeypatch, tmp_path):
    monkeypatch.setenv("GITBLOCKS_BLENDER_BIN", "/opt/blender/bin/blender")

    runs = harness.plan_blender_runs(
        ["--blender-version", "5.1.0"],
        addon_root=tmp_path,
        env={"GITBLOCKS_TEST_DIR": str(tmp_path / "tests")},
        resolver=lambda version: tmp_path / version / "blender",
    )

    assert len(runs) == 1
    assert runs[0].blender_bin == Path("/opt/blender/bin/blender")


def test_version_matrix_expands_to_one_run_per_version(tmp_path):
    runs = harness.plan_blender_runs(
        ["--blender-versions", "5.0.1,5.1.0"],
        addon_root=tmp_path,
        env={"GITBLOCKS_TEST_DIR": str(tmp_path / "tests")},
        resolver=lambda version: tmp_path / version / "blender",
    )

    assert [run.version for run in runs] == ["5.0.1", "5.1.0"]
    assert [run.test_dir for run in runs] == [
        tmp_path / "tests" / "5.0.1",
        tmp_path / "tests" / "5.1.0",
    ]


def test_no_selector_keeps_single_binary_fallback(tmp_path):
    runs = harness.plan_blender_runs(
        [],
        addon_root=tmp_path,
        env={"GITBLOCKS_TEST_DIR": str(tmp_path / "tests")},
        resolver=lambda version: tmp_path / version / "blender",
    )

    assert len(runs) == 1
    assert runs[0].version is None
