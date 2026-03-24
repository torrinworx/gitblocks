"""
Create a clean GitBlocks test environment and run pytest inside Blender.

Usage (from the GitBlocks add-on root):

  python test.py
"""

import sys
import shutil
import subprocess
import argparse
import json
import types
from contextlib import nullcontext
from dataclasses import dataclass, asdict
from pathlib import Path
import importlib.util

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tests import runner_tui


SUMMARY_FILENAME = "gitblocks-test-summary.json"

try:
    import bpy  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - Blender-only dependency
    bpy = types.ModuleType("bpy")
    bpy.types = types.SimpleNamespace(Operator=object, AddonPreferences=object)
    bpy.ops = types.SimpleNamespace(
        preferences=types.SimpleNamespace(
            addon_disable=lambda *args, **kwargs: {"CANCELLED"},
        ),
        wm=types.SimpleNamespace(
            read_factory_settings=lambda *args, **kwargs: None,
            save_as_mainfile=lambda *args, **kwargs: None,
            open_mainfile=lambda *args, **kwargs: None,
        ),
        gitblocks=types.SimpleNamespace(),
    )
    bpy.utils = types.SimpleNamespace(user_resource=lambda *args, **kwargs: "/tmp")
    bpy.app = types.SimpleNamespace(background=True, timers=types.SimpleNamespace(is_registered=lambda *args, **kwargs: False))
    bpy.context = types.SimpleNamespace(preferences=types.SimpleNamespace(addons={}), window=None, window_manager=types.SimpleNamespace(event_timer_add=lambda *args, **kwargs: None, modal_handler_add=lambda *args, **kwargs: None, event_timer_remove=lambda *args, **kwargs: None), scene=None, view_layer=None)
    bpy.data = types.SimpleNamespace(filepath="")
    sys.modules["bpy"] = bpy


# Helpers
@dataclass(frozen=True)
class PhaseResult:
    stage: str
    selected: int
    deselected: int
    passed: int
    failed: int
    skipped: int
    exit_code: int
    failures: tuple["FailureDetail", ...] = ()


@dataclass(frozen=True)
class FailureDetail:
    nodeid: str
    message: str
    longreprtext: str


class TeeStream:
    def __init__(self, *streams):
        self._streams = streams

    def write(self, text):
        for stream in self._streams:
            stream.write(text)

    def flush(self):
        for stream in self._streams:
            stream.flush()

    def isatty(self):
        for stream in self._streams:
            isatty = getattr(stream, "isatty", None)
            if callable(isatty) and isatty():
                return True
        return False


def build_parser():
    parser = argparse.ArgumentParser(description="Run GitBlocks tests inside Blender")
    parser.add_argument("target_dir", type=Path, help="Directory where test data should be prepared")
    parser.add_argument(
        "--blender-version",
        help="Blender version selected by the outer harness for this run",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Write detailed pytest output to this log file",
    )
    return parser


def select_target_directory(target: Path, version: str | None):
    if version and target.name != version:
        return target / version
    return target


def parse_runner_args(argv: list[str] | None = None):
    return build_parser().parse_args(argv)


def ensure_pytest_installed():
    if (
        importlib.util.find_spec("pytest") is not None
        and importlib.util.find_spec("pytest_order") is not None
    ):
        return

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "pytest",
            "pytest-order",
        ]
    )


def parse_requirements(path: Path):
    if not path.exists():
        return []
    pkgs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            pkgs.append(line.split("==")[0].strip())
    return pkgs


def addon_install_root():
    try:
        return Path(bpy.utils.user_resource("EXTENSIONS"))
    except Exception:
        return Path(bpy.utils.user_resource("SCRIPTS")) / "addons"


def disable_addon(name: str):
    if name in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_disable(module=name)


def remove_existing_addons(name: str):
    install_root = addon_install_root()
    if install_root.name == "addons":
        addon_dir = install_root / name
        if addon_dir.exists():
            if addon_dir.is_symlink() or addon_dir.is_file():
                addon_dir.unlink(missing_ok=True)
            else:
                shutil.rmtree(addon_dir, ignore_errors=True)
        return

    for repo in install_root.parent.iterdir():
        addon_dir = repo / name
        if addon_dir.exists():
            if addon_dir.is_symlink() or addon_dir.is_file():
                addon_dir.unlink(missing_ok=True)
            else:
                shutil.rmtree(addon_dir, ignore_errors=True)


