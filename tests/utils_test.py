"""
Tests for the utils module.
"""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from auto_print.utils import (
    AUTO_PRINTER_FOLDER,
    PRINTER_CONFIG_PATH,
    LOG_FILE,
    configure_logger,
    get_default_printer,
    get_printer_list,
    check_ghostscript,
    load_config_file,
    save_config_file,
    provision_fulfilled,
)


@patch("logging.basicConfig")
def test_configure_logger(mock_basicConfig):
    """Test the configure_logger function."""
    configure_logger()
    mock_basicConfig.assert_called_once_with(
        filename=LOG_FILE,
        format="%(asctime)-15s %(message)s",
        level=10,  # logging.DEBUG
        filemode="a",
    )


@patch("win32print.GetDefaultPrinter")
def test_get_default_printer(mock_get_default_printer):
    """Test the get_default_printer function."""
    mock_get_default_printer.return_value = "Test Printer"
    result = get_default_printer()
    assert result == "Test Printer"
    mock_get_default_printer.assert_called_once()


@patch("win32print.GetDefaultPrinter")
def test_get_default_printer_error(mock_get_default_printer):
    """Test the get_default_printer function when an error occurs."""
    mock_get_default_printer.side_effect = RuntimeError("Test error")
    result = get_default_printer()
    assert result == "No default printer"
    mock_get_default_printer.assert_called_once()


@patch("win32print.EnumPrinters")
def test_get_printer_list(mock_enum_printers):
    """Test the get_printer_list function."""
    mock_enum_printers.return_value = [
        (0, "Printer1,Driver1", "Port1"),
        (0, "Printer2,Driver2", "Port2"),
    ]
    result = get_printer_list()
    assert result == ["Printer1", "Printer2"]
    mock_enum_printers.assert_called_once_with(2)


@patch("auto_print.utils.install_ghostscript")
def test_check_ghostscript_error(mock_install_ghostscript):
    """Test the check_ghostscript function when ghostscript is not installed."""
    with patch("builtins.__import__", side_effect=RuntimeError("Test error")):
        check_ghostscript()
        mock_install_ghostscript.assert_called_once()


@patch("os.path.exists")
@patch("builtins.open")
def test_load_config_file_exists(mock_open, mock_exists):
    """Test the load_config_file function when the config file exists."""
    mock_exists.return_value = True
    mock_file = Mock()
    mock_open.return_value.__enter__.return_value = mock_file

    with patch("json.load", return_value={"test": "value"}) as mock_json_load:
        result = load_config_file()

    assert result == {"test": "value"}
    mock_exists.assert_called_once_with(PRINTER_CONFIG_PATH)
    mock_open.assert_called_once_with(PRINTER_CONFIG_PATH, encoding="utf-8")
    mock_json_load.assert_called_once()


@patch("os.path.exists")
def test_load_config_file_not_exists(mock_exists):
    """Test the load_config_file function when the config file does not exist."""
    mock_exists.return_value = False
    result = load_config_file()
    assert result == {}
    mock_exists.assert_called_once_with(PRINTER_CONFIG_PATH)


@patch("builtins.open")
def test_save_config_file(mock_open):
    """Test the save_config_file function."""
    mock_file = Mock()
    mock_open.return_value.__enter__.return_value = mock_file

    with patch("json.dump") as mock_json_dump:
        save_config_file({"test": "value"})

    mock_open.assert_called_once_with(PRINTER_CONFIG_PATH, "w", encoding="utf-8")
    mock_json_dump.assert_called_once_with({"test": "value"}, mock_file, indent=2)


def test_provision_fulfilled():
    """Test the provision_fulfilled function."""
    # Test with no prefix or suffix
    assert provision_fulfilled("test.pdf", None, None) is True

    # Test with matching prefix
    assert provision_fulfilled("test.pdf", "test", None) is True

    # Test with non-matching prefix
    assert provision_fulfilled("test.pdf", "other", None) is False

    # Test with matching suffix
    assert provision_fulfilled("test.pdf", None, ".pdf") is True

    # Test with non-matching suffix
    assert provision_fulfilled("test.pdf", None, ".txt") is False

    # Test with matching prefix and suffix
    assert provision_fulfilled("test.pdf", "test", ".pdf") is True

    # Test with matching prefix and non-matching suffix
    assert provision_fulfilled("test.pdf", "test", ".txt") is False

    # Test with non-matching prefix and matching suffix
    assert provision_fulfilled("test.pdf", "other", ".pdf") is False
