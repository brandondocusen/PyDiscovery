#!/usr/bin/env python3
"""
pdtrace.py – one‑shot runtime tracer
====================================

• Trace every Python call made by a script or package.
• Writes **runtime_calls.json** to the directory pdtrace.py is launched from.
• Zero external dependencies – works on stock CPython 3.8 +.

Usage
-----
python pdtrace.py <target> [--chdir] [--] [args for target …]

  <target>   .py file, a folder, or an importable package
  --chdir    run from the target folder so its relative paths keep working
"""
from __future__ import annotations

import importlib.util
import json
import os
import runpy
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import List, Tuple, Dict, Any

# ------------------------------------------------------------------#
#  Make absolute imports (pydiscovery.*) work even when cwd == pydiscovery
_PKG_ROOT = Path(__file__).resolve().parent.parent
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

# Assuming RuntimeMonitor is correctly located relative to _PKG_ROOT
# If pydiscovery package structure is different, adjust this import
try:
    from pydiscovery.analyzer.runtime_monitor import RuntimeMonitor # std-lib only
except ImportError:
    print("[Error] Could not import RuntimeMonitor.", file=sys.stderr)
    print(f"        Attempted import relative to: {_PKG_ROOT}", file=sys.stderr)
    print(f"        Current sys.path: {sys.path}", file=sys.stderr)
    sys.exit(1)


_USAGE = "pdtrace.py <target> [--chdir] [--] [args …]"


@contextmanager
def _maybe_chdir(folder: Path, enabled: bool):
    prev = Path.cwd()
    if enabled:
        # Ensure the target directory exists before changing to it
        if folder.is_dir():
            try:
                os.chdir(folder)
            except OSError as e:
                print(f"[Warning] Could not chdir to {folder}: {e}", file=sys.stderr)
                enabled = False # Prevent changing back if chdir failed
        else:
             print(f"[Warning] --chdir target folder does not exist: {folder}", file=sys.stderr)
             enabled = False # Prevent changing back if target doesn't exist

    try:
        yield
    finally:
        if enabled:
            try:
                os.chdir(prev)
            except OSError as e:
                 print(f"[Warning] Could not chdir back to {prev}: {e}", file=sys.stderr)


# ------------------------------------------------------------------#
# Helpers for resolving the target
def _single_py(folder: Path) -> Path | None:
    py = [p for p in folder.glob("*.py") if p.is_file()]
    return py[0] if len(py) == 1 else None


def _ask_choice(options: List[Path]) -> Path:
    print("[?] Pick the file you want to run:")
    for i, f in enumerate(options, 1):
        print(f"  {i}. {f.name}")
    while True:
        raw = input(f"Number 1‑{len(options)} (default 1): ").strip()
        if not raw:
            return options[0]
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print("Please enter a valid number.")


def _resolve(arg: str) -> Tuple[Path, List[str]]:
    """
    Return (resolved_target_path, launch_prefix).
    launch_prefix == []            → run_path(resolved_target_path)
    launch_prefix == ['-m', name]  → run_module(name)
    resolved_target_path is used for chdir context if needed.
    """
    p = Path(arg).expanduser()
    resolved_p = p.resolve() # Resolve early for consistent path handling

    # explicit .py file ----------------------------------------------
    if resolved_p.suffix == ".py" and resolved_p.is_file():
        return resolved_p, []

    # folder ----------------------------------------------------------
    if resolved_p.is_dir():
        main_py = resolved_p / "__main__.py"
        if main_py.is_file():
            # Target is the folder containing __main__.py for chdir
            return resolved_p, ['-m', resolved_p.name] # Run as module relative to parent
        if solo := _single_py(resolved_p):
             # Target is the specific .py file
            return solo, []
        py_files = sorted(f for f in resolved_p.glob("*.py") if f.is_file())
        if py_files:
             # Target is the chosen .py file
            chosen_py = _ask_choice(py_files)
            return chosen_py, []
        sys.exit(f"No *.py files or __main__.py found in {resolved_p}")

    # importable package ---------------------------------------------
    # Try resolving as an importable module name *first* before failing
    try:
        spec = importlib.util.find_spec(arg)
        # Ensure it's not a namespace package and has a file location
        if spec and spec.origin and spec.origin != 'namespace':
            origin_path = Path(spec.origin)
            # Heuristic: If origin is __init__.py, target path for chdir is its parent
            target_path_for_chdir = origin_path.parent if origin_path.name == "__init__.py" else origin_path
            return target_path_for_chdir.resolve(), ["-m", arg]
    except ModuleNotFoundError:
         pass # Fall through to exit
    except ValueError: # Handles cases like empty string args
         pass

    # If we get here, resolution failed
    # Check if the original path exists at all to give a better error
    if not p.exists():
         sys.exit(f"Target does not exist: {arg}")
    elif p.is_dir(): # e.g., directory exists but no runnable Python files
         sys.exit(f"Cannot find runnable Python file or __main__.py in directory: {p}")
    else: # e.g., exists but is not .py, dir, or importable module
         sys.exit(f"Cannot resolve target (not a .py file, directory, or importable module): {arg}")


