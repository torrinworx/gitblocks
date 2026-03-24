from pathlib import Path

from tests import runner


def test_runner_uses_version_specific_target_directory(tmp_path):
    target = runner.select_target_directory(tmp_path, "5.1.0")

    assert target == tmp_path / "5.1.0"


def test_runner_keeps_existing_version_specific_directory(tmp_path):
    versioned = tmp_path / "5.1.0"

    target = runner.select_target_directory(versioned, "5.1.0")

    assert target == versioned


def test_runner_keeps_base_target_directory_without_version(tmp_path):
    target = runner.select_target_directory(tmp_path, None)

    assert target == tmp_path


def test_runner_parses_version_argument():
    args = runner.build_parser().parse_args(["/tmp/tests", "--blender-version", "5.1.0"])

    assert args.target_dir == Path("/tmp/tests")
    assert args.blender_version == "5.1.0"
