"""
Tests for the auto_print_execute module.
"""

from unittest.mock import patch

from auto_print.auto_print_execute import (
    LOG_FILE,
    configure_logger,
    get_default_printer,
    get_printer_list,
    provision_fulfilled,
)


class TestProvisionFulfilled:
    """Tests for the provision_fulfilled function."""

    def test_no_prefix_no_suffix(self):
        """Test with no prefix and no suffix."""
        assert provision_fulfilled("test_file.pdf", None, None) is True

    def test_matching_prefix_no_suffix(self):
        """Test with matching prefix and no suffix."""
        assert provision_fulfilled("test_file.pdf", "test_", None) is True

    def test_non_matching_prefix_no_suffix(self):
        """Test with non-matching prefix and no suffix."""
        assert provision_fulfilled("file.pdf", "test_", None) is False

    def test_no_prefix_matching_suffix(self):
        """Test with no prefix and matching suffix."""
        assert provision_fulfilled("file.pdf", None, ".pdf") is True

    def test_no_prefix_non_matching_suffix(self):
        """Test with no prefix and non-matching suffix."""
        assert provision_fulfilled("file.txt", None, ".pdf") is False

    def test_matching_prefix_matching_suffix(self):
        """Test with matching prefix and matching suffix."""
        assert provision_fulfilled("test_file.pdf", "test_", ".pdf") is True

    def test_non_matching_prefix_matching_suffix(self):
        """Test with non-matching prefix and matching suffix."""
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
