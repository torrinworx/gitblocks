bl_info = {
    "name": "GitBlocks",
    "author": "Torrin Leonard",
    "description": "Git-backed datablock version control for GitBlocks",
    "blender": (4, 5, 3),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}

import os
import sys
import importlib
import subprocess
import threading
import types

try:
    import bpy  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - allows unit-test imports outside Blender
    bpy = types.ModuleType("bpy")
    bpy.types = types.SimpleNamespace(Operator=object, AddonPreferences=object)
    bpy.ops = types.SimpleNamespace(
        preferences=types.SimpleNamespace(
            addon_enable=lambda *args, **kwargs: {"CANCELLED"},
            addon_disable=lambda *args, **kwargs: {"CANCELLED"},
        ),
        wm=types.SimpleNamespace(),
        gitblocks=types.SimpleNamespace(),
    )
    bpy.utils = types.SimpleNamespace(
        register_class=lambda *args, **kwargs: None,
        unregister_class=lambda *args, **kwargs: None,
        user_resource=lambda *args, **kwargs: "/tmp",
    )
    bpy.app = types.SimpleNamespace(
        background=True,
        timers=types.SimpleNamespace(
            register=lambda *args, **kwargs: None,
            unregister=lambda *args, **kwargs: None,
            is_registered=lambda *args, **kwargs: False,
        ),
    )
    bpy.context = types.SimpleNamespace(
        window=None,
        window_manager=types.SimpleNamespace(
            modal_handler_add=lambda *args, **kwargs: None,
            event_timer_add=lambda *args, **kwargs: None,
            event_timer_remove=lambda *args, **kwargs: None,
        ),
        preferences=types.SimpleNamespace(addons={}),
        scene=types.SimpleNamespace(collection=types.SimpleNamespace(objects=types.SimpleNamespace(link=lambda *args, **kwargs: None))),
        view_layer=None,
    )
    bpy.data = types.SimpleNamespace(filepath="", meshes=types.SimpleNamespace(new=lambda *args, **kwargs: None), objects=types.SimpleNamespace(new=lambda *args, **kwargs: None))
    sys.modules["bpy"] = bpy

from .utils.timers import timers
from .branding import ADDON_DESCRIPTION, ADDON_NAME, UI_LOG_PREFIX

bl_info["name"] = ADDON_NAME
bl_info["description"] = ADDON_DESCRIPTION

IMPORT_NAME_MAP = {"GitPython": "git"}

REQUIREMENTS_PATH = os.path.join(os.path.dirname(__file__), "requirements.txt")

DEPENDENCIES_INSTALLED = False
MISSING_DEPENDENCIES = []
INSTALL_IN_PROGRESS = False
auto_load_was_registered = False
_core_classes_registered = False

_install_thread = None
_install_thread_error = None


