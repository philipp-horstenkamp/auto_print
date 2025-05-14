import sys
from importlib.metadata import metadata
from pathlib import Path

from cx_Freeze import Executable, setup

# Load metadata from installed package (after `pip install -e .`)
meta = metadata("auto-print")

# Define the bdist_msi options with registry entries for PDF file association
bdist_msi_options = {
    "upgrade_code": "{87CE1A83-346A-470C-9214-891B42186848}",
    "add_to_path": True,
    "data": {
        "Registry": [
            # Register Auto Print in the Applications key
            # Register app in the Applications section (via HKLM)
            (
                "Registry",
                "HKLM",
                r"Software\Classes\Applications\auto-print.exe\shell\open\command",
                None,
                r'"[TARGETDIR]auto-print.exe" "%1"',
            ),
            (
                "Registry",
                "HKLM",
                r"Software\Classes\Applications\auto-print.exe",
                "FriendlyAppName",
                "Auto Print",
            ),
            # Add right-click context menu item for PDF files
            (
                "Registry",
                "HKCR",
                r".pdf\Shell\AutoPrintWithApp",
                None,
                "Auto Print with Auto Print",
            ),
            (
                "Registry",
                "HKCR",
                r".pdf\Shell\AutoPrintWithApp\command",
                None,
                r'"[TARGETDIR]auto-print.exe" "%1"',
            ),
        ]
    },
}

# Define the base executable
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Use this for a Windows GUI application

# Define the executables
executables = [
    Executable(
        script="src\\auto_print\\auto_print_execute.py",  # Main script to execute
        base=base,
        target_name="auto-print.exe",  # Name of the executable
        icon="printer.ico",  # Icon for the executable
        # shortcut_name="Auto Print",
        # shortcut_dir="ProgramMenuFolder",
    ),
    Executable(
        script="src\\auto_print\\auto_print_config_generator.py",  # Config generator script
        base=base,
        target_name="auto-print-config.exe",  # Name of the executable
        icon="printer-gear.ico",  # Icon for the executable
        shortcut_name="Auto Print Config",
        shortcut_dir="ProgramMenuFolder",
    ),
]

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
# To build the MSI installer, run:
# python msi_setup.py bdist_msi
