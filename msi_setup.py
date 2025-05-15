import sys
from importlib.metadata import metadata
from pathlib import Path

from cx_Freeze import Executable, setup

# Load package metadata
meta = metadata("auto-print")

# Define base for GUI apps
base = "Win32GUI" if sys.platform == "win32" else None

executables = [
    Executable(
        script="src\\auto_print\\auto_print_execute.py",
        base=base,
        target_name="auto-print.exe",
        icon="printer.ico",
    ),
    Executable(
        script="src\\auto_print\\auto_print_config_generator.py",
        base=base,
        target_name="auto-print-config.exe",
        icon="printer-gear.ico",
        shortcut_name="Auto Print Config",
        shortcut_dir="ProgramMenuFolder",
    ),
]

# Minimal MSI config
bdist_msi_options = {
    "upgrade_code": "{87CE1A83-346A-470C-9214-891B42186848}",
    "add_to_path": True,
    "initial_target_dir": r"[ProgramFilesFolder]\auto-print",
    "all_users": True,
    # "install_icon": "printer.ico",  # Optional
    "summary_data": {
        "author": meta["Author"],
        "comments": meta["Summary"],
    },
    # "data": {
    #     "Registry": [],
    #     "RemoveRegistry": [],
    #     "Component": [],
    #     "FeatureComponents": [],
    # },
}

# Setup
setup(
    name=meta["Name"],
    version=meta["Version"],
    description=meta["Summary"],
    long_description=Path("README.md").read_text(encoding="utf-8"),
    author=meta["Author"],
    author_email=meta["Author-email"],
    url=meta["Home-page"],
    license=meta["License"],
    options={
        "build_exe": {
            "packages": ["auto_print"],
            "include_files": ["config.json"],
        },
        "bdist_msi": bdist_msi_options,
    },
    executables=executables,
)
