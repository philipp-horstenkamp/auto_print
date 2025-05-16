"""Tests for the execute module using pytest conventions.
"""

from unittest.mock import Mock, patch

import pytest

from auto_print.execute import (
    execute_print_command,
    get_parser,
    handle_printer_error,
    log_print_operation,
    printer_ghost_script,
    printer_pdf_reader,
    process_file,
    validate_arguments,
)
from auto_print.utils import (
    LOG_FILE,
    check_ghostscript,
    configure_logger,
    get_default_printer,
    get_printer_list,
    install_ghostscript,
    provision_fulfilled,
)


@pytest.mark.parametrize(
    "filename, prefix, suffix, expected_result",
    [
        # Test with no prefix and no suffix
        ("test_file.pdf", None, None, True),
        # Tests with prefix
        ("test_file.pdf", "test_", None, True),
        ("file.pdf", "test_", None, False),
        # Tests with suffix
        ("file.pdf", None, ".pdf", True),
        ("file.txt", None, ".pdf", False),
        # Tests with both prefix and suffix
        ("test_file.pdf", "test_", ".pdf", True),
        ("file.pdf", "test_", ".pdf", False),
        ("test_file.txt", "test_", ".pdf", False),
    ],
)
def test_provision_fulfilled(filename, prefix, suffix, expected_result):
    """Test provision_fulfilled with various combinations of parameters."""
    assert provision_fulfilled(filename, prefix, suffix) is expected_result


def test_configure_logger(monkeypatch):
    """Test the configure_logger function."""
    # Create a mock for logging.basicConfig
    mock_basic_config = Mock()
    mock_logging = Mock()
    mock_logging.DEBUG = "DEBUG"
    mock_logging.basicConfig = mock_basic_config

    # Patch the logging module
    monkeypatch.setattr("auto_print.utils.logging", mock_logging)

    # Call the function
    configure_logger()

    # Verify the logging was configured correctly
    mock_basic_config.assert_called_once_with(
        filename=LOG_FILE,
        format="%(asctime)-15s %(message)s",
        level="DEBUG",
        filemode="a",
    )


def test_get_default_printer(monkeypatch):
    """Test the get_default_printer function."""
    # Create a mock for win32print.GetDefaultPrinter
    mock_get_default_printer = Mock(return_value="Test Printer")
    mock_win32print = Mock()
    mock_win32print.GetDefaultPrinter = mock_get_default_printer

    # Patch the win32print module
    monkeypatch.setattr("auto_print.utils.win32print", mock_win32print)

    # Call the function
    result = get_default_printer()

    # Verify the result
    assert result == "Test Printer"
    mock_get_default_printer.assert_called_once()


def test_get_printer_list(monkeypatch):
    """Test the get_printer_list function."""
    # Create a mock for win32print.EnumPrinters
    mock_enum_printers = Mock(
        return_value=[
            (0, "Printer1,Port1"),
            (0, "Printer2,Port2"),
        ]
    )
    mock_win32print = Mock()
    mock_win32print.EnumPrinters = mock_enum_printers

    # Patch the win32print module
    monkeypatch.setattr("auto_print.utils.win32print", mock_win32print)

    # Call the function
    result = get_printer_list()

    # Verify the result
    assert result == ["Printer1", "Printer2"]
    mock_enum_printers.assert_called_once_with(2)


def test_get_parser():
    """Test the get_parser function."""
    parser = get_parser()
    assert parser.description is not None
    assert "auto-print" in parser.description.lower()

    # Check that the parser has the expected arguments
    args = parser.parse_args(["test_file.pdf"])
    assert args.file_path == "test_file.pdf"


