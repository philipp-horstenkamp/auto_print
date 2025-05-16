"""Shared utilities for auto_print modules."""

import json
import logging
import os
import sys
import webbrowser
from pathlib import Path
from tkinter import messagebox
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
    """Configure a logger for the application."""
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
    """Get the default printer's name.

    Returns:
        str: The name of the default printer or "No default printer" if none is set.
    """
    try:
        return str(win32print.GetDefaultPrinter())
    except RuntimeError:
        return "No default printer"


def get_printer_list() -> list[str]:
    """Get a list of available printers.

    Returns:
        list[str]: A list of printer names.
    """
    return [section[1].split(",")[0] for section in win32print.EnumPrinters(2)]


def install_ghostscript() -> None:
    """Help install ghostscript if it's missing on the system.

    Displays a dialog to the user and offers to open the download page.
    Exits the program with code -5 after the dialog.
    """
    for sys_arg in sys.argv:
        logging.error(f"Started with arguments: {sys_arg}")

    messagebox.showerror(
        "Ghostscript missing!",
        "Ghostscript is not installed.\nPlease install ghostscript!",
    )
    action = messagebox.askyesno(
        "Install Ghostscript!", "Would you likte to download Ghostscript 64 bit?"
    )
    if action:
        webbrowser.open("https://ghostscript.com/releases/gsdnld.html", new=2)
    sys.exit(-5)


def check_ghostscript() -> None:
    """Check if ghostscript is installed.

    Attempts to import the ghostscript module. If it fails, calls install_ghostscript().
    """
    try:
        import ghostscript  # type: ignore # noqa: F401
    except RuntimeError as err:
        logging.exception(err)
        install_ghostscript()


def load_config_file() -> dict:
    """Load the configuration file.

    Returns:
        dict: The configuration data as a dictionary. Returns an empty dictionary if the file doesn't exist.
    """
    if not os.path.exists(PRINTER_CONFIG_PATH):
        return {}
    try:
        with open(PRINTER_CONFIG_PATH, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_config_file(config_data: dict) -> None:
    """Save the configuration to file.

    Args:
        config_data: The configuration data to save.
    """
    with open(PRINTER_CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(config_data, file, indent=2)
    print("Config saved!")


def provision_fulfilled(file_name: str, prefix: str | None, suffix: str | None) -> bool:
    """Check if a provision is fulfilled to execute a section of the program.

    Args:
        file_name: The name of the file to check.
        prefix: A prefix of the basename. Checks if the file starts with this prefix.
        suffix: A suffix of the basename (file extension). Checks if the file ends with this suffix.

    Returns:
        bool: True if all provisions are fulfilled, False otherwise.
    """
    if prefix and not file_name.startswith(prefix):
        return False
    if suffix and not file_name.endswith(suffix):
        return False
    return True
