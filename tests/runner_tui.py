"""Structured terminal output for the Blender test runner."""

from __future__ import annotations

from dataclasses import dataclass, field
import sys
from typing import TextIO


def format_stage_banner(stage: str) -> str:
    return f"== {stage.strip().upper()} PHASE =="


def format_test_result(nodeid: str, outcome: str) -> str:
    status = {
        "passed": "PASS",
        "failed": "FAIL",
        "skipped": "SKIP",
    }.get(outcome, outcome.upper())
    return f"{status} {nodeid}"


def format_summary(collected: int, deselected: int, selected: int) -> str:
    return f"collected {collected} | selected {selected} | deselected {deselected}"


@dataclass
class PytestTUI:
    stage: str
    stream: TextIO = sys.stdout
    collected: int = 0
    deselected: int = 0
    selected: int = 0
    _banner_written: bool = field(default=False, init=False)

    def _write(self, line: str) -> None:
        print(line, file=self.stream)

    def pytest_sessionstart(self, session) -> None:
        if not self._banner_written:
            self._write(format_stage_banner(self.stage))
            self._banner_written = True

    def pytest_deselected(self, items) -> None:
        self.deselected += len(items)

    def pytest_collection_finish(self, session) -> None:
        self.selected = len(session.items)
        self.collected = self.selected + self.deselected
        self._write(format_summary(self.collected, self.deselected, self.selected))

    def pytest_runtest_logreport(self, report) -> None:
        if getattr(report, "when", None) == "call":
            self._write(format_test_result(report.nodeid, report.outcome))

    def pytest_sessionfinish(self, session, exitstatus) -> None:
        self._write(
            f"{self.stage} phase finished: {self.selected} selected, {self.deselected} deselected"
        )


def build_pytest_tui(stage: str, stream: TextIO | None = None) -> PytestTUI:
    return PytestTUI(stage=stage, stream=stream or sys.stdout)
