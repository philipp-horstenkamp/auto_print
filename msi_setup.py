"""
Build modele.
"""

import os.path

from cx_Freeze import Executable, setup  # type: ignore

import auto_print
import auto_print.auto_print_config_generator as ag
import auto_print.auto_print_execute as ap

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {
    "packages": [],
    "excludes": [],
    "optimize": 2,
    "include_files": [
        "README.md",
        "README.md",
        "doc/ChoosePrinter.PNG",
        "doc/Settings.PNG",
        "printer-gear.ico",
        "printer.ico",
    ],
}

# directory_table = []

shortcut_table = [
    (
        "DesktopShortcut",  # Shortcut
        "DesktopFolder",  # Directory_
        "Auto Print Configurator",  # Name
        "TARGETDIR",  # Component_
        "[TARGETDIR]generator.exe",  # Target
        None,  # Arguments
        "auto_print",  # Description
        None,  # Hotkey
        os.path.abspath("printer-gear.ico"),  # Icon
        None,  # IconIndex
        None,  # ShowCmd
        "TARGETDIR",  # WkDir
    )
]

msi_data = {
    # "Directory": directory_table,
    "ProgId": [
        (
            "Prog.Id",
            None,
            None,
            "auto_print",
            "IconId",
            None,
        ),
    ],
    "Icon": [
        ("IconId", "printer.ico"),  # "icon.ico"
    ],
    "Shortcut": shortcut_table,
}

bdist_msi_options = {
    "add_to_path": True,
    "data": msi_data,
    "upgrade_code": "{FD1CA5B3-593F-4DF1-841D-2CFB9B2D4F58}",
    "summary_data": {
        "author": auto_print.__author__,
        "comments": str(auto_print.__description__),
        "keywords": ", ".join(["printer", "autoprinter", "ghostscript"]),
    },
    # "install_icon": "printer-gear.ico",
    "all_users": True,
    # "initial_target_dir" : None
}

BASE = "Win32GUI"
# base = 'Win32Service' if sys.platform=='win32' else None

executables = [
    Executable(ap.__file__, base=BASE, target_name="auto_print", icon="printer.ico"),
    Executable(
        ag.__file__, base=None, target_name="generator", icon="printer-gear.ico"
    ),
]

setup(
    name="auto_print",
    version=auto_print.__version__,
    description="auto_print",
    options={"build_exe": build_options, "bdist_msi": bdist_msi_options},
    executables=executables,
)
