from pathlib import Path

import pytest

from tests import harness


def test_help_includes_blender_version_flags():
    parser = harness.build_parser()
    help_text = parser.format_help()

    assert "--blender-version" in help_text
    assert "--blender-versions" in help_text


def test_direct_binary_override_wins_over_version_selectors(monkeypatch, tmp_path):
    runs = harness.plan_blender_runs(
        ["--blender-version", "5.1.0"],
        addon_root=tmp_path,
        env={
            "GITBLOCKS_TEST_DIR": str(tmp_path / "tests"),
            "GITBLOCKS_BLENDER_BIN": "/opt/blender/bin/blender",
        },
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


def test_version_resolution_forwards_progress_callback(tmp_path):
    calls = []
    progress = object()

    def resolver(version, progress=None):
        calls.append((version, progress))
        return tmp_path / version / "blender"

    runs = harness.plan_blender_runs(
        ["--blender-version", "5.1.0"],
        addon_root=tmp_path,
        env={"GITBLOCKS_TEST_DIR": str(tmp_path / "tests")},
        resolver=resolver,
        progress=progress,
    )

    assert calls == [("5.1.0", progress)]
    assert runs[0].version == "5.1.0"


def test_main_prints_version_headers_before_each_run(monkeypatch, tmp_path, capsys):
    versioned_bin = tmp_path / "5.1.0" / "blender"
    versioned_bin.parent.mkdir(parents=True)
    versioned_bin.write_text("ok", encoding="utf-8")

    second_bin = tmp_path / "5.0.1" / "blender"
    second_bin.parent.mkdir(parents=True, exist_ok=True)
    second_bin.write_text("ok", encoding="utf-8")

    runs = [
        harness.BlenderRun(blender_bin=versioned_bin, test_dir=tmp_path / "tests" / "5.1.0", version="5.1.0"),
        harness.BlenderRun(blender_bin=second_bin, test_dir=tmp_path / "tests" / "5.0.1", version="5.0.1"),
    ]

    monkeypatch.setattr(harness._MODULE, "plan_blender_runs", lambda *args, **kwargs: runs)
    monkeypatch.setattr(harness._MODULE.subprocess, "call", lambda *args, **kwargs: 0)
    monkeypatch.setattr("sys.argv", ["test.py"])

    with pytest.raises(SystemExit) as exc:
        harness.main()

    assert exc.value.code == 0

    output = capsys.readouterr().out
    assert f"▶ Running Blender 5.1.0 at {versioned_bin}" in output
    assert f"▶ Running Blender 5.0.1 at {second_bin}" in output
    assert "--blender-version 5.1.0" in output
    assert "--blender-version 5.0.1" in output


def test_main_keeps_single_binary_fallback_without_version_label(monkeypatch, tmp_path, capsys):
    blender_bin = tmp_path / "blender"
    blender_bin.write_text("ok", encoding="utf-8")

    runs = [harness.BlenderRun(blender_bin=blender_bin, test_dir=tmp_path / "tests", version=None)]

    monkeypatch.setattr(harness._MODULE, "plan_blender_runs", lambda *args, **kwargs: runs)
    monkeypatch.setattr(harness._MODULE.subprocess, "call", lambda *args, **kwargs: 0)
    monkeypatch.setattr("sys.argv", ["test.py"])

    with pytest.raises(SystemExit) as exc:
        harness.main()

    assert exc.value.code == 0

    output = capsys.readouterr().out
    assert f"▶ Running Blender at {blender_bin}" in output
    assert "--blender-version" not in output


def test_no_selector_keeps_single_binary_fallback(tmp_path):
    runs = harness.plan_blender_runs(
        [],
        addon_root=tmp_path,
        env={"GITBLOCKS_TEST_DIR": str(tmp_path / "tests")},
        resolver=lambda version: tmp_path / version / "blender",
    )

    assert len(runs) == 1
    assert runs[0].version is None
