"""Structured terminal output for the Blender test runner."""

from __future__ import annotations

from dataclasses import dataclass, field
import sys
from typing import TextIO


def format_stage_banner(stage: str) -> str:
    return f"[ {stage.strip().upper()} ]"


def compact_nodeid(nodeid: str) -> str:
    base, bracket, param = nodeid.partition("[")
    path_part, separator, test_name = base.rpartition("::")
    module = path_part.rsplit("/", 1)[-1].removesuffix(".py")
    if module.startswith("test_"):
        module = module[5:]
    if separator and test_name.startswith("test_"):
        test_name = test_name[5:]
    label = f"{module}.{test_name}" if separator else module
    if bracket:
        return f"{label} [{param.rstrip(']')}]"
    return label


def truncate_label(label: str, width: int = 48) -> str:
    if len(label) <= width:
        return label
    if width <= 3:
        return label[:width]
    return f"{label[: width - 3]}..."


def format_collection_summary(collected: int, deselected: int, selected: int) -> str:
    return f"selected {selected} of {collected} tests ({deselected} deselected)"


def colorize(text: str, color: str) -> str:
    palette = {
        "green": "\x1b[32m",
        "red": "\x1b[31m",
        "yellow": "\x1b[33m",
        "cyan": "\x1b[36m",
        "dim": "\x1b[2m",
    }
    return f"{palette.get(color, '')}{text}\x1b[0m" if color in palette else text


def format_status_mark(kind: str) -> str:
    marks = {
        "pass": ("✔", "green"),
        "fail": ("✖", "red"),
        "skip": ("↷", "yellow"),
    }
    mark, color = marks.get(kind, ("•", "cyan"))
    return colorize(mark, color)


def format_progress_grid(completed: int, total: int, width: int = 8) -> str:
    if width <= 0:
        return ""
    if total <= 0:
        return "⣀" * width
    filled = min(width, max(0, int((completed / total) * width)))
    return f"{'⣿' * filled}{'⣀' * (width - filled)}"


def format_progress_bar(completed: int, total: int, width: int = 24) -> str:
    return format_progress_grid(completed, total, width)


def format_matrix_progress_line(
    completed_tests: int,
    total_tests: int,
    current_version: str,
    current_run_index: int,
    run_count: int,
) -> str:
    percent = int((completed_tests / total_tests) * 100) if total_tests else 100
    grid = format_progress_grid(completed_tests, total_tests)
    return (
        f"{current_version} [{current_run_index}/{run_count}] "
        f"{completed_tests}/{total_tests} {percent}% {grid}"
    )


def format_test_footer(
    stage: str,
    nodeid: str,
    completed: int,
    total: int,
    passed: int,
    failed: int,
    skipped: int,
    current_version: str | None = None,
    current_run_index: int = 1,
    run_count: int = 1,
    status_kind: str | None = None,
) -> str:
    percent = int((completed / total) * 100) if total else 100
    label = truncate_label(compact_nodeid(nodeid))
    status = status_kind or ("fail" if failed > 0 and completed >= total else "skip" if skipped > 0 and passed == 0 and failed == 0 else "pass")
    matrix = format_matrix_progress_line(
        completed,
        total,
        current_version or "Blender",
        current_run_index,
        run_count,
    )
    return (
        f"{stage.upper():7} {format_status_mark(status)} {label} | {matrix}"
    )


def format_stage_finish(stage: str, passed: int, failed: int, skipped: int) -> str:
    return f"{stage} complete | passed {passed} | failed {failed} | skipped {skipped}"


def format_failure_heading(count: int) -> str:
    noun = "failure" if count == 1 else "failures"
    return f"FAILURES ({count} {noun})"


def format_failure_detail(nodeid: str, longreprtext: str) -> list[str]:
    lines = [f"- {compact_nodeid(nodeid)}"]
    details = [line.rstrip() for line in longreprtext.splitlines() if line.strip()]
    lines.extend(details)
    return lines


