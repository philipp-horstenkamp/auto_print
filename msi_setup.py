"""
MSI Installer Setup Script for Auto Print Application

This script configures and builds a Windows MSI installer for the Auto Print application
using cx_Freeze. It defines the executables to be included, MSI package options,
and setup parameters required for installation.

The installer includes:
- The main Auto Print executable for printing documents
- A configuration tool executable for setting up the application
- Appropriate icons and shortcuts
- Environment variable settings
- Component and directory configurations

Usage:
    python msi_setup.py bdist_msi
"""

import sys
from importlib.metadata import metadata
from pathlib import Path

from cx_Freeze import Executable, setup

"""
Load package metadata from the installed auto-print package.

This retrieves metadata such as version, author, and description from the package
that has been installed in development mode (pip install -e .).
The metadata is used later in the setup configuration.
"""
meta = metadata("auto-print")

"""
Define the base executable type for the application.

For Windows platforms, this sets the base to "Win32GUI" which creates a Windows GUI
application that doesn't open a console window when executed. For non-Windows platforms,
it defaults to None which creates a console application.
"""
base = "Win32GUI" if sys.platform == "win32" else None

"""
Define the executables to be included in the installer package.

This list contains two executables:
1. auto-print.exe - The main application executable for printing documents
   - Uses auto_print_execute.py as the source script
   - Uses printer.ico as its icon
   - There is no shortcut to the application create

2. auto-print-config.exe - The configuration tool executable
   - Uses auto_print_config_generator.py as the source script
   - Uses printer-gear.ico as its icon
   - Creates a shortcut in the Start Menu (ProgramMenuFolder)
   - Shortcut is named "Auto Print Config"

Both executables use the previously defined base to determine their application type.
"""
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

"""
Configure MSI installer options for the Windows Installer package.

This dictionary defines all the MSI-specific options for the installer:
- upgrade_code: A unique GUID that identifies this application for upgrades
- add_to_path: Adds the installation directory to the system PATH
- initial_target_dir: Default installation directory (Program Files\auto-print)
- install_icon: Icon displayed during installation
- environment_variables: Environment variables to set during installation
- summary_data: Metadata for the installer (author, comments)
- data: Component definitions for the Windows Installer

The Component section defines:
- AutoPrintComponent: The main component containing the application
- A fixed GUID for the component based on the upgrade_code
- TARGETDIR as the installation location
- auto-print.exe as the key path (must match an executable target_name)

These options control how the MSI installer behaves during installation and uninstallation.
"""
bdist_msi_options = {
    "upgrade_code": "{87CE1A83-346A-470C-9214-891B42186848}",
    "add_to_path": True,
    "initial_target_dir": r"[ProgramFilesFolder]\auto-print",
    # "all_users": True,
    "install_icon": "printer.ico",
    "environment_variables": {
        "PATH": "$INSTDIR;.",
    },
    "summary_data": {
        "author": meta["Author"],
        "comments": meta["Summary"],
    },
    "data": {
        "Component": [
            (
                "AutoPrintComponent",
                "{87CE1A83-346A-470C-9214-891B42186849}",  # Using a fixed GUID based on the upgrade_code
                "TARGETDIR",  # Install location
                0,  # Attributes
                None,  # Condition
                "auto-print.exe",  # KeyPath (must match target_name of Executable)
            )
        ],
    },
}

"""
Execute the cx_Freeze setup function to build the application installer.

This is the main entry point for the cx_Freeze build process. It configures:
- Basic package metadata (name, version, description, etc.) from the package metadata
- Long description from the README.md file
- Author information and licensing
- Build options:
  - build_exe: Configures the executable build process
    - packages: Python packages to include in the build
    - include_files: Additional files to include in the build (config.json)
  - bdist_msi: Uses the previously defined MSI options
- Executables: Uses the previously defined executables list

When this script is run with 'python msi_setup.py bdist_msi', cx_Freeze will:
1. Build the executables specified in the executables list
2. Package them into an MSI installer with the options specified in bdist_msi_options
3. Place the resulting MSI file in the 'dist' directory
"""
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