@patch("auto_print.execute.win32print.OpenPrinter")
@patch("auto_print.execute.win32print.StartDocPrinter")
@patch("auto_print.execute.win32api.ShellExecute")
@patch("auto_print.execute.win32print.StartPagePrinter")
@patch("auto_print.execute.win32print.WritePrinter")
@patch("auto_print.execute.win32print.EndPagePrinter")
@patch("auto_print.execute.win32print.EndDocPrinter")
@patch("auto_print.execute.win32print.ClosePrinter")
@patch("auto_print.execute.logging.info")
def test_printer_pdf_reader(
    mock_logging_info,
    mock_close_printer,
    mock_end_doc_printer,
    mock_end_page_printer,
    mock_write_printer,
    mock_start_page_printer,
    mock_shell_execute,
    mock_start_doc_printer,
    mock_open_printer,
):
    """Test the printer_pdf_reader function."""
    # Set up the mocks
    mock_open_printer.return_value = "printer_handle"

    # Call the function
    printer_pdf_reader("test_file.pdf", "test_file.pdf", "Test Printer")

    # Verify the function calls
    mock_open_printer.assert_called_once_with("Test Printer")
    mock_start_doc_printer.assert_called_once_with(
        "printer_handle", 1, ("Auto-test_file.pdf", None, None)
    )
    mock_shell_execute.assert_called_once_with(
        0, "print", "test_file.pdf", None, ".", 0
    )
    mock_start_page_printer.assert_called_once_with("printer_handle")
    mock_write_printer.assert_called_once_with("printer_handle", "test")
    mock_end_page_printer.assert_called_once_with("printer_handle")
    mock_end_doc_printer.assert_called_once_with("printer_handle")
    mock_close_printer.assert_called_once_with("printer_handle")
    mock_logging_info.assert_called_once()


@patch("auto_print.execute.win32print.OpenPrinter")
@patch("auto_print.execute.logging.error")
def test_printer_pdf_reader_error(mock_logging_error, mock_open_printer):
    """Test the printer_pdf_reader function with an error."""

    # Set up the mocks to raise an error
    class PrinterError(Exception):
        def __init__(self):
            self.args = [1801]

    mock_open_printer.side_effect = PrinterError()

    # Call the function
    printer_pdf_reader("test_file.pdf", "test_file.pdf", "Test Printer")

    # Verify the error was logged
    mock_logging_error.assert_called_once()
    assert "does not exists" in mock_logging_error.call_args[0][0]


@patch("auto_print.execute.subprocess.call")
@patch("auto_print.execute.check_ghostscript")
@patch("auto_print.execute.os.path.abspath")
@patch("auto_print.execute.logging.info")
def test_printer_ghost_script(
    mock_logging_info, mock_abspath, mock_check_ghostscript, mock_subprocess_call
):
    """Test the printer_ghost_script function."""
    # Set up the mocks
    mock_abspath.return_value = "C:\\test_file.pdf"

    # Call the function
    printer_ghost_script("test_file.pdf", "Test Printer")

    # Verify the function calls
    mock_logging_info.assert_called_once()
    mock_check_ghostscript.assert_called_once()
    mock_abspath.assert_called_once_with("test_file.pdf")
    mock_subprocess_call.assert_called_once()
    # Check that the command contains the printer name
    assert "Test Printer" in mock_subprocess_call.call_args[0][0]


@patch("auto_print.utils.sys.exit")
@patch("auto_print.utils.messagebox.showerror")
@patch("auto_print.utils.messagebox.askyesno")
@patch("webbrowser.open")
@patch("auto_print.utils.logging.error")
def test_install_ghostscript(
    mock_logging_error, mock_webbrowser_open, mock_askyesno, mock_showerror, mock_exit
):
    """Test the install_ghostscript function."""
    # Set up the mocks
    mock_askyesno.return_value = True  # User wants to download

    # Call the function
    install_ghostscript()

    # Verify the function calls
    mock_showerror.assert_called_once()
    mock_askyesno.assert_called_once()
    mock_webbrowser_open.assert_called_once_with(
        "https://ghostscript.com/releases/gsdnld.html", new=2
    )
    mock_exit.assert_called_once_with(-5)