def sanitize_target_directory(target: Path):
    """Delete contents of target folder but keep the folder itself."""
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)
        return
    for item in target.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink(missing_ok=True)
        else:
            shutil.rmtree(item, ignore_errors=True)


def run_pytest_phase(
    tests_dir: Path,
    stage: str,
    extra_args: list[str] | None = None,
    current_version: str | None = None,
    current_run_index: int = 1,
    run_count: int = 1,
    log_file: Path | None = None,
):
    pytest_module = globals().get("pytest")
    if pytest_module is None:
        import pytest as pytest_module  # type: ignore

    args = [str(tests_dir), "-p", "no:terminal"]
    if extra_args:
        args.extend(extra_args)
    if log_file is not None:
        args.extend(["--log-file", str(log_file)])
        log_file.parent.mkdir(parents=True, exist_ok=True)
    log_context = open(log_file, "a", encoding="utf-8", buffering=1) if log_file else nullcontext()
    stream = TeeStream(sys.stdout, log_context) if log_file else sys.stdout
    with log_context:
        tui = runner_tui.build_pytest_tui(
            stage,
            stream=stream,
            current_version=current_version,
            current_run_index=current_run_index,
            run_count=run_count,
        )
        exit_code = pytest_module.main(args, plugins=[tui])
    return PhaseResult(
        stage=stage,
        selected=tui.selected,
        deselected=tui.deselected,
        passed=tui.passed,
        failed=tui.failed,
        skipped=tui.skipped,
        exit_code=exit_code,
        failures=tuple(
            FailureDetail(
                nodeid=failure.nodeid,
                message=(failure.longreprtext.splitlines()[0] if failure.longreprtext else ""),
                longreprtext=failure.longreprtext,
            )
            for failure in tui.failures
        ),
    )


def write_run_summary(
    target_path: Path,
    blender_version: str | None,
    phases: list[PhaseResult],
    log_file: Path | None = None,
) -> None:
    target_path.mkdir(parents=True, exist_ok=True)
    summary_path = target_path / SUMMARY_FILENAME
    payload = {
        "blender_version": blender_version,
        "log_file": str(log_file) if log_file else None,
        "phases": [asdict(phase) for phase in phases],
    }
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None):
    raw_argv = sys.argv[1:] if argv is None else argv
    raw_argv = raw_argv[raw_argv.index("--") + 1 :] if "--" in raw_argv else raw_argv
    parsed = parse_runner_args(raw_argv) if raw_argv else None
    target_path = parsed.target_dir.absolute() if parsed else Path.cwd()
    target_path = select_target_directory(target_path, getattr(parsed, "blender_version", None))
    log_file = getattr(parsed, "log_file", None)

    ensure_pytest_installed()

    sanitize_target_directory(target_path)

    blend_path = target_path / "test.blend"
    bpy.ops.wm.read_factory_settings(use_empty=False)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    addon_name = "gitblocks_addon"  # GitBlocks addon package name
    addon_src = Path(__file__).parent.parent.resolve()

    # reset environment for the addon
    try:
        reqs = parse_requirements(addon_src / "requirements.txt")
        if reqs:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "uninstall", "--yes", *reqs],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception:
        pass
    disable_addon(addon_name)
    remove_existing_addons(addon_name)

    user_repo = addon_install_root() / "user_default"
    user_repo.mkdir(parents=True, exist_ok=True)

    addon_dest = user_repo / addon_src.name
    if addon_dest.exists():
        shutil.rmtree(addon_dest, ignore_errors=True)
    shutil.copytree(addon_src, addon_dest)

    tests_dir = Path(__file__).parent
    phase_results = []

    install_result = run_pytest_phase(
        tests_dir,
        "install",
        ["-m", "install", "--ignore=tests/unit"],
        current_version=getattr(parsed, "blender_version", None),
        log_file=log_file,
    )
    phase_results.append(install_result)
    if install_result.exit_code != 0:
        write_run_summary(target_path, getattr(parsed, "blender_version", None), phase_results, log_file=log_file)
        return install_result.exit_code

    test_result = run_pytest_phase(
        tests_dir,
        "test",
        ["-m", "not install"],
        current_version=getattr(parsed, "blender_version", None),
        log_file=log_file,
    )
    phase_results.append(test_result)
    write_run_summary(target_path, getattr(parsed, "blender_version", None), phase_results, log_file=log_file)
    return test_result.exit_code


if __name__ == "__main__":
    sys.exit(main())