# ------------------------------------------------------------------#
# Modified _dump function
def _dump(edges: Dict[Tuple[str, str], Any], launch_dir: Path, elapsed: float) -> Path:
    """
    Dumps the collected edges to runtime_calls.json in the launch directory.
    """
    # Construct the output path using the launch directory
    out = launch_dir / "runtime_calls.json"
    payload = [
        {
            "caller": c,
            "callee": d,
            # Handle potential variations in stats format (dict or simple count)
            **(stats if isinstance(stats, dict) else {"calls": int(stats)}),
        }
        for (c, d), stats in sorted(edges.items())
    ]
    try:
        out.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        print(
            f"\n[pdtrace] saved {len(payload)} calls to {out} "
            f"in {elapsed:.1f}s"
        )
    except OSError as e:
        print(f"\n[Error] Failed to write trace file to {out}: {e}", file=sys.stderr)
        # Fallback: Try writing to CWD as a last resort if different from launch_dir
        fallback_path = Path.cwd() / "runtime_calls.json"
        if fallback_path != out:
            try:
                fallback_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
                print(f"[pdtrace] Fallback: Saved trace to {fallback_path}", file=sys.stderr)
                out = fallback_path # Update return value if fallback succeeded
            except OSError as e_fallback:
                print(f"[Error] Fallback write to {fallback_path} also failed: {e_fallback}", file=sys.stderr)
        # Even if write fails, return the intended path for logging purposes
    return out