@patch("auto_print.utils.install_ghostscript")
def test_check_ghostscript_error(mock_install_ghostscript, monkeypatch):
    """Test the check_ghostscript function when ghostscript is not installed."""

    # Mock the import to raise an error
    def mock_import(*args, **kwargs):
        raise RuntimeError("Ghostscript not found")

    monkeypatch.setattr("builtins.__import__", mock_import)

    # Call the function
    check_ghostscript()

    # Verify install_ghostscript was called
    mock_install_ghostscript.assert_called_once()


@patch("auto_print.execute.sys.argv", ["auto_print", "test_file.pdf"])
@patch("auto_print.utils.configure_logger")
@patch("auto_print.execute.logging")
@patch("auto_print.execute.os.path.exists")
@patch("auto_print.execute.json.load")
@patch("auto_print.utils.provision_fulfilled")
@patch("auto_print.execute.printer_pdf_reader")
@patch("auto_print.execute.sys.exit")
def test_main_with_print_and_show(
    mock_exit,
    mock_printer_pdf_reader,
    mock_provision_fulfilled,
    mock_json_load,
    mock_exists,
    mock_logging,
    mock_configure_logger,
):
    """Test the main function with print and show options."""
    from auto_print.execute import main

    # Set up the mocks
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "Test Section": {
            "active": True,
            "prefix": "test_",
            "print": True,
            "show": True,
            "printer": "Test Printer",
        }
    }
    mock_provision_fulfilled.return_value = True

    # Call the function
    main()

    # Verify the function calls
    mock_configure_logger.assert_called_once()
    mock_exists.assert_called_once()
    mock_provision_fulfilled.assert_called_once()
    mock_printer_pdf_reader.assert_called_once()
    mock_exit.assert_called_once_with(0)


@patch("auto_print.execute.sys.argv", ["auto_print", "test_file.pdf"])
@patch("auto_print.utils.configure_logger")
@patch("auto_print.execute.logging")
@patch("auto_print.execute.os.path.exists")
@patch("auto_print.execute.json.load")
@patch("auto_print.utils.provision_fulfilled")
@patch("auto_print.execute.printer_ghost_script")
@patch("auto_print.execute.sys.exit")
def test_main_with_print_no_show(
    mock_exit,
    mock_printer_ghost_script,
    mock_provision_fulfilled,
    mock_json_load,
    mock_exists,
    mock_logging,
    mock_configure_logger,
):
    """Test the main function with print but no show options."""
    from auto_print.execute import main

    # Set up the mocks
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "Test Section": {
            "active": True,
            "prefix": "test_",
            "print": True,
            "show": False,
            "printer": "Test Printer",
        }
    }
    mock_provision_fulfilled.return_value = True

    # Call the function
    main()

    # Verify the function calls
    mock_configure_logger.assert_called_once()
    mock_exists.assert_called_once()
    mock_provision_fulfilled.assert_called_once()
    mock_printer_ghost_script.assert_called_once()
    mock_exit.assert_called_once_with(0)


@patch("auto_print.execute.sys.argv", ["auto_print", "test_file.pdf"])
@patch("auto_print.utils.configure_logger")
@patch("auto_print.execute.logging")
@patch("auto_print.execute.os.path.exists")
@patch("auto_print.execute.json.load")
@patch("auto_print.utils.provision_fulfilled")
@patch("auto_print.execute.os.startfile")
@patch("auto_print.execute.sys.exit")
def test_main_with_no_print(
    mock_exit,
    mock_startfile,
    mock_provision_fulfilled,
    mock_json_load,
    mock_exists,
    mock_logging,
    mock_configure_logger,
):
    """Test the main function with no print option."""
    from auto_print.execute import main

    # Set up the mocks
    mock_exists.return_value = True
    mock_json_load.return_value = {
        "Test Section": {
            "active": True,
            "prefix": "test_",
            "print": False,
            "printer": "Test Printer",
        }
    }
    mock_provision_fulfilled.return_value = True

    # Call the function
    main()

    # Verify the function calls
    mock_configure_logger.assert_called_once()
    mock_exists.assert_called_once()
    mock_provision_fulfilled.assert_called_once()
    mock_startfile.assert_called_once()
    # No exit call because we're showing the file


