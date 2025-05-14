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
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Final

import win32api  # type: ignore
import win32print  # type: ignore


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


# noinspection PyBroadException
def printer_pdf_reader(file_path: str, filename: str, printer_name: str) -> None:
    """
    Prints a document via the adobe pdf reader.
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
                )  # Instead of raw text is there a way to print PDF File ?
                win32print.EndPagePrinter(h_printer)
            except Exception:  # pylint: disable=W0703
                pass
            finally:
                win32print.EndDocPrinter(h_printer)
        except Exception:  # pylint: disable=W0703
            pass
        finally:
            win32print.ClosePrinter(h_printer)
    except Exception as error:  # pylint: disable=W0703
        # pylint: disable=unsubscriptable-object
        if error[0] == 1801:  # type: ignore
            logging.error(
                f'The printer with the name "{printer_name}" does not exists.'
            )
        else:
            raise error


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


# The main function should be started as shown above.
def main() -> None:  # noqa: PLR0912
    # loads the argument that where used to start this software.
    configure_logger()
    logging.info("Starting the program!")
    logging.info(f"Start programm in: {os.path.abspath(sys.path[0])}")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    args = sys.argv  # loading the arguments
    for index, arg in enumerate(args):  # logging the arguments
        logging.debug(f'Argument {index} is "{arg}".')
        del index, arg

    if len(args) != 2:
        logging.warning("No file to print specified!")
        sys.exit(-1)

    if len(args) > 2:
        logging.warning(
            "There is more then one additional Argument. Please only use the filename as an Argument!"
        )
        sys.exit(-2)

    # The first argument should always be the path of the file.
    # file_to_print_arg: str = os.path.abspath(args[1])
    file_to_print_arg: str = args[1]

    if not file_to_print_arg:
        sys.exit(-5)
    # file_to_print_folder: str = os.path.dirname(file_to_print_arg)
    file_to_print_name: str = os.path.basename(file_to_print_arg)

    logging.info(f"File to print: {file_to_print_arg}")

    if not os.path.exists(file_to_print_arg):  # checks if the file exists!
        logging.warning(
            "The file specified in the argument does not exist!\n"
            f'The specified path is: "{file_to_print_arg}".',
        )
        sys.exit(-3)
    try:
        with open(PRINTER_CONFIG_PATH, encoding="utf-8") as printer_config_file:
            printer_config = json.load(printer_config_file)
    except Exception as main_error:  # pylint: disable=broad-exception-caught
        logging.error(main_error)
        print(main_error)
        sys.exit(-4)

    for action_key in printer_config:
        printer_action = printer_config[action_key]
        if not printer_action.get(
            "active", "false"
        ):  # skip if printer action is disabled!
            logging.debug(f"The action {action_key} is not active.")
            continue
        if not provision_fulfilled(  # check if the printer action should be performed.
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
    logging.error("No valid action found.")


if __name__ == "__main__":
    main()
