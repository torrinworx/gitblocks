from types import SimpleNamespace
from io import StringIO

from tests import runner_tui
from tests import runner


def test_stage_banner_is_stable_for_install_and_test_phases():
    assert runner_tui.format_stage_banner("install") == "== INSTALL PHASE =="
    assert runner_tui.format_stage_banner("test") == "== TEST PHASE =="


def test_compact_nodeid_keeps_file_test_and_param_case_readable():
    assert (
        runner_tui.compact_nodeid(
            "tests/unit/test_example.py::test_ok[latest]"
        )
        == "test_example.py::test_ok [latest]"
    )


def test_format_progress_shows_checkbox_and_percentage():
    assert (
        runner_tui.format_test_progress(
            "tests/unit/test_example.py::test_ok", "passed", 3, 10
        )
        == "[x] test_example.py::test_ok (3/10, 30%)"
    )


def test_format_collection_summary_includes_selected_counts():
    assert (
        runner_tui.format_collection_summary(12, 3, 9)
        == "selected 9 of 12 tests (3 deselected)"
    )


def test_tui_plugin_emits_stage_header_collection_progress_and_summary():
    stream = StringIO()
    plugin = runner_tui.build_pytest_tui("install", stream=stream)

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
        "== INSTALL PHASE ==",
        "selected 3 of 5 tests (2 deselected)",
        "[x] test_example.py::test_ok (1/3, 33%)",
        "install phase complete: 1 passed, 0 failed, 0 skipped",
    ]


def test_tui_plugin_prints_failure_details_only_for_failing_tests():
    stream = StringIO()
    plugin = runner_tui.build_pytest_tui("test", stream=stream)

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
        "== TEST PHASE ==",
        "selected 2 of 2 tests (0 deselected)",
        "[x] test_example.py::test_ok (1/2, 50%)",
        "[ ] test_example.py::test_bad (2/2, 100%)",
        "test phase complete: 1 passed, 1 failed, 0 skipped",
        "",
        "FAILURES (1 failure)",
        "[ ] test_example.py::test_bad",
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
