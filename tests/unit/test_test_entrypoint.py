import json
from datetime import UTC, datetime
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

    summaries = iter(
        [
            {"phases": [{"stage": "install", "passed": 2, "failed": 0, "skipped": 0, "selected": 2, "deselected": 40, "exit_code": 0}]},
            {"phases": [{"stage": "test", "passed": 80, "failed": 0, "skipped": 0, "selected": 80, "deselected": 2, "exit_code": 0}]},
        ]
    )

    def fake_call(*args, **kwargs):
        run = runs[fake_call.calls]
        run.test_dir.mkdir(parents=True, exist_ok=True)
        (run.test_dir / harness._MODULE.SUMMARY_FILENAME).write_text(
            json.dumps(next(summaries)),
            encoding="utf-8",
        )
        fake_call.calls += 1
        return 0

    fake_call.calls = 0

    monkeypatch.setattr(harness._MODULE, "plan_blender_runs", lambda *args, **kwargs: runs)
    monkeypatch.setattr(harness._MODULE.subprocess, "call", fake_call)
    monkeypatch.setattr("sys.argv", ["test.py"])

    with pytest.raises(SystemExit) as exc:
        harness.main()

    assert exc.value.code == 0

    output = capsys.readouterr().out
    assert "GitBlocks | Blender 5.1.0" in output
    assert "GitBlocks | Blender 5.0.1" in output
    assert "Matrix Summary" in output
    assert "5.1.0        PASS install P:2 F:0 S:0" in output
    assert "5.0.1        PASS test P:80 F:0 S:0" in output
    assert "--blender-version" not in output


def test_main_keeps_running_after_a_failing_blender_version(monkeypatch, tmp_path, capsys):
    first_bin = tmp_path / "5.1.0" / "blender"
    first_bin.parent.mkdir(parents=True)
    first_bin.write_text("ok", encoding="utf-8")

    second_bin = tmp_path / "5.0.1" / "blender"
    second_bin.parent.mkdir(parents=True, exist_ok=True)
    second_bin.write_text("ok", encoding="utf-8")

    runs = [
        harness.BlenderRun(blender_bin=first_bin, test_dir=tmp_path / "tests" / "5.1.0", version="5.1.0"),
        harness.BlenderRun(blender_bin=second_bin, test_dir=tmp_path / "tests" / "5.0.1", version="5.0.1"),
    ]

    calls = []

    def fake_call(*args, **kwargs):
        run = runs[len(calls)]
        run.test_dir.mkdir(parents=True, exist_ok=True)
        summary = (
            {
                "phases": [
                    {
                        "stage": "test",
                        "passed": 0,
                        "failed": 1,
                        "skipped": 0,
                        "selected": 1,
                        "deselected": 0,
                        "exit_code": 1,
                        "failures": [
                            {
                                "nodeid": "tests/unit/test_example.py::test_bad",
                                "message": "AssertionError: boom",
                                "longreprtext": "AssertionError: boom\nCaptured stdout call\nhelpful detail",
                            }
                        ],
                    }
                ]
            }
            if run.version == "5.1.0"
            else {"phases": []}
        )
        (run.test_dir / harness._MODULE.SUMMARY_FILENAME).write_text(json.dumps(summary), encoding="utf-8")
        calls.append(run.version)
        return 1 if run.version == "5.1.0" else 0

    monkeypatch.setattr(harness._MODULE, "plan_blender_runs", lambda *args, **kwargs: runs)
    monkeypatch.setattr(harness._MODULE.subprocess, "call", fake_call)
    monkeypatch.setattr("sys.argv", ["test.py"])

    with pytest.raises(SystemExit) as exc:
        harness.main()

    assert exc.value.code == 1
    assert calls == ["5.1.0", "5.0.1"]

    output = capsys.readouterr().out
    assert "GitBlocks | Blender 5.1.0" in output
    assert "GitBlocks | Blender 5.0.1" in output
    assert "Matrix Summary" in output
    assert "FAILURE DIGEST" in output
    assert "5.1.0" in output
    assert "- example.bad :: AssertionError: boom" in output


def test_log_path_for_run_is_timestamped_and_rooted_in_logs(tmp_path):
    run = harness.BlenderRun(blender_bin=tmp_path / "blender", test_dir=tmp_path / "tests", version="5.1.0")
    started_at = datetime(2026, 3, 24, 0, 0, 0, tzinfo=UTC)

    log_file = harness._MODULE.log_path_for_run(tmp_path, run, started_at)

    assert log_file == tmp_path / "logs" / "gitblocks-test-2026-03-24_00-00-00-5.1.0.log"
    assert log_file.parent.name == "logs"


def test_build_blender_command_can_take_a_log_file(tmp_path):
    run = harness.BlenderRun(blender_bin=tmp_path / "blender", test_dir=tmp_path / "tests", version="5.1.0")
    log_file = tmp_path / "logs" / "gitblocks-test-2026-03-24_00-00-00-5.1.0.log"

    command = harness.build_blender_command(tmp_path, run, log_file=log_file)

    assert "--log-file" in command
    assert str(log_file) in command


def test_main_keeps_single_binary_fallback_without_version_label(monkeypatch, tmp_path, capsys):
    blender_bin = tmp_path / "blender"
    blender_bin.write_text("ok", encoding="utf-8")

    runs = [harness.BlenderRun(blender_bin=blender_bin, test_dir=tmp_path / "tests", version=None)]

    def fake_call(*args, **kwargs):
        runs[0].test_dir.mkdir(parents=True, exist_ok=True)
        (runs[0].test_dir / harness._MODULE.SUMMARY_FILENAME).write_text(
            json.dumps({"phases": []}),
            encoding="utf-8",
        )
        return 0

    monkeypatch.setattr(harness._MODULE, "plan_blender_runs", lambda *args, **kwargs: runs)
    monkeypatch.setattr(harness._MODULE.subprocess, "call", fake_call)
    monkeypatch.setattr("sys.argv", ["test.py"])

    with pytest.raises(SystemExit) as exc:
        harness.main()

    assert exc.value.code == 0

    output = capsys.readouterr().out
    assert "GitBlocks | Blender" in output
    assert "--blender-version" not in output


def test_build_blender_command_reduces_blender_log_noise(tmp_path):
    run = harness.BlenderRun(blender_bin=tmp_path / "blender", test_dir=tmp_path / "tests", version="5.1.0")

    command = harness.build_blender_command(tmp_path, run)

    assert "--log-level" in command
    assert "0" in command


def test_no_selector_keeps_single_binary_fallback(tmp_path):
    runs = harness.plan_blender_runs(
        [],
        addon_root=tmp_path,
        env={"GITBLOCKS_TEST_DIR": str(tmp_path / "tests")},
        resolver=lambda version: tmp_path / version / "blender",
    )

    assert len(runs) == 1
    assert runs[0].version is None
