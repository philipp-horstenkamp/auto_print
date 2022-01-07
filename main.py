# -*- coding: utf-8 -*-
import json
import locale
import logging
import os
import sys

import win32api
import win32print

# defines the path of the printer config JSON file.
PRINTER_CONFIG_PATH: str = "config.json"
# defines the generell config file.
# GENERELL_CONFIG_FILE: str = ""  # todo define this file.

LOG_FILE: str = "auto_print.log"


# Try to load the ghostscript api.
# This programm will shut down if ghostscript is not installed.


def printer_pdf_reader(file_path: str, printer_name: str) -> None:
    """
    Prints a document via the adobe pdf reader.
    :param file_path: The path of the file that should be printed.
    :param printer_name: The name of the printer that should be used.
    :return: None
    """
    logging.info(
        f'The printer "{printer_name}" will be chosen to print the file "{file_to_print_arg}"'
        "\nWhile showing the file!"
    )

    h_printer = win32print.OpenPrinter(printer_name)
    try:
        try:
            win32api.ShellExecute(0, "print", file_path, None, ".", 0)
            win32print.StartPagePrinter(h_printer)
            win32print.WritePrinter(
                h_printer, "test"
            )  # Instead of raw text is there a way to print PDF File ?
            win32print.EndPagePrinter(h_printer)
        finally:
            win32print.EndDocPrinter(h_printer)
    finally:
        win32print.ClosePrinter(h_printer)


def printer_ghost_script(file_path: str, printer_name: str) -> None:
    """
    Prints a document with the ghostscript printer.
    :param file_path: The path of the file that should be printed.
    :param printer_name: The name of the printer that should be used.
    :return: None
    """
    logging.info(
        f"The printer {printer_name} will be chosen to print the file {file_path}"
        f" while not showing the file and using ghostscript!"
    )

    printer_args = [
        "-dPrinted",
        "-dBATCH",
        "-dNOSAFER",
        "-dNOPAUSE",
        "-dNOPROMPT",
        "-q",
        "-dNumCopies#1",
        "-sDEVICE#mswinpr2",
        f'-sOutputFile#"%printer%{printer_name}"',
    ]

    with ghostscript.Ghostscript(*printer_args[:]) as gs:
        gs.run_filename(file_to_print_arg.encode(locale.getpreferredencoding()))


def provision_fulfilled(file_name: str, prefix: str | None, suffix: str | None) -> bool:
    """
    Checks if a provision is fulfilled to execute a section of the Programm.
    :param file_name:
    :param prefix: A prefix of the basename. Checks if the suffix is fulfilled.
    :param suffix: A suffix of the basename (file extension).
    :return: Returns true if all provisions are fulfilled.
    """
    if not prefix or not file_name.startswith(prefix):
        return False
    if not suffix or not file_name.endswith(suffix):
        return False
    return True


# The main function should be started as shown above.
if __name__ == "__main__":
    # loads the argument that where used to start this software.

    logging.basicConfig(
        filename=f"{LOG_FILE}",
        format="%(asctime)-15s %(message)s",
        level=logging.DEBUG,
        filemode="a",
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    # todo check for a config test argument!

    # try to load the ghostscript software!
    try:
        import ghostscript
    except RuntimeError as e:
        logging.error(e)
        sys.exit(-5)

    logging.info("Starting the program!")
    logging.info(f"Start programm in: {os.path.abspath(sys.path[0])}")

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

    # file_to_print_arg = file_to_print_arg.replace("\\", "/")  # Transform the path
    # todo check if tha abspath needs to be transformed.

    # file_to_print_folder: str = os.path.dirname(file_to_print_arg)
    file_to_print_name: str = os.path.basename(file_to_print_arg)

    logging.info(f"File to print: {file_to_print_arg}")

    if not os.path.exists(file_to_print_arg):  # checks if the file exists!
        logging.warning(
            "The file specified in the argument does not exist!\n"
            f'The specified path is: "{file_to_print_arg}".'
        )
        sys.exit(-3)

    try:
        with open(PRINTER_CONFIG_PATH) as printer_config_file:
            printer_config = json.load(printer_config_file)
    except Exception as e:
        # todo start a tkinter dialoge here. Only import what is needed here!
        logging.error(e)
        print(e)
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
        print(f'Action to print "{action_key}"')
        if bool(printer_action.get("print", "false")):
            printer_to_use: str = printer_action.get(
                "printer", win32print.GetDefaultPrinter()
            )
            if bool(printer_action.get("show", "true")):
                printer_pdf_reader(file_to_print_arg, printer_to_use)
                sys.exit(0)
            else:
                printer_ghost_script(file_to_print_arg, printer_to_use)
                sys.exit(0)
        else:
            logging.info("Showing the file!")
            os.system("start " + file_to_print_arg)
