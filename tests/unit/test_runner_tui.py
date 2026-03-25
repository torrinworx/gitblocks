from types import SimpleNamespace
from io import StringIO

from tests import runner_tui
from tests import runner


def test_stage_banner_is_stable_for_install_and_test_phases():
    assert runner_tui.format_stage_banner("install") == "[ INSTALL ]"
    assert runner_tui.format_stage_banner("test") == "[ TEST ]"


def test_compact_nodeid_keeps_file_test_and_param_case_readable():
    assert (
        runner_tui.compact_nodeid(
            "tests/unit/test_example.py::test_ok[latest]"
        )
        == "example.ok [latest]"
    )


def test_format_progress_grid_uses_unicode_blocks_not_ascii_bar_chars():
    assert runner_tui.format_progress_grid(3, 8) == "⣿⣿⣿⣀⣀⣀⣀⣀"


def test_format_status_mark_uses_colored_heavy_unicode_symbols():
    assert runner_tui.format_status_mark("pass") == "\x1b[32m✔\x1b[0m"
    assert runner_tui.format_status_mark("fail") == "\x1b[31m✖\x1b[0m"
    assert runner_tui.format_status_mark("skip") == "\x1b[33m↷\x1b[0m"


def test_format_matrix_progress_line_includes_version_counts_and_percentage():
    assert (
        runner_tui.format_matrix_progress_line(3, 8, "Blender 4.2.1", 2, 5)
        == "Blender 4.2.1 [2/5] 3/8 37% ⣿⣿⣿⣀⣀⣀⣀⣀"
    )


def test_format_test_footer_shows_colored_status_and_matrix_progress():
    assert (
        runner_tui.format_test_footer(
            "test",
            "tests/unit/test_example.py::test_ok",
            3,
            10,
            3,
            0,
            0,
            current_version="Blender 4.2.1",
            current_run_index=2,
            run_count=5,
        )
        == "TEST    \x1b[32m✔\x1b[0m example.ok | Blender 4.2.1 [2/5] 3/10 30% ⣿⣿⣀⣀⣀⣀⣀⣀"
    )


def test_format_collection_summary_includes_selected_counts():
    assert (
        runner_tui.format_collection_summary(12, 3, 9)
        == "selected 9 of 12 tests (3 deselected)"
    )


def test_tui_plugin_emits_stage_header_collection_progress_and_summary():
    stream = StringIO()
    plugin = runner_tui.build_pytest_tui(
        "install",
        stream=stream,
        current_version="Blender 4.2.1",
        current_run_index=2,
        run_count=5,
    )

    plugin.pytest_sessionstart(SimpleNamespace())
    plugin.pytest_deselected([object(), object()])
    plugin.pytest_collection_finish(SimpleNamespace(items=[object(), object(), object()]))
    plugin.pytest_runtest_logreport(
        SimpleNamespace(
            when="call",
            nodeid="tests/unit/test_example.py::test_ok",
            passed=True,
            failed=False,
            skipped=False,
        )
    )
    plugin.pytest_sessionfinish(SimpleNamespace(), 0)

    assert stream.getvalue().splitlines() == [
        "[ INSTALL ]",
        "selected 3 of 5 tests (2 deselected)",
        "INSTALL \x1b[32m✔\x1b[0m example.ok | Blender 4.2.1 [2/5] 1/3 33% ⣿⣿⣀⣀⣀⣀⣀⣀",
        "install complete | passed 1 | failed 0 | skipped 0",
    ]


