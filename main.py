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

import json
import locale
import logging
import os
import sys

import win32api
import win32print

# defines the path of the printer config JSON file.
PRINTER_CONFIG_PATH: str = "config.json"

LOG_FILE: str = "auto_print.log"


# Try to load the ghostscript api.
# This programm will shut down if ghostscript is not installed.


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
        'The printer "%s" will be chosen to print the file "%s"'
        "\nWhile showing the file!",
        printer_name,
        file_to_print_arg,
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
    except Exception as err:  # pylint: disable=W0703
        if err[0] == 1801:  # type: ignore
            logging.error(
                'The printer with the name "%s" does not exists.', printer_name
            )
        else:
            raise err


def printer_ghost_script(file_path: str, printer_name: str) -> None:
    """
    Prints a document with the ghostscript printer.
    :param file_path: The path of the file that should be printed.
    :param printer_name: The name of the printer that should be used.
    :return: None
    """
    logging.info(
        "The printer %s will be chosen to print the file %s"
        " while not showing the file and using ghostscript!",
        printer_name,
        file_path,
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

    with ghostscript.Ghostscript(*printer_args) as gs:
        gs.run_filename(file_to_print_arg.encode(locale.getpreferredencoding()))


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

    # try to load the ghostscript software!
    try:
        import ghostscript
    except RuntimeError as e:
        logging.error(e)
        sys.exit(-5)

    logging.info("Starting the program!")
    logging.info("Start programm in: %s" % os.path.abspath(sys.path[0]))

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

    logging.info("File to print: %s", file_to_print_arg)

    if not os.path.exists(file_to_print_arg):  # checks if the file exists!
        logging.warning(
            "The file specified in the argument does not exist!\n"
            'The specified path is: "%s".',
            file_to_print_arg,
        )
        sys.exit(-3)

    try:
        with open(PRINTER_CONFIG_PATH) as printer_config_file:
            printer_config = json.load(printer_config_file)
    except Exception as e:
        logging.error(e)
        print(e)
        sys.exit(-4)

    for action_key in printer_config:
        printer_action = printer_config[action_key]
        if not printer_action.get(
            "active", "false"
        ):  # skip if printer action is disabled!
            logging.debug("The action %s is not active.", action_key)
            continue
        if not provision_fulfilled(  # check if the printer action should be performed.
            file_to_print_name,
            printer_action.get("prefix", None),
            printer_action.get("suffix", None),
        ):
            continue

        logging.info(
            "The action %s is the valid action. This action will be executed!",
            action_key,
        )
        print('Action to print "%s"', action_key)
        if bool(printer_action.get("print", "false")):
            printer_to_use: str = printer_action.get(
                "printer", win32print.GetDefaultPrinter()
            )
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
            os.startfile(file_to_print_arg)
            os.system("start " + file_to_print_arg.replace("\\", "/"))
            sys.exit(0)
    logging.error("No valid action found.")
