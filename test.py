import os
import sys
import subprocess
import argparse
from dataclasses import dataclass
from pathlib import Path

from tests.blender_versions import ensure_installed


def load_env(env_path: Path):
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"").strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def read_env(primary: str, default: str) -> str:
    return os.environ.get(primary) or default


@dataclass(frozen=True)
class BlenderRun:
    blender_bin: Path
    test_dir: Path
    version: str | None = None


def build_parser():
    parser = argparse.ArgumentParser(description="Run GitBlocks Blender tests")
    parser.add_argument("--blender-version", help="Run tests against a single Blender version")
    parser.add_argument(
        "--blender-versions",
        help="Run tests against a comma-separated matrix of Blender versions",
    )
    return parser


def _parse_version_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [entry.strip() for entry in value.split(",") if entry.strip()]


def plan_blender_runs(
    argv: list[str],
    *,
    addon_root: Path,
    env: dict[str, str] | None = None,
    resolver=ensure_installed,
) -> list[BlenderRun]:
    env = dict(env or {})
    args = build_parser().parse_args(argv)

    test_dir = Path(env.get("GITBLOCKS_TEST_DIR", "/tmp/gitblocks_addon_tests"))
    blender_bin_override = env.get("GITBLOCKS_BLENDER_BIN")

    cli_versions = _parse_version_list(args.blender_versions)
    env_versions = _parse_version_list(env.get("GITBLOCKS_BLENDER_VERSIONS"))
    cli_version = (args.blender_version or "").strip() or None
    env_version = (env.get("GITBLOCKS_BLENDER_VERSION") or "").strip() or None

    if blender_bin_override:
        return [
            BlenderRun(
                blender_bin=Path(blender_bin_override).expanduser(),
                test_dir=test_dir,
            )
        ]

    selected_versions = cli_versions or env_versions or ([] if cli_version is None and env_version is None else [cli_version or env_version])

    if selected_versions:
        return [
            BlenderRun(
                blender_bin=Path(resolver(version)),
                test_dir=test_dir / version,
                version=version,
            )
            for version in selected_versions
        ]

    fallback_bin = read_env(
        "GITBLOCKS_BLENDER_BIN",
        "/home/torrin/blender-4.5.3-linux-x64/blender",
    )
    return [
        BlenderRun(
            blender_bin=Path(fallback_bin).expanduser(),
            test_dir=test_dir,
        )
    ]


def build_blender_command(addon_root: Path, run: BlenderRun) -> list[str]:
    runner = addon_root / "tests" / "runner.py"
    cmd = [
        str(run.blender_bin),
        "--factory-startup",
        "--background",
        "--python",
        str(runner),
        "--",
        str(run.test_dir),
    ]
    if run.version:
        cmd.extend(["--blender-version", run.version])
    return cmd


def main():
    addon_root = Path(__file__).parent.resolve()
    load_env(addon_root / ".env")

    runs = plan_blender_runs(sys.argv[1:], addon_root=addon_root, env=os.environ)

    runner = addon_root / "tests" / "runner.py"
    if not runner.exists():
        print(f"Test runner not found at {runner}")
        sys.exit(1)

    exit_code = 0
    for run in runs:
        blender_path = run.blender_bin
        if not blender_path.exists():
            print(f"GitBlocks Blender binary not found at {blender_path}")
            print("Set GITBLOCKS_BLENDER_BIN in .env")
            sys.exit(1)

        cmd = build_blender_command(addon_root, run)
        print("Running GitBlocks Blender tests:")
        print(" ".join(cmd))
        exit_code = subprocess.call(cmd, cwd=str(addon_root))
        if exit_code != 0:
            break

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