def parse_requirements(filepath):
    if not os.path.exists(filepath):
        return []
    lines = []
    with open(filepath, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                lines.append(ln)
    return [entry.split("==")[0].strip() for entry in lines]


def check_dependencies():
    missing = []
    for pkg in parse_requirements(REQUIREMENTS_PATH):
        # If the PyPI name differs from the import name, swap here
        import_name = IMPORT_NAME_MAP.get(pkg, pkg)
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append(pkg)
    return missing


def install_packages():
    """Install packages with pip (in a worker thread)."""
    global DEPENDENCIES_INSTALLED, MISSING_DEPENDENCIES, _install_thread_error
    pkgs = parse_requirements(REQUIREMENTS_PATH)
    if not pkgs:
        _install_thread_error = "No requirements.txt or no packages."
        return

    try:
        pybin = sys.executable
        subprocess.check_call([pybin, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([pybin, "-m", "pip", "install", "-r", REQUIREMENTS_PATH])
        MISSING_DEPENDENCIES[:] = check_dependencies()
        DEPENDENCIES_INSTALLED = len(MISSING_DEPENDENCIES) == 0
    except Exception as e:
        _install_thread_error = f"Failed to install dependencies: {e}"


class GITBLOCKS_OT_install_deps(bpy.types.Operator):
    """Install missing requirements asynchronously."""

    bl_idname = "gitblocks.install_deps"
    bl_label = "Install Dependencies"
    bl_options = {"REGISTER", "INTERNAL"}

    _timer = None

    def _run_install_sync(self, context):
        global _install_thread_error, INSTALL_IN_PROGRESS, auto_load_was_registered

        _install_thread_error = None
        INSTALL_IN_PROGRESS = True
        install_packages()
        INSTALL_IN_PROGRESS = False

        if _install_thread_error:
            self.report({"ERROR"}, _install_thread_error)
            return {"CANCELLED"}
        if MISSING_DEPENDENCIES:
            self.report({"WARNING"}, "Still missing: " + ", ".join(MISSING_DEPENDENCIES))
            return {"CANCELLED"}

        try:
            from . import auto_load

            auto_load.init()
            auto_load.register()
            auto_load_was_registered = True
        except ImportError:
            pass
        except Exception as e:
            self.report({"ERROR"}, f"Auto-load failed: {e}")
            return {"CANCELLED"}

        return {"FINISHED"}

    def execute(self, context):
        return self._run_install_sync(context)

    def invoke(self, context, event):
        global _install_thread, INSTALL_IN_PROGRESS, _install_thread_error

        if bpy.app.background or context.window is None:
            return self._run_install_sync(context)

        if _install_thread and _install_thread.is_alive():
            self.report({"INFO"}, "Already installing.")
            return {"CANCELLED"}

        _install_thread_error = None
        INSTALL_IN_PROGRESS = True

        _install_thread = threading.Thread(target=install_packages)
        _install_thread.start()

        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        global _install_thread, _install_thread_error, INSTALL_IN_PROGRESS

        if event.type == "TIMER":
            if _install_thread and not _install_thread.is_alive():
                # Stop the timer
                context.window_manager.event_timer_remove(self._timer)
                self._timer = None
                INSTALL_IN_PROGRESS = False

                if _install_thread_error:
                    self.report({"ERROR"}, _install_thread_error)
                elif MISSING_DEPENDENCIES:
                    self.report(
                        {"WARNING"}, "Still missing: " + ", ".join(MISSING_DEPENDENCIES)
                    )
                else:
                    self.report({"INFO"}, "Dependencies installed successfully.")
                    try:
                        from . import auto_load

                        auto_load.init()
                        auto_load.register()
                        global auto_load_was_registered
                        auto_load_was_registered = True
                    except ImportError:
                        pass  # auto_load not found

                _install_thread = None
                return {"FINISHED"}

        return {"PASS_THROUGH"}


class GitBlocksPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout

        if INSTALL_IN_PROGRESS:
            layout.label(text=f"Installing {ADDON_NAME} dependencies...", icon="FILE_REFRESH")
        elif DEPENDENCIES_INSTALLED:
            layout.label(text="All dependencies are installed.", icon="CHECKMARK")
        else:
            layout.label(
                text="Missing: " + ", ".join(MISSING_DEPENDENCIES), icon="ERROR"
            )
            layout.operator(GITBLOCKS_OT_install_deps.bl_idname, icon="CONSOLE")


def register():
    global DEPENDENCIES_INSTALLED, MISSING_DEPENDENCIES, auto_load_was_registered
    global _core_classes_registered

    MISSING_DEPENDENCIES[:] = check_dependencies()
    DEPENDENCIES_INSTALLED = len(MISSING_DEPENDENCIES) == 0
    auto_load_was_registered = False
    _core_classes_registered = False

    try:
        existing_install = getattr(bpy.types, GITBLOCKS_OT_install_deps.__name__, None)
        if existing_install is not None and existing_install is not GITBLOCKS_OT_install_deps:
            if getattr(existing_install, "bl_rna", None) is not None:
                try:
                    bpy.utils.unregister_class(existing_install)
                except Exception:
                    pass
        if getattr(bpy.types, GITBLOCKS_OT_install_deps.__name__, None) is not GITBLOCKS_OT_install_deps:
            bpy.utils.register_class(GITBLOCKS_OT_install_deps)

        existing_prefs = getattr(bpy.types, GitBlocksPreferences.__name__, None)
        if existing_prefs is not None and existing_prefs is not GitBlocksPreferences:
            if getattr(existing_prefs, "bl_rna", None) is not None:
                try:
                    bpy.utils.unregister_class(existing_prefs)
                except Exception:
                    pass
        if getattr(bpy.types, GitBlocksPreferences.__name__, None) is not GitBlocksPreferences:
            bpy.utils.register_class(GitBlocksPreferences)
        _core_classes_registered = True
    except Exception as e:
        print(f"[{UI_LOG_PREFIX}] Error registering core classes:", e)

    if DEPENDENCIES_INSTALLED:
        try:
            from . import auto_load

            auto_load.init()
            auto_load.register()
            auto_load_was_registered = True
        except ImportError:
            pass  # auto_load not found, skipping registration.
        except Exception as e:
            print(f"[{UI_LOG_PREFIX}] Error in auto_load.register:", e)


def unregister():
    # Only call auto_load.unregister() if we actually registered it
    if auto_load_was_registered:
        try:
            from . import auto_load

            auto_load.unregister()
            timers.unregister_all()
        except Exception as e:
            print(f"[{UI_LOG_PREFIX}] Error in auto_load.unregister:", e)

    global _core_classes_registered
    if _core_classes_registered:
        try:
            existing_prefs = getattr(bpy.types, GitBlocksPreferences.__name__, None)
            if existing_prefs is not None and getattr(existing_prefs, "bl_rna", None) is not None:
                bpy.utils.unregister_class(existing_prefs)
        except Exception as e:
            print(f"[{UI_LOG_PREFIX}] Error unregistering preferences:", e)
        try:
            existing_install = getattr(bpy.types, GITBLOCKS_OT_install_deps.__name__, None)
            if existing_install is not None and getattr(existing_install, "bl_rna", None) is not None:
                bpy.utils.unregister_class(existing_install)
        except Exception as e:
            print(f"[{UI_LOG_PREFIX}] Error unregistering install operator:", e)
    _core_classes_registered = False
