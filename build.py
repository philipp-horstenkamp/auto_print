import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import tomllib

# 🔧 Define your entrypoints here
ENTRYPOINTS: dict[str, str] = {
    "auto_print_config_generator.exe": "src/auto_print/auto_print_config_generator.py",
    "auto_print_execute.exe": "src/auto_print/auto_print_execute.py",
}

OUTPUT_DIR = "build"

# 🔍 Resolve the actual output .exe path based on the first script
first_main = next(iter(ENTRYPOINTS.values()))
exe_base_name = os.path.splitext(os.path.basename(first_main))[0]
DIST_DIR = os.path.join(OUTPUT_DIR, exe_base_name + ".dist")
SOURCE_EXE = os.path.join(DIST_DIR, exe_base_name + ".exe")


@contextlib.contextmanager
def temporary_generated_init(pyproject_path: str, init_path: str):
    """
    Temporarily replaces the given __init__.py with static metadata
    extracted from pyproject.toml and restores it on exit.
    """

    init_file = Path(init_path)
    pyproject_file = Path(pyproject_path)

    if not pyproject_file.exists():
        raise FileNotFoundError(f"{pyproject_path} not found")
    if not init_file.exists():
        raise FileNotFoundError(f"{init_path} not found")

    # Backup original __init__.py to a tempfile
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".py") as temp_backup:
        shutil.copyfile(init_file, temp_backup.name)
        temp_backup_path = Path(temp_backup.name)

        try:
            # Parse pyproject.toml
            with pyproject_file.open("rb") as f:
                pyproject = tomllib.load(f)

            project = (
                pyproject.get("tool", {}).get("poetry")
                or pyproject.get("project")
                or {}
            )

            author, email = "unknown", "unknown@example.com"
            if authors := project.get("authors"):
                parts = authors[0].split("<")
                author = parts[0].strip()
                if len(parts) > 1:
                    email = parts[1].rstrip(">")

            metadata_lines = [
                f'__version__ = "{project.get("version", "0.0.0")}"',
                f'__author__ = "{author}"',
                f'__email__ = "{email}"',
                f'__description__ = "{project.get("description", "")}"',
                f'__license__ = "{project.get("license", "MIT")}"',
            ]

            init_file.write_text("\n".join(metadata_lines) + "\n", encoding="utf-8")
            print(f"🧩 Overwrote {init_path} with generated metadata.")
            yield

        finally:
            shutil.copyfile(temp_backup_path, init_file)
            print(f"↩️  Restored original {init_path} from temp backup.")


def run_nuitka_multidist():
    print("🔨 Building with Nuitka (Multidist)...")

    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--lto=yes",
        "--enable-console",
        "--remove-output",
        "--assume-yes-for-downloads",
        "--show-progress",
        "--show-scons",
        "--noinclude-unittest-mode=nofollow",
        "--noinclude-setuptools-mode=nofollow",
        f"--output-dir={OUTPUT_DIR}",
        "--include-package=auto_print",
        "--include-module=win32api",
        "--include-module=win32con",
        "--include-package=win32api",
        "--include-package=win32com",
        "--enable-plugin=anti-bloat",
    ]

    for script in ENTRYPOINTS.values():
        cmd.append(f"--main={script}")

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

    for line in process.stdout:
        print(line, end="")

    process.wait()
    if process.returncode != 0:
        print(f"❌ Build failed with code {process.returncode}")
        sys.exit(process.returncode)

    print("✅ Nuitka build complete.")


def create_entrypoint_binaries():
    print("📦 Creating entry point executables...")

    if not os.path.exists(SOURCE_EXE):
        print(f"❌ Could not find expected build output: {SOURCE_EXE}")
        sys.exit(1)

    for exe_name, filenames in ENTRYPOINTS.items():
        target_path = os.path.join(OUTPUT_DIR, exe_name)
        shutil.copyfile(SOURCE_EXE, target_path)
        print(f"  ↪ {exe_name} → {filenames}")

    print("✅ Entrypoint copies created.")


def main() -> None:
    with temporary_generated_init("pyproject.toml", "src/auto_print/__init__.py"):
        run_nuitka_multidist()
        create_entrypoint_binaries()


if __name__ == "__main__":
    main()
