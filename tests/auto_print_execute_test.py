"""Tests for the auto_print_execute module."""

import contextlib
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from auto_print.auto_print_execute import (
    LOG_FILE,
    configure_logger,
    get_default_printer,
    get_printer_list,
    load_printer_config,
    main,
    provision_fulfilled,
)


class TestProvisionFulfilled:
    """Tests for the provision_fulfilled function."""

    def test_no_prefix_no_suffix(self):
        """Test with no prefix and no suffix."""
        assert provision_fulfilled("test_file.pdf", None, None) is True

    def test_matching_prefix_no_suffix(self):
        """Test with a matching prefix and no suffix."""
        assert provision_fulfilled("test_file.pdf", "test_", None) is True

    def test_non_matching_prefix_no_suffix(self):
        """Test with a non-matching prefix and no suffix."""
        assert provision_fulfilled("file.pdf", "test_", None) is False

    def test_no_prefix_matching_suffix(self):
        """Test with no prefix and matching suffix."""
        assert provision_fulfilled("file.pdf", None, ".pdf") is True

    def test_no_prefix_non_matching_suffix(self):
        """Test with no prefix and non-matching suffix."""
        assert provision_fulfilled("file.txt", None, ".pdf") is False

    def test_matching_prefix_matching_suffix(self):
        """Test with a matching prefix and matching suffix."""
        assert provision_fulfilled("test_file.pdf", "test_", ".pdf") is True

    def test_non_matching_prefix_matching_suffix(self):
        """Test with a non-matching prefix and matching suffix."""
        assert provision_fulfilled("file.pdf", "test_", ".pdf") is False

    def test_matching_prefix_non_matching_suffix(self):
        """Test with matching prefix and non-matching suffix."""
        assert provision_fulfilled("test_file.txt", "test_", ".pdf") is False


@patch("auto_print.auto_print_execute.logging")
def test_configure_logger(mock_logging):
    """Test the configure_logger function."""
    configure_logger()
    mock_logging.basicConfig.assert_called_once_with(
        filename=LOG_FILE,
        format="%(asctime)-15s %(message)s",
        level=mock_logging.DEBUG,
        filemode="a",
    )


@patch("auto_print.auto_print_execute.win32print")
def test_get_default_printer(mock_win32print):
    """Test the get_default_printer function."""
    mock_win32print.GetDefaultPrinter.return_value = "Test Printer"
    result = get_default_printer()
    assert result == "Test Printer"
    mock_win32print.GetDefaultPrinter.assert_called_once()


@patch("auto_print.auto_print_execute.win32print")
def test_get_printer_list(mock_win32print):
    """Test the get_printer_list function."""
    mock_win32print.EnumPrinters.return_value = [
        (0, "Printer1,Port1"),
        (0, "Printer2,Port2"),
    ]
    result = get_printer_list()
    assert result == ["Printer1", "Printer2"]
    mock_win32print.EnumPrinters.assert_called_once_with(2)


def test_read_empty_file(temp_empty_config_file: Path) -> None:
    """Test loading an empty configuration file.

    This test verifies that attempting to load an empty configuration file
    results in a SystemExit with the appropriate exit code.

    Args:
        temp_empty_config_file: Fixture that provides an empty config file
    """
    with pytest.raises(SystemExit) as pytest_wrapped_error:
        load_printer_config(temp_empty_config_file)
    assert pytest_wrapped_error.value.code == -4


def test_read_broken_file(temp_broken_config_file: Path) -> None:
    """Test loading a broken configuration file.

    This test verifies that attempting to load a malformed JSON configuration file
    results in a SystemExit with the appropriate exit code.

    Args:
        temp_broken_config_file: Fixture that provides a broken config file
    """
    with pytest.raises(SystemExit) as pytest_wrapped_error:
        load_printer_config(temp_broken_config_file)
    assert pytest_wrapped_error.value.code == -4


def test_non_existing_file(tmp_path: Path) -> None:
    """Test loading a non-existing configuration file.

    This test verifies that attempting to load a configuration file that doesn't exist
    results in a SystemExit with the appropriate exit code.

    Args:
        tmp_path: Pytest fixture that provides a temporary directory
    """
    non_existing_file = tmp_path / "non_existing_file.json"
    with pytest.raises(SystemExit) as pytest_wrapped_error:
        load_printer_config(non_existing_file)
    assert pytest_wrapped_error.value.code == -4