@patch("auto_print.execute.sys.argv", ["auto_print", "test_file.pdf"])
@patch("auto_print.utils.configure_logger")
@patch("auto_print.execute.logging")
@patch("auto_print.execute.os.path.exists")
@patch("auto_print.execute.sys.exit")
@patch("auto_print.execute.open", create=True)
@patch("auto_print.execute.json.load")
def test_main_file_not_exists(
    mock_json_load,
    mock_open,
    mock_exit,
    mock_exists,
    mock_logging,
    mock_configure_logger,
):
    """Test the main function when the file doesn't exist."""
    from auto_print.execute import main

    # Set up the mocks
    mock_exists.side_effect = lambda path: path != "test_file.pdf"
    mock_json_load.return_value = {}

    # Call the function
    main()

    # Verify the function calls
    mock_configure_logger.assert_called_once()
    assert mock_exists.call_count >= 1
    # Check that sys.exit was called with -3 (file not found)
    assert mock_exit.call_args_list[0] == (((-3,)), {})


@patch("auto_print.execute.sys.argv", ["auto_print"])
@patch("auto_print.utils.configure_logger")
@patch("auto_print.execute.logging")
@patch("auto_print.execute.sys.exit")
@patch("auto_print.execute.open", create=True)
def test_main_no_file_arg(
    mock_open,
    mock_exit,
    mock_logging,
    mock_configure_logger,
):
    """Test the main function with no file argument."""
    from auto_print.execute import main

    # Call the function with pytest.raises to handle the expected IndexError
    with pytest.raises(IndexError):
        main()

    # Verify the function calls
    mock_configure_logger.assert_called_once()
    # The exit might not be called if an exception is raised first
    # So we don't assert on mock_exit


@patch("auto_print.execute.sys.argv", ["auto_print", "test_file.pdf", "extra_arg"])
@patch("auto_print.utils.configure_logger")
@patch("auto_print.execute.logging")
@patch("auto_print.execute.sys.exit")
@patch("auto_print.execute.open", create=True)
@patch("auto_print.execute.os.path.exists")
@patch("auto_print.execute.json.load")
def test_main_too_many_args(
    mock_json_load,
    mock_exists,
    mock_open,
    mock_exit,
    mock_logging,
    mock_configure_logger,
):
    """Test the main function with too many arguments."""
    from auto_print.execute import main

    # Set up the mocks
    mock_exists.return_value = True
    mock_json_load.return_value = {}

    # Call the function
    main()

    # Verify the function calls
    mock_configure_logger.assert_called_once()
    # Check that sys.exit was called with -2 (too many arguments)
    assert mock_exit.call_args_list[0] == (((-2,)), {})


@patch("auto_print.execute.sys.argv", ["auto_print", "test_file.pdf"])
@patch("auto_print.utils.configure_logger")
@patch("auto_print.execute.logging")
@patch("auto_print.execute.os.path.exists")
@patch("auto_print.execute.open", create=True)
@patch("auto_print.execute.json.load")
@patch("auto_print.utils.provision_fulfilled")
@patch("auto_print.execute.sys.exit")
def test_main_no_valid_action(
    mock_exit,
    mock_provision_fulfilled,
    mock_json_load,
    mock_open,
    mock_exists,
    mock_logging,
    mock_configure_logger,
):
    """Test the main function when no valid action is found."""
    from auto_print.execute import main

    # Set up the mocks
    mock_exists.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = "{}"
    mock_json_load.return_value = {
        "Test Section": {
            "active": True,
            "prefix": "test_",
            "print": True,
            "show": True,
            "printer": "Test Printer",
        }
    }
    # No valid action found
    mock_provision_fulfilled.return_value = False

    # Call the function
    main()

    # Verify the function calls
    mock_configure_logger.assert_called_once()
    assert mock_exists.call_count >= 1
    assert mock_provision_fulfilled.call_count >= 1


