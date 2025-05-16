"""
Tests for the auto_print_config_generator module using pytest conventions.
"""

import json
from unittest.mock import Mock

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


def test_load_config(monkeypatch, tmp_path):
    """Test the load_config function."""
    # Create a temporary config file
    config_path = tmp_path / "test_config.json"
    config_data = {"Test Section": {"printer": "Test Printer"}}
    config_path.write_text(json.dumps(config_data))

    # Patch the config path
    monkeypatch.setattr(
        "auto_print.auto_print_config_generator.PRINTER_CONFIG_PATH",
        str(config_path),
    )

    # Call the function
    result = load_config()

    # Verify the result
    assert isinstance(result, CaseInsensitiveDict)
    assert "Test Section" in result
    assert result["Test Section"]["printer"] == "Test Printer"


def test_save_config(monkeypatch, tmp_path, mock_config_object):
    """Test the save_config function."""
    # Create a temporary config file path
    config_path = tmp_path / "test_config.json"

    # Patch the config path
    monkeypatch.setattr(
        "auto_print.auto_print_config_generator.PRINTER_CONFIG_PATH",
        str(config_path),
    )

    # Call the function
    save_config(mock_config_object)

    # Verify the file was created
    assert config_path.exists()

    # Load the saved data
    saved_data = json.loads(config_path.read_text())

    # The CaseInsensitiveDict.__dict__ structure has a _data attribute
    assert "_data" in saved_data

    # The keys in _data are lowercase
    assert "test section" in saved_data["_data"]

    # Each entry in _data is a list with [original_key, value]
    assert saved_data["_data"]["test section"][0] == "Test Section"
    assert saved_data["_data"]["test section"][1]["printer"] == "Microsoft Print to PDF"


def test_print_configuration(capsys, mock_config_object):
    """Test the print_configuration function."""
    # Call the function
    print_configuration(mock_config_object)

    # Capture the output
    captured = capsys.readouterr()

    # Verify something was printed
    assert captured.out
    assert "Test Section" in captured.out


@pytest.mark.parametrize(
    "input_value, default_value, expected_result",
    [
        ("y", False, True),
        ("n", True, False),
        ("", True, True),
        ("", False, False),
    ],
)
def test_bool_decision(monkeypatch, input_value, default_value, expected_result):
    """Test the bool_decision function with various inputs."""
    # Mock the input function
    monkeypatch.setattr("builtins.input", lambda _: input_value)

    # Call the function
    result = bool_decision("Test decision?", default_value)

    # Verify the result
    assert result is expected_result


@pytest.mark.parametrize(
    "input_value, options, default_value, expected_result",
    [
        ("option1", ["option1", "option2"], "option2", "option1"),
        ("", ["option1", "option2"], "option2", "option2"),
    ],
)
def test_input_choice(
    monkeypatch, input_value, options, default_value, expected_result
):
    """Test the input_choice function with various inputs."""
    # Mock the input function
    monkeypatch.setattr("builtins.input", lambda _: input_value)

    # Call the function
    result = input_choice("Choose an option:", options, default_value)

    # Verify the result
    assert result == expected_result


def test_repair_config_with_invalid_printer(monkeypatch, mock_config_object):
    """Test the repair_config function with an invalid printer."""
    # Create a config with a printer that's not in the printer list
    config_with_invalid_printer = CaseInsensitiveDict(
        {
            "Test Section": {
                "printer": "Non-existent Printer",
                "active": True,
            }
        }
    )

    # Mock the necessary functions
    monkeypatch.setattr(
        "auto_print.auto_print_config_generator.get_printer_list", lambda: ["PDF24"]
    )
    monkeypatch.setattr(
        "auto_print.auto_print_config_generator.get_default_printer",
        lambda: "PDF24",
    )
    monkeypatch.setattr("builtins.input", lambda _: "PDF24")

    # Call the function
    result = repair_config(config_with_invalid_printer)

    # Verify the result
    assert result["Test Section"]["printer"] == "PDF24"


def test_repair_config_with_valid_printer(monkeypatch, mock_config_object):
    """Test the repair_config function with a valid printer."""
    # Create a config with a valid printer
    config_with_valid_printer = CaseInsensitiveDict(
        {
            "Test Section": {
                "printer": "PDF24",
                "active": True,
            }
        }
    )

    # Mock the necessary functions
    monkeypatch.setattr(
        "auto_print.auto_print_config_generator.get_printer_list", lambda: ["PDF24"]
    )

    # Create a mock for input to verify it's not called
    input_mock = Mock(return_value="")
    monkeypatch.setattr("builtins.input", input_mock)

    # Call the function
    result = repair_config(config_with_valid_printer)

    # Verify the result
    assert result["Test Section"]["printer"] == "PDF24"
    assert input_mock.call_count == 0
