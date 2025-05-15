"""
cx_Freeze setup script for building executable files.

This script configures cx_Freeze to build standalone executables for:
1. auto_print_config_generator - Configuration tool for auto_print
2. auto_print_execute - Main execution tool for auto_print
"""

import sys

from cx_Freeze import Executable, setup

import auto_print
import auto_print.auto_print_config_generator as ag
import auto_print.auto_print_execute as ap

# Dependencies are automatically detected, but it might need fine tuning
build_options = {
    "packages": ["auto_print"],
    "excludes": [],
    "optimize": 2,
    "include_files": [
        "README.md",
        "printer-gear.ico",
        "printer.ico",
    ],
    "build_exe": "build/exe.new",  # Use a different build directory
}

# Determine the base for each executable
# For GUI applications on Windows, use "Win32GUI"
# For console applications, use None
BASE_GUI = "Win32GUI" if sys.platform == "win32" else None
BASE_CONSOLE = None

executables = [
    # Main auto_print execution tool (GUI application)
    Executable(
        script=ap.__file__,
        base=BASE_GUI,
        target_name="auto_print_execute",
        icon="printer.ico",
    ),
    # Configuration generator tool (Console application)
    Executable(
        script=ag.__file__,
        base=BASE_CONSOLE,
        target_name="auto_print_config_generator",
        icon="printer-gear.ico",
    ),
]

setup(
    name="auto_print",
    version=auto_print.__version__,
    description="Auto Print - Automatic document printing tool",
    author=auto_print.__author__,
    options={"build_exe": build_options},
    executables=executables,
)
