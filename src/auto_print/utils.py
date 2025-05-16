"""Shared utilities for auto_print modules.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Final

import win32print  # type: ignore

# Constants
AUTO_PRINTER_FOLDER: Final[Path] = Path.home() / Path("auto-printer")

if not os.path.exists(AUTO_PRINTER_FOLDER):
    os.mkdir(AUTO_PRINTER_FOLDER)

PRINTER_CONFIG_PATH: Final[Path] = AUTO_PRINTER_FOLDER / Path(
    "auto-printer-config.json"
)

LOG_FILE: Final[Path] = AUTO_PRINTER_FOLDER / Path("auto_print.log")


def configure_logger() -> None:
    """Configure a logger."""
    try:
        logging.basicConfig(
            filename=LOG_FILE,
            format="%(asctime)-15s %(message)s",
            level=logging.DEBUG,
            filemode="a",
        )
    except Exception as error:  # pylint: disable=broad-exception-caught
        print(error)


def get_default_printer() -> str:
    """Returns the default printers name"""
    try:
        return str(win32print.GetDefaultPrinter())
    except RuntimeError:
        return "No default printer"


def get_printer_list() -> list[str]:
    """Returns a list of printers."""
    return [section[1].split(",")[0] for section in win32print.EnumPrinters(2)]


def install_ghostscript():
    """Helps to install ghostscript if it's missing on the system"""
    for sys_arg in sys.argv:
        logging.error(f"Started with arguments: {sys_arg}")

    from tkinter import messagebox

    messagebox.showerror(
        "Ghostscript missing!",
        "Ghostscript is not installed.\nPlease install ghostscript!",
    )
    action = messagebox.askyesno(
        "Install Ghostscript!", "Would you likte to download Ghostscript 64 bit?"
    )
    if action:
        import webbrowser

        webbrowser.open("https://ghostscript.com/releases/gsdnld.html", new=2)
    sys.exit(-5)


def check_ghostscript():
    """Check if ghostscript is installed"""
    try:
        import ghostscript  # type: ignore # noqa: F401
    except RuntimeError as err:
        logging.exception(err)
        install_ghostscript()


def load_config_file() -> dict:
    """Loads the configuration file."""
    if not os.path.exists(PRINTER_CONFIG_PATH):
        return {}
    try:
        with open(PRINTER_CONFIG_PATH, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_config_file(config_data: dict) -> None:
    """Saves the configuration to file."""
    with open(PRINTER_CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(config_data, file, indent=2)
    print("Config saved!")


def provision_fulfilled(file_name: str, prefix: str | None, suffix: str | None) -> bool:
    """Checks if a provision is fulfilled to execute a section of the Programm.

    Args:
        file_name: The name of the file to check.
        prefix: A prefix of the basename. Checks if the suffix is fulfilled.
        suffix: A suffix of the basename (file extension).

    Returns:
        True if all provisions are fulfilled.

    """
    if prefix and not file_name.startswith(prefix):
        return False
    if suffix and not file_name.endswith(suffix):
        return False
    return True