# ------------------------------------------------------------------#
def main() -> None:
    # Capture the launch directory *before* any potential chdir
    launch_dir = Path.cwd()

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(_USAGE, file=sys.stderr) # Print usage to stderr
        sys.exit(1) # Exit with error code

    # handle --chdir flag
    args = sys.argv[1:]
    chdir_flag = "--chdir" in args
    if chdir_flag:
        args.remove("--chdir")

    if not args: # Check if only '--chdir' was passed
         print(_USAGE, file=sys.stderr)
         sys.exit(1)

    # split target from its arguments at "--" if present
    target_arg = args[0]
    tgt_args: List[str] = []
    if "--" in args:
        try:
            sep_index = args.index("--")
            target_arg = args[0] # Assume target is always first before separator
            if sep_index == 0: # Handle case like '-- --chdir my_script.py' - unlikely but possible
                 print(f"[Error] Invalid argument order: '--' cannot be the first argument.", file=sys.stderr)
                 sys.exit(1)
            if sep_index > 1: # More than just the target before '--'
                 print(f"[Warning] Multiple arguments before '--', only using '{target_arg}' as target.", file=sys.stderr)
            tgt_args = args[sep_index + 1 :]
        except ValueError: # Should not happen if '--' is in args, but good practice
            pass # Keep default tgt_args = []
    else:
        # No '--', target is first arg, rest are its args
        target_arg = args[0]
        tgt_args = args[1:]


    # Resolve the target script/module and the path for chdir context
    resolved_path, prefix = _resolve(target_arg)

    # Determine the path for the _maybe_chdir context manager
    # If running a module (-m), chdir to the directory *containing* the package/module file
    # If running a script (.py), chdir to the directory containing the script
    chdir_target_path = resolved_path.parent if resolved_path.is_file() else resolved_path


    # Set sys.argv for the target script/module
    # For run_module: needs the module name (original target_arg if prefix is set)
    # For run_path: needs the resolved script path
    if prefix: # Running as module
        sys.argv = [resolved_path.as_posix()] + tgt_args # runpy needs a filename even for modules sometimes? Use resolved path.
        module_name_to_run = target_arg # The original name used for -m
    else: # Running as path
        sys.argv = [str(resolved_path)] + tgt_args
        module_name_to_run = None # Not used for run_path

    start = time.perf_counter()
    ended_early = False
    monitor_exception = None

    print(f"[pdtrace] Launch directory: {launch_dir}")
    print(f"[pdtrace] Target argument: {target_arg}")
    print(f"[pdtrace] Resolved path for context: {resolved_path}")
    print(f"[pdtrace] Chdir target path: {chdir_target_path}")
    print(f"[pdtrace] Prefix (run mode): {prefix if prefix else 'run_path'}")
    print(f"[pdtrace] Arguments for target: {tgt_args}")
    print(f"[pdtrace] sys.argv for target: {sys.argv}")
    print(f"[pdtrace] Running with chdir: {chdir_flag}")


    try:
        # Use chdir_target_path for the context manager
        with _maybe_chdir(chdir_target_path, chdir_flag), RuntimeMonitor() as mon:
            try:
                if prefix and module_name_to_run:
                    print(f"[pdtrace] Executing: runpy.run_module('{module_name_to_run}', run_name='__main__')")
                    runpy.run_module(module_name_to_run, run_name="__main__")
                elif not prefix:
                    print(f"[pdtrace] Executing: runpy.run_path('{str(resolved_path)}', run_name='__main__')")
                    runpy.run_path(str(resolved_path), run_name="__main__")
                else:
                     # This case should ideally not be reached if _resolve is correct
                     print("[Error] Inconsistent state: prefix set but no module name.", file=sys.stderr)
                     ended_early = True
            except BaseException as e: # Catch broader exceptions, incl. SystemExit
                print(f"\n[pdtrace] Target execution interrupted: {type(e).__name__}: {e}", file=sys.stderr)
                ended_early = True
                # Optionally re-raise if you want pdtrace to exit with target's error code
                # raise

    except Exception as e:
        # Catch exceptions occurring in context manager or RuntimeMonitor setup/teardown
        print(f"\n[pdtrace] Error during monitoring setup/teardown: {type(e).__name__}: {e}", file=sys.stderr)
        monitor_exception = e
        # Ensure monitor exists even if context failed, might have partial data
        if 'mon' not in locals():
             mon = None # type: ignore

    # Ensure mon exists and has edges before dumping
    if 'mon' in locals() and mon is not None and hasattr(mon, 'edges'):
         # Pass the captured launch_dir to _dump
         out_file = _dump(mon.edges, launch_dir, time.perf_counter() - start)
         # summary -------------------------------------------------
         print("[pdtrace] ✅ Trace capture finished.") # Changed from success as it might have ended early
         print(f"[pdtrace] 📄 Trace file attempted save at: {out_file}")
    else:
         print("[pdtrace] ❌ No trace data captured, likely due to an early error.", file=sys.stderr)
         if monitor_exception:
              print(f"[pdtrace] Monitor error details: {monitor_exception}", file=sys.stderr)
         sys.exit(1) # Exit with error if no trace data


    if ended_early:
        print(
            "[pdtrace] ℹ️  Your program stopped after completing some work.\n"
            "          The calls executed so far were saved and are usable.\n"
            "          For an even more complete view, run pdtrace again once\n"
            "          your program has everything it needs (often different file types)."
        )
    elif monitor_exception:
         print(
              "\n[pdtrace] ⚠️ An error occurred within the monitoring process itself.\n"
              "          The trace might be incomplete or inaccurate."
         )


if __name__ == "__main__":
    # It's good practice to wrap main() call in a try/except
    # to catch unexpected top-level errors if needed, but
    # the internal error handling might be sufficient.
    main()