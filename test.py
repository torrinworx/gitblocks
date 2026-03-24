import os
import sys
import subprocess
import argparse
import inspect
import json
from datetime import UTC, datetime
from dataclasses import dataclass
from pathlib import Path

from tests.blender_versions import ensure_installed
from tests.runner_tui import compact_nodeid


SUMMARY_FILENAME = "gitblocks-test-summary.json"


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


@dataclass(frozen=True)
class PhaseSummary:
    stage: str
    passed: int
    failed: int
    skipped: int
    selected: int
    deselected: int
    exit_code: int
    failures: tuple["FailureSummary", ...] = ()


@dataclass(frozen=True)
class FailureSummary:
    nodeid: str
    message: str
    longreprtext: str


@dataclass(frozen=True)
class BlenderRunResult:
    run: BlenderRun
    exit_code: int
    phases: tuple[PhaseSummary, ...] = ()


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
                blender_bin=Path(_resolve_blender_binary(resolver, version, progress=progress)),
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


def summary_path_for_run(run: BlenderRun) -> Path:
    return run.test_dir / SUMMARY_FILENAME


def log_path_for_run(addon_root: Path, run: BlenderRun, started_at: datetime | None = None) -> Path:
    started_at = started_at or datetime.utcnow()
    stamp = started_at.strftime("%Y-%m-%d_%H-%M-%S")
    version = (run.version or "blender").replace("/", "-")
    logs_dir = addon_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / f"gitblocks-test-{stamp}-{version}.log"


def load_run_summary(summary_path: Path) -> tuple[PhaseSummary, ...]:
    if not summary_path.exists():
        return ()
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    return tuple(
        PhaseSummary(
            stage=phase["stage"],
            passed=phase["passed"],
            failed=phase["failed"],
            skipped=phase["skipped"],
            selected=phase["selected"],
            deselected=phase["deselected"],
            exit_code=phase["exit_code"],
            failures=tuple(
                FailureSummary(
                    nodeid=failure["nodeid"],
                    message=failure.get("message", ""),
                    longreprtext=failure.get("longreprtext", ""),
                )
                for failure in phase.get("failures", [])
            ),
        )
        for phase in data.get("phases", [])
    )


def format_phase_totals(phase: PhaseSummary) -> str:
    return f"{phase.stage} P:{phase.passed} F:{phase.failed} S:{phase.skipped}"


def render_run_result(result: BlenderRunResult) -> str:
    version = result.run.version or result.run.blender_bin.name
    status = "PASS" if result.exit_code == 0 else "FAIL"
    details = " | ".join(format_phase_totals(phase) for phase in result.phases)
    if details:
        return f"{version:<12} {status:<4} {details}"
    return f"{version:<12} {status:<4} no summary captured"


def render_failure_digest(results: list[BlenderRunResult]) -> list[str]:
    grouped: list[tuple[str, list[FailureSummary]]] = []
    for result in results:
        failures: list[FailureSummary] = []
        for phase in result.phases:
            failures.extend(list(phase.failures))
        if failures:
            grouped.append((result.run.version or result.run.blender_bin.name, failures))

    if not grouped:
        return []

    lines = ["FAILURE DIGEST"]
    for version, failures in grouped:
        lines.append(f"{version}")
        for failure in failures:
            lines.append(f"- {compact_nodeid(failure.nodeid)} :: {failure.message}")
    return lines


def render_matrix_summary(results: list[BlenderRunResult]) -> str:
    border = "=" * 60
    lines = [border, "GitBlocks | Matrix Summary", border]
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    for result in results:
        lines.append(render_run_result(result))
        for phase in result.phases:
            total_passed += phase.passed
            total_failed += phase.failed
            total_skipped += phase.skipped
    lines.append(border)
    lines.append(
        f"overall P:{total_passed} F:{total_failed} S:{total_skipped} across {len(results)} Blender run(s)"
    )
    digest = render_failure_digest(results)
    if digest:
        lines.append("")
        lines.extend(digest)
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
        summary_path = summary_path_for_run(run)
        summary_path.unlink(missing_ok=True)
        print(render_run_header(run))
        exit_code = subprocess.call(cmd, cwd=str(addon_root))
        results.append(
            BlenderRunResult(
                run=run,
                exit_code=exit_code,
                phases=load_run_summary(summary_path),
            )
        )
        if exit_code != 0 and overall_exit_code == 0:
            overall_exit_code = exit_code

    if results:
        print(render_matrix_summary(results))

    sys.exit(overall_exit_code)


if __name__ == "__main__":
    main()
