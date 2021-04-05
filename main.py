import json
import locale
import logging
import os
import sys

import ghostscript
import win32api
import win32print


# import render_to_pdf


def auto_print2():
    name = win32print.GetDefaultPrinter()  # verify that it matches with the name of your printer
    printdefaults = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}  # Doesn't work with PRINTER_ACCESS_USE
    handle = win32print.OpenPrinter(name, printdefaults)
    level = 2
    attributes = win32print.GetPrinter(handle, level)
    # attributes['pDevMode'].Duplex = 1  # no flip
    # attributes['pDevMode'].Duplex = 2  # flip up
    attributes['pDevMode'].Duplex = 3  # flip over
    win32print.SetPrinter(handle, level, attributes, 0)

    win32print.GetPrinter(handle, level)['pDevMode'].Duplex

    win32api.ShellExecute(0, 'print', 'PRINT_TEST.pdf', '.', '/manualstoprint', 0)


def auto_print3(filepath: str, printer_name: str):
    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ('PrintJobName', None, 'RAW'))
        try:
            win32api.ShellExecute(0, "print", filepath, None, ".", 0)
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, "test")  # Instead of raw text is there a way to print PDF File ?
            win32print.EndPagePrinter(hPrinter)
        finally:
            win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)


def auto_ghost1(filename, printer_name: str):
    # p_name = "Minolta Main"
    # p_name = r"\\192.168.10.109\Ettiketen Drucker"
    args = [
        "-dPrinted", "-dBATCH", "-dNOSAFER", "-dNOPAUSE", "-dNOPROMPT", "-q",
        "-dNumCopies#1",
        "-sDEVICE#mswinpr2",
        "-dNODISPLAY",  # TODO test
        f'-sOutputFile#"%printer%{printer_name}"',
        f'"{filename}"'
    ]

    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in args]
    ghostscript.Ghostscript(*args)


def execute_action(fname: str, fpath: str, prefix: str, suffix: str) -> bool:
    if not fname.startswith(prefix):
        return False
    if not fname.endswith(suffix):
        return False

    return True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = sys.argv
    temp_arg = args[0]
    temp_arg = temp_arg.replace("\\", "/")
    root_folder: str = temp_arg[:temp_arg.rfind("/")]

    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(filename=f"{root_folder}/auto_print.log", format=FORMAT, level=logging.DEBUG, filemode='a')
    logging.info("Starting the program!")
    logging.info(f"Start path: {args[0]}")
    logging.info(f"Start p1: {sys.path[0]}")

    for index, arg in enumerate(args):
        logging.debug(f"Argument {index} is \"{arg}\".")

    if len(args) == 1:
        logging.warning("No file to print specified!")
        sys.exit(-1)

    if len(args) > 2:
        logging.warning("There is more then one argument! Please use only the filename as an Argument!")
        sys.exit(-2)
    filepath = args[1]
    filename = filepath[filepath.rfind(f"\\") + 1:]

    if not os.path.exists(filepath):
        logging.warning("The file specified in the argument does not exist!")
        logging.warning(f"The specified path is: \"{filepath}\".")
        sys.exit(-3)

    try:
        with open(f"{root_folder}/config.json") as json_file:
            config = json.load(json_file)
    except Exception as e:
        logging.error(e)
        print(e)
        sys.exit(-4)

    for c in config:
        action = config[c]
        if not action.get("active", "false"):  # skip
            logging.debug(f"The action {c} is not active.")
            continue
        if execute_action(filename, filepath, action.get("prefix", ""), action.get("suffix", "")):
            logging.info(f"The action {c} is the valid action. No other action will be performed!")
            print(f"Action to print {c}")
            if bool(action.get("print", "false")):
                p_name: str = action.get("printer", win32print.GetDefaultPrinter())
                if bool(action.get("show", "true")):

                    logging.info(f"The printer {p_name} will be chosen to print the file {filename}"
                                 f" while showing the file!")
                    auto_print3(filepath, p_name)
                    break
                else:
                    logging.info(f"The printer {p_name} will be chosen to print the file {filename}"
                                 f" while not showing the file and using ghostscript!")
                    auto_ghost1(filepath, p_name)
                    if bool(action.get("delete", "false")):
                        try:
                            # os.remove(filepath)
                            break
                        except PermissionError as pe:
                            print(pe)
            else:
                logging.info(f"Showing the file!")
                os.system("start " + filepath)
        else:
            continue
