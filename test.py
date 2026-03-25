import os
import sys
import subprocess
import argparse
import inspect
from datetime import UTC, datetime
from dataclasses import dataclass
from pathlib import Path

from tests.blender_versions import ensure_installed
from tests.blender_versions import check_blender_compatibility
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
    test_filter: str | None = None


@dataclass(frozen=True)
class BlenderRunResult:
    run: BlenderRun
    exit_code: int


def build_parser():
    parser = argparse.ArgumentParser(description="Run GitBlocks Blender tests")
    parser.add_argument("--blender-version", help="Run tests against a single Blender version")
    parser.add_argument(
        "--blender-versions",
        help="Run tests against a comma-separated matrix of Blender versions",
    )
    parser.add_argument(
        "--test",
        help="Run a single test expression inside Blender using pytest -k",
    )
    return parser


def _parse_version_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [entry.strip() for entry in value.split(",") if entry.strip()]


def _read_test_filter(args, env: dict[str, str]) -> str | None:
    cli_value = (getattr(args, "test", None) or "").strip() or None
    env_value = (env.get("GITBLOCKS_TEST_FILTER") or "").strip() or None
    return cli_value or env_value


def _resolver_supports_progress(resolver) -> bool:
    try:
        signature = inspect.signature(resolver)
    except (TypeError, ValueError):
        return False
    for parameter in signature.parameters.values():
        if parameter.kind == inspect.Parameter.VAR_KEYWORD or parameter.name == "progress":
            return True
    return False


def _resolve_blender_binary(resolver, version: str, *, progress=None):
    if progress is not None and _resolver_supports_progress(resolver):
        return resolver(version, progress=progress)
    return resolver(version)


def plan_blender_runs(
    argv: list[str],
    *,
    addon_root: Path,
    env: dict[str, str] | None = None,
    resolver=ensure_installed,
    progress=None,
) -> list[BlenderRun]:
    env = dict(env or {})
    args = build_parser().parse_args(argv)

    test_dir = Path(env.get("GITBLOCKS_TEST_DIR", "/tmp/gitblocks_addon_tests"))
    blender_bin_override = env.get("GITBLOCKS_BLENDER_BIN")

    cli_versions = _parse_version_list(args.blender_versions)
    env_versions = _parse_version_list(env.get("GITBLOCKS_BLENDER_VERSIONS"))
    cli_version = (args.blender_version or "").strip() or None
    env_version = (env.get("GITBLOCKS_BLENDER_VERSION") or "").strip() or None
    test_filter = _read_test_filter(args, env)

    if blender_bin_override:
        return [
            BlenderRun(
                blender_bin=Path(blender_bin_override).expanduser(),
                test_dir=test_dir,
                test_filter=test_filter,
            )
        ]

    selected_versions = cli_versions or env_versions or ([] if cli_version is None and env_version is None else [cli_version or env_version])

    compatibility = check_blender_compatibility(selected_versions)
    if selected_versions and not compatibility.ok:
        print("GitBlocks compatibility preflight failed:")
        print(compatibility.message)
        sys.exit(1)

    if selected_versions:
        return [
            BlenderRun(
                blender_bin=Path(_resolve_blender_binary(resolver, version, progress=progress)),
                test_dir=test_dir / version,
                version=version,
                test_filter=test_filter,
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
            test_filter=test_filter,
        )
    ]


def render_blender_install_event(event) -> str | None:
    if event.kind == "start":
        return f"◆ Preparing Blender {event.version}"
    if event.kind == "cache-hit":
        return f"✓ Blender {event.version} ready (cached)"
    if event.kind == "progress":
        if event.detail == "checksum":
            return f"… Checking Blender {event.version} download"
        if event.bytes_downloaded is not None and event.total_bytes:
            percent = int((event.bytes_downloaded / event.total_bytes) * 100)
            return f"… Downloading Blender {event.version}: {percent}%"
        return f"… Downloading Blender {event.version}"
    if event.kind == "complete":
        return f"✓ Blender {event.version} ready"
    return None


def print_blender_install_event(event) -> None:
    line = render_blender_install_event(event)
    if line:
        print(line)


def log_path_for_run(addon_root: Path, run: BlenderRun, started_at: datetime | None = None) -> Path:
    started_at = started_at or datetime.utcnow()
    stamp = started_at.strftime("%Y-%m-%d_%H-%M-%S")
    version = (run.version or "blender").replace("/", "-")
    logs_dir = addon_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / f"gitblocks-test-{stamp}-{version}.log"


def render_run_result(result: BlenderRunResult) -> str:
    version = result.run.version or result.run.blender_bin.name
    status = "PASS" if result.exit_code == 0 else "FAIL"
    return f"{version:<12} {status:<4} exit {result.exit_code}"


def render_matrix_summary(results: list[BlenderRunResult]) -> str:
    border = "=" * 60
    lines = [border, "GitBlocks | Matrix Summary", border]
    total_passed = 0
    total_failed = 0
    for result in results:
        lines.append(render_run_result(result))
        if result.exit_code == 0:
            total_passed += 1
        else:
            total_failed += 1
    lines.append(border)
    lines.append(f"overall PASS:{total_passed} FAIL:{total_failed} across {len(results)} Blender run(s)")
    return "\n".join(lines)


def render_run_header(run: BlenderRun) -> str:
    if run.version:
        label = f"Blender {run.version}"
    else:
        label = "Blender"
    border = "=" * 60
    return f"{border}\nGitBlocks | {label}\n{border}"


def build_blender_command(addon_root: Path, run: BlenderRun, log_file: Path | None = None) -> list[str]:
    runner = addon_root / "tests" / "runner.py"
    cmd = [
        str(run.blender_bin),
        "--factory-startup",
        "--background",
        "--log-level",
        "0",
        "--python",
        str(runner),
        "--",
        str(run.test_dir),
    ]
    if run.version:
        cmd.extend(["--blender-version", run.version])
    if run.test_filter:
        cmd.extend(["--test", run.test_filter])
    if log_file is not None:
        cmd.extend(["--log-file", str(log_file)])
    return cmd


def main():
    addon_root = Path(__file__).parent.resolve()
    load_env(addon_root / ".env")

    runs = plan_blender_runs(
        sys.argv[1:],
        addon_root=addon_root,
        env=os.environ,
        progress=print_blender_install_event,
    )

    runner = addon_root / "tests" / "runner.py"
    if not runner.exists():
        print(f"Test runner not found at {runner}")
        sys.exit(1)

    exit_code = 0
    overall_exit_code = 0
    results = []
    for run in runs:
        blender_path = run.blender_bin
        if not blender_path.exists():
            print(f"GitBlocks Blender binary not found at {blender_path}")
            print("Set GITBLOCKS_BLENDER_BIN in .env")
            sys.exit(1)

        log_file = log_path_for_run(addon_root, run, datetime.now(UTC))
        cmd = build_blender_command(addon_root, run, log_file=log_file)
        print(render_run_header(run))
        exit_code = subprocess.call(cmd, cwd=str(addon_root))
        results.append(
            BlenderRunResult(
                run=run,
                exit_code=exit_code,
            )
        )
        if exit_code != 0 and overall_exit_code == 0:
            overall_exit_code = exit_code

    if results:
        print(render_matrix_summary(results))

    sys.exit(overall_exit_code)


if __name__ == "__main__":
    main()
