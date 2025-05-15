"""
MSI Installer Setup Script for Auto Print Application with Context Menu Integration

This script configures and builds a Windows MSI installer for the Auto Print application
using cx_Freeze. It includes:
- Executables for the main auto-print tool and config utility
- Context menu entry for PDF files (without taking over default association)
- MSI registry integration for all users
- Install-time assertions to ensure correctness of the installer configuration

Usage:
    python msi_setup.py bdist_msi

The installer includes:
- The main Auto Print executable for printing documents
- A configuration tool executable for setting up the application
- Appropriate icons and shortcuts
- Environment variable settings
- Component and directory configurations

This script also defines:
- File associations for PDF files using context menu only
- Avoids setting the application as the default handler for PDF files
- All settings applied for all users (system-wide installation)

Implementation details:
- Uses HKEY_CLASSES_ROOT via Root=0 in registry entries, which maps to HKLM\Software\Classes
  when `all_users=True`, ensuring all-user installation
- Context menu added under SystemFileAssociations to not interfere with default PDF application
- Assertions added to validate assumptions and configuration correctness

Known Windows behavior:
- On Windows 11, context menu items added via registry under `SystemFileAssociations` appear
  under "Show more options"
- This is a Microsoft UX design and not an installer limitation

"""

import sys
from importlib.metadata import metadata
from pathlib import Path

from cx_Freeze import Executable, setup

# Application constants
component_name = "AutoPrintComponent"
app_exe_name = "auto-print.exe"
context_menu_verb = "AutoPrint"
context_menu_text = "Auto Print with Auto Print"

# Load package metadata from installed package
meta = metadata("auto-print")

# Determine base executable type
base = "Win32GUI" if sys.platform == "win32" else None

"""
Define the executables to be included in the installer package.

This list contains two executables:
1. auto-print.exe - The main application executable for printing documents
   - Uses auto_print_execute.py as the source script
   - Uses printer.ico as its icon
   - There is no shortcut to the application created

2. auto-print-config.exe - The configuration tool executable
   - Uses auto_print_config_generator.py as the source script
   - Uses printer-gear.ico as its icon
   - Creates a shortcut in the Start Menu (ProgramMenuFolder)
   - Shortcut is named "Auto Print Config"

Both executables use the previously defined base to determine their application type.
"""
executables = [
    Executable(
        script="src/auto_print/auto_print_execute.py",
        base=base,
        target_name=app_exe_name,
        icon="printer.ico",
    ),
    Executable(
        script="src/auto_print/auto_print_config_generator.py",
        base=None,  # Use console mode for config generator to run in cmd
        target_name="auto-print-config.exe",
        icon="printer-gear.ico",
        shortcut_name="Auto Print Config",
        shortcut_dir="ProgramMenuFolder",
    ),
]

"""
Registry keys for context menu integration.

Context menu added under:
HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\AutoPrint
This avoids taking over the default .pdf handler while adding a right-click option.
"""
install_dir = "[TARGETDIR]"
pdf_shell_key = rf"SystemFileAssociations\.pdf\shell\{context_menu_verb}"
pdf_cmd_key = rf"{pdf_shell_key}\command"

registry_entries = [
    ("PDFContextMenuVerb", 0, pdf_shell_key, None, context_menu_text, component_name),
    (
        "PDFContextMenuCommand",
        0,
        pdf_cmd_key,
        None,
        f'"{install_dir}{app_exe_name}" "%1"',
        component_name,
    ),
]

"""
RemoveRegistry entries ensure that all registry modifications are reverted during uninstall.
Each key matches the entries added above.
"""
remove_registry_entries = [
    ("Remove_PDFContextMenuVerb", 0, pdf_shell_key, None, component_name),
    ("Remove_PDFContextMenuCommand", 0, pdf_cmd_key, None, component_name),
]

"""
Assertions to validate critical installation configuration.
These prevent incorrect registry or MSI assumptions.
"""
assert context_menu_verb != "open", (
    "Using 'open' as verb would override the default PDF handler. Use a custom verb instead."
)
assert registry_entries[0][1] == 0, (
    "Root=0 (HKCR) ensures registry entries are written under HKEY_LOCAL_MACHINE\\Software\\Classes for all users."
)
assert "SystemFileAssociations" in registry_entries[0][2], (
    "Using SystemFileAssociations avoids conflicting with existing default PDF associations."
)

"""
Configure MSI installer options for the Windows Installer package.

This dictionary defines all the MSI-specific options for the installer:
- upgrade_code: A unique GUID that identifies this application for upgrades
- add_to_path: Adds the installation directory to the system PATH
- initial_target_dir: Default installation directory (Program Files\auto-print)
- install_icon: Icon displayed during installation
- environment_variables: Environment variables to set during installation
- summary_data: Metadata for the installer (author, comments)
- data: Component definitions for the Windows Installer, including:
  - Component: The main component containing the application
  - Registry: Registry entries for context menu integration
  - RemoveRegistry: Entries to clean up registry during uninstallation

The Component section defines:
- AutoPrintComponent: The main component containing the application
- A fixed GUID for the component based on the upgrade_code
- TARGETDIR as the installation location
- auto-print.exe as the key path (must match an executable target_name)
"""
bdist_msi_options = {
    "upgrade_code": "{87CE1A83-346A-470C-9214-891B42186848}",
    "add_to_path": True,
    "initial_target_dir": r"[ProgramFilesFolder]\auto-print",
    "all_users": True,
    "install_icon": "printer.ico",
    "license_file": "LICENSE.rtf",
    "extensions": [
        {
            "extension": "pdf",
            "verb": "Print",
            "executable": app_exe_name,
            "context": "Print with Auto Print",
            "argument": '"%1"',
        }
    ],
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
                component_name,
                "{87CE1A83-346A-470C-9214-891B42186849}",
                "TARGETDIR",
                0,
                None,
                app_exe_name,
            )
        ],
        "Registry": registry_entries,
        "RemoveRegistry": remove_registry_entries,
        "ProgId": [
            (
                "AutoPrint.PDF",  # Primary key (ID of the ProgId entry)
                None,  # Parent ProgId (used for hierarchy, None if not nested)
                "Auto Print PDF Document",  # Description (used for display)
                context_menu_verb,  # Command (name of verb used in action, e.g., open, print)
                "AutoPrintIcon",  # Icon reference (defined in Icon table)
                None,  # Icon index (if using a multi-icon file, None = default)
            ),
        ],
        "Icon": [
            (
                "AutoPrintIcon",  # Primary key (ID of the Icon entry)
                "printer.ico",  # Path to the icon file
            ),
        ],
    },
}


def txt_to_rtf(input_path: str, output_path: str) -> None:
    text = Path(input_path).read_text(encoding="utf-8")

    # Basic RTF header and footer
    rtf_content = r"{\rtf1\ansi\deff0" + "\n"
    for line in text.splitlines():
        escaped_line = line.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")
        rtf_content += escaped_line + r"\line" + "\n"
    rtf_content += "}"

    Path(output_path).write_text(rtf_content, encoding="utf-8")


# Usage
txt_to_rtf("LICENSE", "LICENSE.rtf")

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
            "include_files": ["config.json", "LICENSE"],
        },
        "bdist_msi": bdist_msi_options,
    },
    executables=executables,
)