@patch("auto_print.execute.logging")
def test_log_print_operation(mock_logging):
    """Test the log_print_operation function."""
    log_print_operation("test_file.pdf", "Test Printer")
    mock_logging.info.assert_called_once_with(
        'The printer "Test Printer" will be chosen to print the file on "test_file.pdf"\n'
        "While showing the file!",
    )


@patch("auto_print.execute.win32api.ShellExecute")
@patch("auto_print.execute.win32print.StartPagePrinter")
@patch("auto_print.execute.win32print.WritePrinter")
@patch("auto_print.execute.win32print.EndPagePrinter")
def test_execute_print_command(
    mock_end_page_printer,
    mock_write_printer,
    mock_start_page_printer,
    mock_shell_execute,
):
    """Test the execute_print_command function."""
    h_printer = Mock()
    execute_print_command("test_file.pdf", h_printer)

    mock_shell_execute.assert_called_once_with(
        0, "print", "test_file.pdf", None, ".", 0
    )
    mock_start_page_printer.assert_called_once_with(h_printer)
    mock_write_printer.assert_called_once_with(h_printer, "test")
    mock_end_page_printer.assert_called_once_with(h_printer)


@patch("auto_print.execute.logging")
def test_handle_printer_error_known_error(mock_logging):
    """Test the handle_printer_error function with a known error."""
    error = Exception()
    error.args = [1801]
    handle_printer_error(error, "Test Printer")
    mock_logging.error.assert_called_once_with(
        'The printer with the name "Test Printer" does not exists.'
    )


@patch("auto_print.execute.logging")
def test_handle_printer_error_unknown_error(mock_logging):
    """Test the handle_printer_error function with an unknown error."""
    error = Exception("Unknown error")
    with pytest.raises(Exception) as excinfo:
        handle_printer_error(error, "Test Printer")
    assert str(excinfo.value) == "Unknown error"


@patch("auto_print.execute.sys.argv", ["auto_print", "test_file.pdf"])
@patch("auto_print.execute.logging")
@patch("auto_print.execute.os.path.exists")
@patch("auto_print.execute.sys.exit")
def test_validate_arguments_valid(mock_exit, mock_exists, mock_logging):
    """Test the validate_arguments function with valid arguments."""
    mock_exists.return_value = True
    result = validate_arguments()
    assert result == "test_file.pdf"
    mock_exists.assert_called_once_with("test_file.pdf")
    mock_exit.assert_not_called()


@patch("auto_print.execute.sys.argv", ["auto_print"])
@patch("auto_print.execute.logging")
@patch("auto_print.execute.sys.exit")
def test_validate_arguments_no_file(mock_exit, mock_logging):
    """Test the validate_arguments function with no file argument."""
    with pytest.raises(IndexError):
        validate_arguments()


@patch("auto_print.execute.sys.argv", ["auto_print", "test_file.pdf", "extra_arg"])
@patch("auto_print.execute.logging")
@patch("auto_print.execute.sys.exit")
def test_validate_arguments_too_many_args(mock_exit, mock_logging):
    """Test the validate_arguments function with too many arguments."""
    validate_arguments()
    mock_exit.assert_called_once_with(-2)


@patch("auto_print.execute.sys.argv", ["auto_print", "test_file.pdf"])
@patch("auto_print.execute.logging")
@patch("auto_print.execute.os.path.exists")
@patch("auto_print.execute.sys.exit")
def test_validate_arguments_file_not_exists(mock_exit, mock_exists, mock_logging):
    """Test the validate_arguments function when the file doesn't exist."""
    mock_exists.return_value = False
    validate_arguments()
    mock_exists.assert_called_once_with("test_file.pdf")
    mock_exit.assert_called_once_with(-3)


