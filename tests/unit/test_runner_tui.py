from types import SimpleNamespace
from io import StringIO

from tests import runner_tui
from tests import runner


def test_stage_banner_is_stable_for_install_and_test_phases():
    assert runner_tui.format_stage_banner("install") == "== INSTALL PHASE =="
    assert runner_tui.format_stage_banner("test") == "== TEST PHASE =="


def test_format_test_result_is_one_line_and_compact():
    assert (
        runner_tui.format_test_result("tests/unit/test_example.py::test_ok", "passed")
        == "PASS tests/unit/test_example.py::test_ok"
    )


def test_format_summary_includes_collection_counts():
    assert runner_tui.format_summary(12, 3, 9) == "collected 12 | selected 9 | deselected 3"


def test_tui_plugin_emits_stage_header_collection_and_result_lines():
    stream = StringIO()
    plugin = runner_tui.build_pytest_tui("install", stream=stream)

    plugin.pytest_sessionstart(SimpleNamespace())
    plugin.pytest_deselected([object(), object()])
    plugin.pytest_collection_finish(SimpleNamespace(items=[object(), object(), object()]))
    plugin.pytest_runtest_logreport(
        SimpleNamespace(when="call", nodeid="tests/unit/test_example.py::test_ok", outcome="passed")
    )
    plugin.pytest_sessionfinish(SimpleNamespace(), 0)

    assert stream.getvalue().splitlines() == [
        "== INSTALL PHASE ==",
        "collected 5 | selected 3 | deselected 2",
        "PASS tests/unit/test_example.py::test_ok",
        "install phase finished: 3 selected, 2 deselected",
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
    assert all("-s" in args for args, _ in calls)