@dataclass
class FailureDetail:
    nodeid: str
    longreprtext: str


@dataclass(eq=False)
class PytestTUI:
    stage: str
    stream: TextIO = sys.stdout
    current_version: str | None = None
    current_run_index: int = 1
    run_count: int = 1
    collected: int = 0
    deselected: int = 0
    selected: int = 0
    completed: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    failures: list[FailureDetail] = field(default_factory=list)
    _banner_written: bool = field(default=False, init=False)
    _finished_nodeids: set[str] = field(default_factory=set, init=False)
    _footer_active: bool = field(default=False, init=False)
    _last_footer: str = field(default="", init=False)

    def _supports_live_footer(self) -> bool:
        isatty = getattr(self.stream, "isatty", None)
        return bool(callable(isatty) and isatty())

    def _write(self, line: str = "") -> None:
        print(line, file=self.stream)

    def _update_footer(self, line: str) -> None:
        self._last_footer = line
        if self._supports_live_footer():
            self.stream.write(f"\r\033[2K{line}")
            self.stream.flush()
            self._footer_active = True
            return
        self._write(line)

    def _flush_footer(self) -> None:
        if not self._footer_active:
            return
        self.stream.write(f"\r\033[2K{self._last_footer}\n")
        self.stream.flush()
        self._footer_active = False

    def _is_final_report(self, report) -> bool:
        when = getattr(report, "when", None)
        if when == "call":
            return True
        if when == "setup" and (getattr(report, "failed", False) or getattr(report, "skipped", False)):
            return True
        if when == "teardown" and getattr(report, "failed", False):
            return True
        return False

    def _record_outcome(self, report) -> None:
        nodeid = report.nodeid
        if nodeid in self._finished_nodeids:
            return
        self._finished_nodeids.add(nodeid)
        self.completed += 1

        if getattr(report, "passed", False):
            self.passed += 1
        elif getattr(report, "skipped", False):
            self.skipped += 1
        else:
            self.failed += 1
            self.failures.append(
                FailureDetail(
                    nodeid=nodeid,
                    longreprtext=getattr(report, "longreprtext", "") or repr(getattr(report, "longrepr", "")),
                )
            )

        self._update_footer(
            format_test_footer(
                self.stage,
                nodeid,
                self.completed,
                self.selected,
                self.passed,
                self.failed,
                self.skipped,
                current_version=self.current_version,
                current_run_index=self.current_run_index,
                run_count=self.run_count,
                status_kind="fail" if getattr(report, "failed", False) else "skip" if getattr(report, "skipped", False) else "pass",
            )
        )

    def pytest_sessionstart(self, session) -> None:
        if not self._banner_written:
            self._write(format_stage_banner(self.stage))
            self._banner_written = True

    def pytest_deselected(self, items) -> None:
        self.deselected += len(items)

    def pytest_collection_finish(self, session) -> None:
        self.selected = len(session.items)
        self.collected = self.selected + self.deselected
        self._write(format_collection_summary(self.collected, self.deselected, self.selected))

    def pytest_runtest_logreport(self, report) -> None:
        if self._is_final_report(report):
            self._record_outcome(report)

    def pytest_sessionfinish(self, session, exitstatus) -> None:
        self._flush_footer()
        self._write(format_stage_finish(self.stage, self.passed, self.failed, self.skipped))
        if self.failures:
            self._write("")
            self._write(format_failure_heading(len(self.failures)))
            for failure in self.failures:
                for line in format_failure_detail(failure.nodeid, failure.longreprtext):
                    self._write(line)
                self._write("")


def build_pytest_tui(
    stage: str,
    stream: TextIO | None = None,
    current_version: str | None = None,
    current_run_index: int = 1,
    run_count: int = 1,
) -> PytestTUI:
    return PytestTUI(
        stage=stage,
        stream=stream or sys.stdout,
        current_version=current_version,
        current_run_index=current_run_index,
        run_count=run_count,
    )
