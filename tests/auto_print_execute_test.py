"""
Tests for the auto_print_execute module using pytest conventions.
"""

from unittest.mock import Mock

import pytest

from auto_print.auto_print_execute import (
    LOG_FILE,
    configure_logger,
    get_default_printer,
    get_printer_list,
    provision_fulfilled,
)


class TestProvisionFulfilled:
    """Tests for the provision_fulfilled function."""

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
    def test_provision_fulfilled(self, filename, prefix, suffix, expected_result):
        """Test provision_fulfilled with various combinations of parameters."""
        assert provision_fulfilled(filename, prefix, suffix) is expected_result


class TestLogger:
    """Tests for the logger configuration."""

    def test_configure_logger(self, monkeypatch):
        """Test the configure_logger function."""
        # Create a mock for logging.basicConfig
        mock_basic_config = Mock()
        mock_logging = Mock()
        mock_logging.DEBUG = "DEBUG"
        mock_logging.basicConfig = mock_basic_config

        # Patch the logging module
        monkeypatch.setattr("auto_print.auto_print_execute.logging", mock_logging)

        # Call the function
        configure_logger()

        # Verify the logging was configured correctly
        mock_basic_config.assert_called_once_with(
            filename=LOG_FILE,
            format="%(asctime)-15s %(message)s",
            level="DEBUG",
            filemode="a",
        )


class TestPrinters:
    """Tests for printer-related functions."""

    def test_get_default_printer(self, monkeypatch):
        """Test the get_default_printer function."""
        # Create a mock for win32print.GetDefaultPrinter
        mock_get_default_printer = Mock(return_value="Test Printer")
        mock_win32print = Mock()
        mock_win32print.GetDefaultPrinter = mock_get_default_printer

        # Patch the win32print module
        monkeypatch.setattr("auto_print.auto_print_execute.win32print", mock_win32print)

        # Call the function
        result = get_default_printer()

        # Verify the result
        assert result == "Test Printer"
        mock_get_default_printer.assert_called_once()

    def test_get_printer_list(self, monkeypatch):
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
        monkeypatch.setattr("auto_print.auto_print_execute.win32print", mock_win32print)

        # Call the function
        result = get_printer_list()

        # Verify the result
        assert result == ["Printer1", "Printer2"]
        mock_enum_printers.assert_called_once_with(2)
