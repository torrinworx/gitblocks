from pathlib import Path

from tests import harness


def test_cli_version_wins_over_env_version(tmp_path, monkeypatch):
    monkeypatch.setenv("GITBLOCKS_BLENDER_VERSION", "5.0.1")

    runs = harness.plan_blender_runs(
        ["--blender-version", "5.1.0"],
        addon_root=tmp_path,
        env={"GITBLOCKS_TEST_DIR": str(tmp_path / "tests")},
        resolver=lambda version: tmp_path / version / "blender",
    )

    assert [run.version for run in runs] == ["5.1.0"]


def test_default_fallback_keeps_single_binary_path(tmp_path):
    runs = harness.plan_blender_runs(
        [],
        addon_root=tmp_path,
        env={"GITBLOCKS_TEST_DIR": str(tmp_path / "tests")},
        resolver=lambda version: tmp_path / version / "blender",
    )

    assert len(runs) == 1
    assert runs[0].version is None
    assert runs[0].test_dir == Path(tmp_path / "tests")


def test_version_matrix_creates_one_run_per_version(tmp_path):
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
