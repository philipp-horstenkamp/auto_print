"""The goal of this project is to simplify the tedious task or printing similar forms.

1. The program is started with a filepath as an argument.
2. The filename gets extracted.
3. The filename is compared to a list of suffixes and prefixes.
4. If suffix and prefix are a match, the file gets executed.
   If a suffix or a prefix is not given, the comparison is true either way.
5. The file is then either Printed and/or shown depending on the configuration.

Everything is logged and can be locked up in the auto_print.log file!
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Final

import win32api  # type: ignore
import win32print  # type: ignore

# Constants
EXPECTED_ARG_COUNT: Final[int] = 2
PRINTER_NOT_FOUND_ERROR: Final[int] = 1801


def get_parser():
    """Create an argument parser for the auto_print_execute module.

    This function is used for documentation only.

    Returns:
        argparse.ArgumentParser: The argument parser
    """
    parser = argparse.ArgumentParser(
        description="Auto-print: A document routing application that automatically decides whether to print documents directly or open them with the default application based on filename patterns."
    )
    parser.add_argument("file_path", help="Path to the file to be processed", type=str)
    return parser


# defines the path of the printer config JSON file.
AUTO_PRINTER_FOLDER: Final[Path] = Path.home() / Path("auto-printer")

if not AUTO_PRINTER_FOLDER.exists():
    AUTO_PRINTER_FOLDER.mkdir(exist_ok=True)

PRINTER_CONFIG_PATH: Final[Path] = AUTO_PRINTER_FOLDER / Path(
    "auto-printer-config.json"
)

LOG_FILE: Final[Path] = AUTO_PRINTER_FOLDER / Path("auto_print.log")

# Try to load the ghostscript api.
# This program will shut down if ghostscript is not installed.


def get_default_printer() -> str:
    """Returns the default printers name."""
    try:
        return str(win32print.GetDefaultPrinter())
    except RuntimeError:
        return "No default printer"


def get_printer_list() -> list[str]:
    """Returns a list of printers."""
    return [section[1].split(",")[0] for section in win32print.EnumPrinters(2)]


# noinspection PyBroadException
def printer_pdf_reader(file_path: str, filename: str, printer_name: str) -> None:
    """Prints a document via the adobe PDF reader.

    :param filename: The name of the file that should be printed.
    :param file_path: The path of the file that should be printed.
    :param printer_name: The name of the printer that should be used.
    :return: None
    """
    logging.info(
        f'The printer "{printer_name}" will be chosen to print the file "{printer_name}" on "{file_path}"\n'
        "While showing the file!",
    )
    try:
        h_printer = win32print.OpenPrinter(printer_name)
        try:
            win32print.StartDocPrinter(h_printer, 1, (f"Auto-{filename}", None, None))
            try:
                win32api.ShellExecute(0, "print", file_path, None, ".", 0)
                win32print.StartPagePrinter(h_printer)
                win32print.WritePrinter(
                    h_printer, "test"
                )  # Instead of raw text, is there a way to print PDF File?
                win32print.EndPagePrinter(h_printer)
            except (OSError, RuntimeError):
                logging.exception("Error during printing")
            finally:
                win32print.EndDocPrinter(h_printer)
        except (OSError, RuntimeError):
            logging.exception("Error during document printing")
        finally:
            win32print.ClosePrinter(h_printer)
    except OSError as error:
        # Check for printer not found error
        if hasattr(error, "__getitem__") and error[0] == PRINTER_NOT_FOUND_ERROR:
            logging.exception(
                f'The printer with the name "{printer_name}" does not exist.'
            )
        else:
            raise


def install_ghostscript():
    """Help to install ghostscript if it's missing on the system.

    This function displays a message box to the user and offers to open
    the ghostscript download page in a web browser.
    """
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
    """Check if ghostscript is installed.

    This function attempts to import the ghostscript module.
    If the import fails, it calls the install_ghostscript function
    to guide the user through the installation process.
    """
    try:
        import ghostscript  # type: ignore # noqa: F401
    except RuntimeError:
        logging.exception("Can't import ghostscript. Installation probably not valid.")
        install_ghostscript()


def printer_ghost_script(file_path: str, printer_name: str) -> None:
    """Prints a document with the ghostscript printer.

    :param file_path: The path of the file that should be printed.
    :param printer_name: The name of the printer that should be used.
    :return: None
    """
    logging.info(
        f'The printer "{printer_name}" will be chosen to print the file {file_path}'
        " while not showing the file and using ghostscript!"
    )

    # try to load the ghostscript software!
    check_ghostscript()

    abspath = str(Path(file_path).resolve())
    subprocess.call(
        "gswin32c "
        f'-sOutputFile="%printer%{printer_name}" '
        "-dNOPROMPT "
        "-dPrinted "
        "-dBATCH "
        "-dNOPAUSE "
        "-dNOSAFER "
        "-sDEVICE=mswinpr2 "
        f"-sDEVICE#mswinpr2 {abspath}"
    )


def provision_fulfilled(file_name: str, prefix: str | None, suffix: str | None) -> bool:
    """Checks if a provision is fulfilled to execute a section of the Program.

    :param file_name: The name of the file to check.
    :param prefix: A prefix of the basename. Checks if the suffix is fulfilled.
    :param suffix: A suffix of the basename (file extension).
    :return: Returns true if all provisions are fulfilled.
    """
    if prefix and not file_name.startswith(prefix):
        return False
    return not (suffix and not file_name.endswith(suffix))


def configure_logger() -> None:
    """Configure the application logger.

    Sets up a file-based logger that writes to LOG_FILE with DEBUG level.
    The logger uses a timestamp format and appends to the existing log file.
    """
    try:
        logging.basicConfig(
            filename=LOG_FILE,
            format="%(asctime)-15s %(message)s",
            level=logging.DEBUG,
            filemode="a",
        )
    except (PermissionError, OSError) as error:
        print(f"Error configuring logger: {error}")


def load_printer_config(config_path: Path) -> dict[str, dict[str, str | bool]]:
    """Load printer configuration from a JSON file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dictionary containing printer configuration

    Raises:
        SystemExit: If the file is not found or contains invalid JSON (exit code 4)
    """
    try:
        with config_path.open(encoding="utf-8") as printer_config_file:
            return json.load(printer_config_file)
    except (FileNotFoundError, json.JSONDecodeError) as main_error:
        logging.exception("Error loading printer configuration")
        print(main_error)
        sys.exit(-4)


def main() -> None:
    """Execute the main auto-print functionality.

    This function:
    1. Configures the logger
    2. Processes command line arguments
    3. Validates the file to print
    4. Loads the printer configuration
    5. Determines the appropriate action based on filename comparisons
    6. Either prints the file or opens it with the default application

    Exit codes:
    -1: No file specified
    -2: Too many arguments
    -3: File does not exist
    -4: Error loading configuration
    -5: Empty file path
    """
    # loads the argument that where used to start this software.
    configure_logger()
    logging.info("Starting the program!")
    logging.info(f"Start program in: {Path(sys.path[0]).resolve()}")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    args = sys.argv  # loading the arguments
    for index, arg in enumerate(args):  # logging the arguments
        logging.debug(f'Argument {index} is "{arg}".')
        del index, arg

    if len(args) != EXPECTED_ARG_COUNT:
        logging.warning("No file to print specified!")
        sys.exit(-1)

    if len(args) > EXPECTED_ARG_COUNT:
        logging.warning(
            "There is more then one additional Argument. Please only use the filename as an Argument!"
        )
        sys.exit(-2)

    # The first argument should always be the path of the file.
    file_to_print_arg: str = args[1]

    if not file_to_print_arg:
        sys.exit(-5)
    file_to_print_name: str = Path(file_to_print_arg).name

    logging.info(f"File to print: {file_to_print_arg}")

    if not Path(file_to_print_arg).exists():  # checks if the file exists!
        logging.warning(
            "The file specified in the argument does not exist!\n"
            f'The specified path is: "{file_to_print_arg}".',
        )
        sys.exit(-3)
    printer_config = load_printer_config(PRINTER_CONFIG_PATH)

    for action_key in printer_config:
        printer_action = printer_config[action_key]
        if not printer_action.get(
            "active", False
        ):  # skip if printer action is disabled!
            logging.debug(f"The action {action_key} is not active.")
            continue
        if not provision_fulfilled(  # check if the printer action should be performed.
            file_to_print_name,
            printer_action.get("prefix", None),  # type: ignore
            printer_action.get("suffix", None),  # type: ignore
        ):
            continue

        logging.info(
            f"The action {action_key} is the valid action. This action will be executed!"
        )
        if printer_action.get("print", False):
            # Get printer value, ensuring it's a string
            printer_value = printer_action.get("printer", get_default_printer())
            printer_to_use: str = (
                printer_value
                if isinstance(printer_value, str)
                else get_default_printer()
            )
            if printer_action.get("show", True):
                printer_pdf_reader(
                    file_to_print_arg, file_to_print_name, printer_to_use
                )
                sys.exit(0)
            else:
                printer_ghost_script(file_to_print_arg, printer_to_use)
                sys.exit(0)
        else:
            logging.info("Showing the file! No printing!")
            os.startfile(file_to_print_arg)  # type: ignore
    logging.error("No valid action found.")


if __name__ == "__main__":
    main()
