"""
Create a clean GitBlocks test environment and run pytest inside Blender.

Usage (from the GitBlocks add-on root):

  python test.py
"""

import sys
import shutil
import subprocess
import argparse
import types
from pathlib import Path
import importlib.util

from tests import runner_tui


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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
def build_parser():
    parser = argparse.ArgumentParser(description="Run GitBlocks tests inside Blender")
    parser.add_argument("target_dir", type=Path, help="Directory where test data should be prepared")
    parser.add_argument(
        "--blender-version",
        help="Blender version selected by the outer harness for this run",
    )
    return parser


def select_target_directory(target: Path, version: str | None):
    return target / version if version else target


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


def run_pytest_phase(tests_dir: Path, stage: str, extra_args: list[str] | None = None):
    pytest_module = globals().get("pytest")
    if pytest_module is None:
        import pytest as pytest_module  # type: ignore

    args = [
        str(tests_dir),
        "-q",
        "-s",
        "--disable-warnings",
        "--maxfail=1",
        "-p",
        "no:terminal",
    ]
    if extra_args:
        args.extend(extra_args)
    return pytest_module.main(args, plugins=[runner_tui.build_pytest_tui(stage)])


def main(argv: list[str] | None = None):
    raw_argv = sys.argv[1:] if argv is None else argv
    raw_argv = raw_argv[raw_argv.index("--") + 1 :] if "--" in raw_argv else raw_argv
    parsed = parse_runner_args(raw_argv) if raw_argv else None
    target_path = parsed.target_dir.absolute() if parsed else Path.cwd()
    target_path = select_target_directory(target_path, getattr(parsed, "blender_version", None))

    ensure_pytest_installed()

    # Silence Blender's banner in pytest output
    print("\n\033[36m[ runner ] Preparing clean GitBlocks test environment\033[0m")

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
    print(f"\033[36m[ runner ] Launching GitBlocks pytest in {tests_dir}\033[0m\n")

    install_code = run_pytest_phase(
        tests_dir,
        "install",
        ["-m", "install", "--ignore=tests/unit"],
    )
    if install_code != 0:
        return install_code

    return run_pytest_phase(tests_dir, "test", ["-m", "not install"])


if __name__ == "__main__":
    sys.exit(main())
