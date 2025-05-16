"""
The goal of this project is to simplify the tedious task or printing similar forms.

1. The program is started with a filepath as an argument.
2. The filename gets extracted.
3. The filename is compared to a list of suffixes and prefixes.
4. If suffix and prefix are a match the file gets executed.
If a suffix or a prefix is not given the comparison is true either way.
5. The file is then eiter Printed and/or shown depending on the configuration.

Everything is logged and can be locked up in the auto_print.log file!
"""

import argparse
import os
import subprocess
import sys
from tkinter import messagebox

import win32api  # type: ignore
import win32print  # type: ignore

from auto_print.utils import (
    PRINTER_CONFIG_PATH,
    LOG_FILE,
    check_ghostscript,
    configure_logger,
    get_default_printer,
    get_printer_list,
    load_config_file,
    provision_fulfilled,
)


def get_parser():
    """
    Create an argument parser for the auto_print_execute module.
    This function is used for documentation purposes only.

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

if not os.path.exists(AUTO_PRINTER_FOLDER):
    os.mkdir(AUTO_PRINTER_FOLDER)

PRINTER_CONFIG_PATH: Final[Path] = AUTO_PRINTER_FOLDER / Path(
    "auto-printer-config.json"
)

LOG_FILE: Final[Path] = AUTO_PRINTER_FOLDER / Path("auto_print.log")

# Try to load the ghostscript api.
# This programm will shut down if ghostscript is not installed.


def get_default_printer() -> str:
    """Returns the default printers name"""
    try:
        return str(win32print.GetDefaultPrinter())
    except RuntimeError:
        return "No default printer"


def get_printer_list() -> list[str]:
    """Returns a list of printers."""
    return [section[1].split(",")[0] for section in win32print.EnumPrinters(2)]


def log_print_operation(file_path: str, printer_name: str) -> None:
    """
    Log information about the print operation.

    Args:
        file_path: The path of the file that should be printed.
        printer_name: The name of the printer that should be used.
    """
    import logging
    logging.info(
        f'The printer "{printer_name}" will be chosen to print the file on "{file_path}"\n'
        "While showing the file!",
    )


def execute_print_command(file_path: str, h_printer: object) -> None:
    """
    Execute the print command using ShellExecute.

    Args:
        file_path: The path of the file that should be printed.
        h_printer: The printer handle.
    """
    win32api.ShellExecute(0, "print", file_path, None, ".", 0)
    win32print.StartPagePrinter(h_printer)
    win32print.WritePrinter(h_printer, "test")  # Instead of raw text is there a way to print PDF File ?
    win32print.EndPagePrinter(h_printer)


def handle_printer_error(error: Exception, printer_name: str) -> None:
    """
    Handle printer-related errors.

    Args:
        error: The exception that occurred.
        printer_name: The name of the printer that was used.
    """
    import logging
    # pylint: disable=unsubscriptable-object
    if hasattr(error, "args") and len(error.args) > 0 and error.args[0] == 1801:
        logging.error(
            f'The printer with the name "{printer_name}" does not exists.'
        )
    else:
        raise error


# noinspection PyBroadException
def printer_pdf_reader(file_path: str, filename: str, printer_name: str) -> None:
    """
    Prints a document via the adobe pdf reader.

    Args:
        filename: The name of the file that should be printed.
        file_path: The path of the file that should be printed.
        printer_name: The name of the printer that should be used.
    """
    log_print_operation(file_path, printer_name)

    try:
        h_printer = win32print.OpenPrinter(printer_name)
        try:
            win32print.StartDocPrinter(h_printer, 1, (f"Auto-{filename}", None, None))
            try:
                execute_print_command(file_path, h_printer)
            except Exception:  # pylint: disable=W0703
                pass
            finally:
                win32print.EndDocPrinter(h_printer)
        except Exception:  # pylint: disable=W0703
            pass
        finally:
            win32print.ClosePrinter(h_printer)
    except Exception as error:  # pylint: disable=W0703
        handle_printer_error(error, printer_name)


def install_ghostscript():
    """Helps to install ghostscript if it's missing on the system"""
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
        import webbrowser

        webbrowser.open("https://ghostscript.com/releases/gsdnld.html", new=2)
    sys.exit(-5)


def check_ghostscript():
    """Check if ghostscript is installed"""
    try:
        import ghostscript  # type: ignore # noqa: F401
    except RuntimeError as err:
        logging.error(err)
        install_ghostscript()


def printer_ghost_script(file_path: str, printer_name: str) -> None:
    """
    Prints a document with the ghostscript printer.
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

    abspath = os.path.abspath(file_path)
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
    """
    Checks if a provision is fulfilled to execute a section of the Programm.
    :param file_name:
    :param prefix: A prefix of the basename. Checks if the suffix is fulfilled.
    :param suffix: A suffix of the basename (file extension).
    :return: Returns true if all provisions are fulfilled.
    """
    if prefix and not file_name.startswith(prefix):
        return False
    if suffix and not file_name.endswith(suffix):
        return False
    return True


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


def validate_arguments() -> str:
    """
    Validate command line arguments and return the file path.

    Returns:
        The path to the file to print.
    """
    import logging
    args = sys.argv

    for index, arg in enumerate(args):
        logging.debug(f'Argument {index} is "{arg}".')

    if len(args) > 2:
        logging.warning(
            "There is more then one additional Argument. Please only use the filename as an Argument!"
        )
        sys.exit(-2)

    if len(args) != 2:
        logging.warning("No file to print specified!")
        sys.exit(-1)

    file_to_print_arg: str = args[1]

    if not file_to_print_arg:
        sys.exit(-5)

    logging.info(f"File to print: {file_to_print_arg}")

    if not os.path.exists(file_to_print_arg):
        logging.warning(
            "The file specified in the argument does not exist!\n"
            f'The specified path is: "{file_to_print_arg}".',
        )
        sys.exit(-3)

    return file_to_print_arg


def process_file(file_to_print_arg: str, file_to_print_name: str, printer_config: dict) -> None:
    """
    Process the file according to the printer configuration.

    Args:
        file_to_print_arg: The path to the file to print.
        file_to_print_name: The name of the file to print.
        printer_config: The printer configuration.
    """
    import logging

    for action_key in printer_config:
        printer_action = printer_config[action_key]
        if not printer_action.get("active", "false"):
            logging.debug(f"The action {action_key} is not active.")
            continue

        if not provision_fulfilled(
            file_to_print_name,
            printer_action.get("prefix", None),
            printer_action.get("suffix", None),
        ):
            continue

        logging.info(
            f"The action {action_key} is the valid action. This action will be executed!"
        )

        if bool(printer_action.get("print", "false")):
            printer_to_use: str = printer_action.get("printer", get_default_printer())
            if bool(printer_action.get("show", "true")):
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
            sys.exit(0)

    logging.error("No valid action found.")


# The main function should be started as shown above.
def main() -> None:  # noqa: PLR0912
    import logging

    # Configure logging
    configure_logger()
    logging.info("Starting the program!")
    logging.info(f"Start programm in: {os.path.abspath(sys.path[0])}")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # Validate arguments and get file path
    file_to_print_arg = validate_arguments()
    file_to_print_name = os.path.basename(file_to_print_arg)

    # Load printer configuration
    try:
        printer_config = load_config_file()
    except Exception as main_error:  # pylint: disable=broad-exception-caught
        logging.error(main_error)
        print(main_error)
        sys.exit(-4)

    # Process the file
    process_file(file_to_print_arg, file_to_print_name, printer_config)


if __name__ == "__main__":
    main()