def test_tui_plugin_prints_failure_details_only_for_failing_tests():
    stream = StringIO()
    plugin = runner_tui.build_pytest_tui(
        "test",
        stream=stream,
        current_version="Blender 4.2.1",
        current_run_index=1,
        run_count=1,
    )

    plugin.pytest_sessionstart(SimpleNamespace())
    plugin.pytest_collection_finish(SimpleNamespace(items=[object(), object()]))
    plugin.pytest_runtest_logreport(
        SimpleNamespace(
            when="call",
            nodeid="tests/unit/test_example.py::test_ok",
            passed=True,
            failed=False,
            skipped=False,
        )
    )
    plugin.pytest_runtest_logreport(
        SimpleNamespace(
            when="call",
            nodeid="tests/unit/test_example.py::test_bad",
            passed=False,
            failed=True,
            skipped=False,
            longreprtext="AssertionError: boom\nCaptured stdout call\nhelpful detail",
        )
    )
    plugin.pytest_sessionfinish(SimpleNamespace(), 1)

    assert stream.getvalue().splitlines() == [
        "[ TEST ]",
        "selected 2 of 2 tests (0 deselected)",
        "TEST    \x1b[32m✔\x1b[0m example.ok | Blender 4.2.1 [1/1] 1/2 50% ⣿⣿⣿⣿⣀⣀⣀⣀",
        "TEST    \x1b[31m✖\x1b[0m example.bad | Blender 4.2.1 [1/1] 2/2 100% ⣿⣿⣿⣿⣿⣿⣿⣿",
        "test complete | passed 1 | failed 1 | skipped 0",
        "",
        "FAILURES (1 failure)",
        "- example.bad",
        "AssertionError: boom",
        "Captured stdout call",
        "helpful detail",
        "",
    ]


def test_runner_uses_structured_tui_for_install_then_test_phases(monkeypatch, tmp_path):
    calls = []

    def fake_main(args, plugins=None):
        calls.append((args, plugins[0].stage))
        return 0

    monkeypatch.setattr(runner, "ensure_pytest_installed", lambda: None)
    monkeypatch.setattr(runner, "sanitize_target_directory", lambda target: None)
    monkeypatch.setattr(runner, "disable_addon", lambda name: None)
    monkeypatch.setattr(runner, "remove_existing_addons", lambda name: None)
    monkeypatch.setattr(runner, "addon_install_root", lambda: tmp_path / "addons")
    monkeypatch.setattr(runner.shutil, "copytree", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        runner.bpy.ops,
        "wm",
        SimpleNamespace(
            read_factory_settings=lambda *args, **kwargs: None,
            save_as_mainfile=lambda *args, **kwargs: None,
            open_mainfile=lambda *args, **kwargs: None,
        ),
        raising=False,
    )
    monkeypatch.setattr(runner, "pytest", SimpleNamespace(main=fake_main), raising=False)
    monkeypatch.setattr(
        runner,
        "parse_runner_args",
        lambda argv=None: SimpleNamespace(target_dir=tmp_path, blender_version=None),
    )

    exit_code = runner.main([])

    assert exit_code == 0
    assert [stage for _, stage in calls] == ["install", "test"]
    assert any("-p" in args and "no:terminal" in args for args, _ in calls)
    assert all("-s" not in args for args, _ in calls)


def test_runner_parser_accepts_log_file_path(tmp_path):
    parsed = runner.parse_runner_args([str(tmp_path), "--log-file", str(tmp_path / "run.log")])

    assert parsed.log_file == tmp_path / "run.log"


def test_run_pytest_phase_keeps_collecting_after_failure(monkeypatch, tmp_path):
    captured = {}

    def fake_main(args, plugins=None):
        captured["args"] = args
        captured["plugin"] = plugins[0]
        return 1

    monkeypatch.setattr(runner, "pytest", SimpleNamespace(main=fake_main), raising=False)

    result = runner.run_pytest_phase(tmp_path, "test", ["-m", "not install"])

    assert "--maxfail=1" not in captured["args"]
    assert result.exit_code == 1


def test_run_pytest_phase_mirrors_live_tui_output_to_stdout_and_log_file(monkeypatch, tmp_path, capsys):
    def fake_main(args, plugins=None):
        plugin = plugins[0]
        plugin.pytest_sessionstart(SimpleNamespace())
        plugin.pytest_collection_finish(SimpleNamespace(items=[object()]))
        plugin.pytest_runtest_logreport(
            SimpleNamespace(
                when="call",
                nodeid="tests/unit/test_example.py::test_ok",
                passed=True,
                failed=False,
                skipped=False,
            )
        )
        plugin.pytest_sessionfinish(SimpleNamespace(), 0)
        return 0

    monkeypatch.setattr(runner, "pytest", SimpleNamespace(main=fake_main), raising=False)

    log_file = tmp_path / "run.log"
    result = runner.run_pytest_phase(tmp_path, "test", ["-m", "not install"], log_file=log_file)

    output = capsys.readouterr().out
    assert "[ TEST ]" in output
    assert "TEST    \x1b[32m✔\x1b[0m example.ok" in output
    assert "[ TEST ]" in log_file.read_text(encoding="utf-8")
    assert result.exit_code == 0
