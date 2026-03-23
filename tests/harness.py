"""Package-safe wrapper around the root test harness."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


_HARNESS_PATH = Path(__file__).resolve().parent.parent / "test.py"
_SPEC = spec_from_file_location("gitblocks_root_test", _HARNESS_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load harness from {_HARNESS_PATH}")

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

BlenderRun = _MODULE.BlenderRun
build_parser = _MODULE.build_parser
plan_blender_runs = _MODULE.plan_blender_runs
build_blender_command = _MODULE.build_blender_command
load_env = _MODULE.load_env
read_env = _MODULE.read_env
main = _MODULE.main
