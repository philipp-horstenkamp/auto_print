"""Tests for the auto_print_config_generator module."""

from unittest.mock import mock_open, patch

import pytest
from case_insensitive_dict import CaseInsensitiveDict

from auto_print.auto_print_config_generator import (
    bool_decision,
    input_choice,
    load_config,
    print_configuration,
    repair_config,
    save_config,
)


@pytest.fixture
def mock_config_object():
    """Returns a mock configuration object for testing."""
    return CaseInsensitiveDict(
        {
            "Test Section": {
                "printer": "Microsoft Print to PDF",
                "prefix": "test_",
                "suffix": "_document",
                "software": "",
                "delete": False,
                "active": True,
            }
        }
    )


@patch("auto_print.auto_print_config_generator.PRINTER_CONFIG_PATH")
@patch("json.load")
def test_load_config(mock_json_load, mock_config_path):
    """Test the load_config function."""
    mock_json_load.return_value = {"Test Section": {"printer": "Test Printer"}}
    mock_file = mock_open(read_data='{"Test Section": {"printer": "Test Printer"}}')
    mock_config_path.open.return_value = mock_file()

    result = load_config()

    mock_config_path.open.assert_called_once_with(encoding="utf-8")
    mock_json_load.assert_called_once()
    assert isinstance(result, CaseInsensitiveDict)
    assert "Test Section" in result
    assert result["Test Section"]["printer"] == "Test Printer"


@patch("auto_print.auto_print_config_generator.PRINTER_CONFIG_PATH")
@patch("json.dump")
def test_save_config(mock_json_dump, mock_config_path, mock_config_object):
    """Test the save_config function."""
    mock_file = mock_open()
    mock_config_path.open.return_value = mock_file()

    save_config(mock_config_object)

    mock_config_path.open.assert_called_once_with("w", encoding="utf-8")
    mock_json_dump.assert_called_once()
    # Check that the first argument to json.dump is our config object's __dict__
    assert mock_json_dump.call_args[0][0] == mock_config_object.__dict__


@patch("builtins.print")
def test_print_configuration(mock_print, mock_config_object):
    """Test the print_configuration function."""
    print_configuration(mock_config_object)

    # Check that print was called at least once
    assert mock_print.call_count > 0


@patch("builtins.input", return_value="y")
def test_bool_decision_yes(mock_input):
    """Test the bool_decision function with 'y' input."""
    result = bool_decision("Test decision?", default=False)
    assert result is True
    mock_input.assert_called_once()


@patch("builtins.input", return_value="n")
def test_bool_decision_no(mock_input):
    """Test the bool_decision function with 'n' input."""
    result = bool_decision("Test decision?", default=True)
    assert result is False
    mock_input.assert_called_once()


@patch("builtins.input", return_value="")
def test_bool_decision_default(mock_input):
    """Test the bool_decision function with the default input."""
    result = bool_decision("Test decision?", default=True)
    assert result is True
    mock_input.assert_called_once()


@patch("builtins.input", return_value="option1")
def test_input_choice(mock_input):
    """Test the input_choice function."""
    result = input_choice("Choose an option:", ["option1", "option2"], "option2")
    assert result == "option1"
    mock_input.assert_called_once()


@patch("builtins.input", return_value="")
def test_input_choice_default(mock_input):
    """Test the input_choice function with default input."""
    result = input_choice("Choose an option:", ["option1", "option2"], "option2")
    assert result == "option2"
    mock_input.assert_called_once()


@patch("builtins.input", return_value="PDF24")
@patch(
    "auto_print.auto_print_config_generator.get_default_printer", return_value="PDF24"
)
@patch(
    "auto_print.auto_print_config_generator.get_printer_list", return_value=["PDF24"]
)
def test_repair_config(
    mock_get_printer_list, mock_get_default_printer, mock_input, mock_config_object
):
    """Test the repair_config function."""
    # Create a config with a printer that's not in the printer list
    config_with_invalid_printer = CaseInsensitiveDict(
        {
            "Test Section": {
                "printer": "Non-existent Printer",
                "active": True,
            }
        }
    )

    result = repair_config(config_with_invalid_printer)

    # Check that the printer was updated to the one selected via input
    assert result["Test Section"]["printer"] == "PDF24"

    # Reset mocks for the second part of the test
    mock_input.reset_mock()
    mock_get_printer_list.reset_mock()

    # Test with a valid printer
    config_with_valid_printer = CaseInsensitiveDict(
        {
            "Test Section": {
                "printer": "PDF24",
                "active": True,
            }
        }
    )

    result = repair_config(config_with_valid_printer)

    # Check that the printer wasn't changed
    assert result["Test Section"]["printer"] == "PDF24"
    # Input shouldn't have been called since no repair was needed
    mock_input.assert_not_called()