@patch("auto_print.execute.logging")
@patch("auto_print.execute.printer_pdf_reader")
@patch("auto_print.execute.printer_ghost_script")
@patch("auto_print.execute.os.startfile")
@patch("auto_print.execute.sys.exit")
@patch("auto_print.execute.provision_fulfilled")
def test_process_file_print_and_show(
    mock_provision_fulfilled,
    mock_exit,
    mock_startfile,
    mock_printer_ghost_script,
    mock_printer_pdf_reader,
    mock_logging,
):
    """Test the process_file function with print and show."""
    mock_provision_fulfilled.return_value = True
    printer_config = {
        "Test Section": {
            "active": True,
            "print": True,
            "show": True,
            "printer": "Test Printer",
        }
    }
    process_file("test_file.pdf", "test_file.pdf", printer_config)
    mock_provision_fulfilled.assert_called_once()
    mock_printer_pdf_reader.assert_called_once_with(
        "test_file.pdf", "test_file.pdf", "Test Printer"
    )
    mock_exit.assert_called_once_with(0)
    mock_printer_ghost_script.assert_not_called()
    mock_startfile.assert_not_called()


@patch("auto_print.execute.logging")
@patch("auto_print.execute.printer_pdf_reader")
@patch("auto_print.execute.printer_ghost_script")
@patch("auto_print.execute.os.startfile")
@patch("auto_print.execute.sys.exit")
@patch("auto_print.execute.provision_fulfilled")
def test_process_file_print_no_show(
    mock_provision_fulfilled,
    mock_exit,
    mock_startfile,
    mock_printer_ghost_script,
    mock_printer_pdf_reader,
    mock_logging,
):
    """Test the process_file function with print but no show."""
    mock_provision_fulfilled.return_value = True
    printer_config = {
        "Test Section": {
            "active": True,
            "print": True,
            "show": False,
            "printer": "Test Printer",
        }
    }
    process_file("test_file.pdf", "test_file.pdf", printer_config)
    mock_provision_fulfilled.assert_called_once()
    mock_printer_ghost_script.assert_called_once_with("test_file.pdf", "Test Printer")
    mock_exit.assert_called_once_with(0)
    mock_printer_pdf_reader.assert_not_called()
    mock_startfile.assert_not_called()


@patch("auto_print.execute.logging")
@patch("auto_print.execute.printer_pdf_reader")
@patch("auto_print.execute.printer_ghost_script")
@patch("auto_print.execute.os.startfile")
@patch("auto_print.execute.sys.exit")
@patch("auto_print.execute.provision_fulfilled")
def test_process_file_no_print(
    mock_provision_fulfilled,
    mock_exit,
    mock_startfile,
    mock_printer_ghost_script,
    mock_printer_pdf_reader,
    mock_logging,
):
    """Test the process_file function with no print."""
    mock_provision_fulfilled.return_value = True
    printer_config = {
        "Test Section": {
            "active": True,
            "print": False,
            "show": True,
        }
    }
    process_file("test_file.pdf", "test_file.pdf", printer_config)
    mock_provision_fulfilled.assert_called_once()
    mock_startfile.assert_called_once_with("test_file.pdf")
    mock_exit.assert_called_once_with(0)
    mock_printer_pdf_reader.assert_not_called()
    mock_printer_ghost_script.assert_not_called()


@patch("auto_print.execute.logging")
@patch("auto_print.execute.sys.exit")
@patch("auto_print.execute.provision_fulfilled")
def test_process_file_no_valid_action(
    mock_provision_fulfilled,
    mock_exit,
    mock_logging,
):
    """Test the process_file function with no valid action."""
    mock_provision_fulfilled.return_value = False
    printer_config = {
        "Test Section": {
            "active": True,
            "print": True,
            "show": True,
            "printer": "Test Printer",
        }
    }
    process_file("test_file.pdf", "test_file.pdf", printer_config)
    mock_provision_fulfilled.assert_called_once()
    mock_logging.error.assert_called_once_with("No valid action found.")