class TestMainFunction:
    """Tests for the main function."""

    @pytest.fixture
    def mock_sys_argv(self, monkeypatch, tmp_path):
        """Mock sys.argv with a test file path."""
        test_file = tmp_path / "invoice_test.pdf"
        test_file.write_text("Test content")
        monkeypatch.setattr(sys, "argv", ["auto_print", str(test_file)])
        return test_file

    @pytest.fixture
    def mock_config(self, monkeypatch, basic_config_file):
        """Mock the printer configuration path."""
        monkeypatch.setattr(
            "auto_print.auto_print_execute.PRINTER_CONFIG_PATH", basic_config_file
        )
        return basic_config_file

    def test_show_only_workflow(
        self, mocker, mock_sys_argv, mock_config, mock_os_startfile
    ):
        """Test the workflow where a file is only shown (not printed)."""
        # Mock the necessary functions
        mock_pdf_reader = mocker.patch(
            "auto_print.auto_print_execute.printer_pdf_reader"
        )
        mock_ghost_script = mocker.patch(
            "auto_print.auto_print_execute.printer_ghost_script"
        )
        mock_logging = mocker.patch("auto_print.auto_print_execute.logging")

        # Import the module and spy on the provision_fulfilled function
        from auto_print import auto_print_execute

        mock_provision = mocker.spy(auto_print_execute, "provision_fulfilled")

        # Modify the config to match our test case
        with Path(mock_config).open("r+", encoding="utf-8") as f:
            config = f.read()
            f.seek(0)
            f.write(config.replace('"print": true', '"print": false'))
            f.truncate()

        # Print the configuration for debugging
        with Path(mock_config).open(encoding="utf-8") as f:
            print(f"Config content: {f.read()}")
        print(f"Test file name: {mock_sys_argv.name}")

        # Run the main function
        # We don't expect SystemExit to be raised in this case
        with contextlib.suppress(SystemExit):
            main()

        # Print debug info
        print(f"Mock startfile called: {mock_os_startfile.call_count}")
        print(f"Mock provision called: {mock_provision.call_count}")
        print(f"Mock logging calls: {mock_logging.method_calls}")

        # Verify the correct function was called
        mock_os_startfile.assert_called_once_with(str(mock_sys_argv))
        mock_pdf_reader.assert_not_called()
        mock_ghost_script.assert_not_called()

    def test_print_with_show_workflow(
        self, mocker, mock_sys_argv, mock_config, mock_os_startfile
    ):
        """Test the workflow where a file is printed and shown."""
        # Mock the necessary functions
        mock_pdf_reader = mocker.patch(
            "auto_print.auto_print_execute.printer_pdf_reader"
        )
        mock_ghost_script = mocker.patch(
            "auto_print.auto_print_execute.printer_ghost_script"
        )
        mock_logging = mocker.patch("auto_print.auto_print_execute.logging")

        # Import the module and spy on the provision_fulfilled function
        from auto_print import auto_print_execute

        mock_provision = mocker.spy(auto_print_execute, "provision_fulfilled")

        # Modify the config to match our test case
        with Path(mock_config).open("r+", encoding="utf-8") as f:
            config = f.read()
            f.seek(0)
            f.write(config.replace('"show": false', '"show": true'))
            f.truncate()

        # Print the configuration for debugging
        with Path(mock_config).open(encoding="utf-8") as f:
            print(f"Config content: {f.read()}")
        print(f"Test file name: {mock_sys_argv.name}")

        # Run the main function
        # The function might raise SystemExit with code 0 if successful
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main()
        assert pytest_wrapped_e.value.code == 0

        # Print debug info
        print(f"Mock pdf reader called: {mock_pdf_reader.call_count}")
        print(f"Mock provision called: {mock_provision.call_count}")
        print(f"Mock logging calls: {mock_logging.method_calls}")

        # Verify the correct function was called
        mock_pdf_reader.assert_called_once()
        mock_ghost_script.assert_not_called()
        mock_os_startfile.assert_not_called()

    def test_print_without_show_workflow(
        self, mocker, mock_sys_argv, mock_config, mock_os_startfile
    ):
        """Test the workflow where a file is printed without being shown."""
        # Mock the necessary functions
        mock_pdf_reader = mocker.patch(
            "auto_print.auto_print_execute.printer_pdf_reader"
        )
        mock_ghost_script = mocker.patch(
            "auto_print.auto_print_execute.printer_ghost_script"
        )
        mock_logging = mocker.patch("auto_print.auto_print_execute.logging")

        # Import the module and spy on the provision_fulfilled function
        from auto_print import auto_print_execute

        mock_provision = mocker.spy(auto_print_execute, "provision_fulfilled")

        # The basic_config_file already has print=true and show=false
        # Print the configuration for debugging
        with Path(mock_config).open(encoding="utf-8") as f:
            print(f"Config content: {f.read()}")
        print(f"Test file name: {mock_sys_argv.name}")

        # Run the main function
        # The function might raise SystemExit with code 0 if successful
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main()
        assert pytest_wrapped_e.value.code == 0

        # Print debug info
        print(f"Mock ghost script called: {mock_ghost_script.call_count}")
        print(f"Mock provision called: {mock_provision.call_count}")
        print(f"Mock logging calls: {mock_logging.method_calls}")

        # Verify the correct function was called
        mock_ghost_script.assert_called_once()
        mock_pdf_reader.assert_not_called()
        mock_os_startfile.assert_not_called()
