"""Tests for the auto_print_config_generator module using pytest conventions.
"""

import json
from unittest.mock import Mock, patch

import pytest
from case_insensitive_dict import CaseInsensitiveDict

from auto_print.config_generator import (
    bool_decision,
    configure_activation,
    configure_display_settings,
    configure_prefix,
    configure_print_settings,
    configure_suffix,
    display_insert_positions,
    edit_section,
    edit_section_command,
    generate_list_of_available_commands,
    get_insert_position,
    get_parser,
    handle_action,
    input_choice,
    load_config,
    print_configuration,
    print_element,
    repair_config,
    save_config,
    show_help,
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
        "auto_print.utils.PRINTER_CONFIG_PATH",
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
        "auto_print.utils.PRINTER_CONFIG_PATH",
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
        "auto_print.config_generator.get_printer_list", lambda: ["PDF24"]
    )
    monkeypatch.setattr(
        "auto_print.config_generator.get_default_printer",
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
        "auto_print.config_generator.get_printer_list", lambda: ["PDF24"]
    )

    # Create a mock for input to verify it's not called
    input_mock = Mock(return_value="")
    monkeypatch.setattr("builtins.input", input_mock)

    # Call the function
    result = repair_config(config_with_valid_printer)

    # Verify the result
    assert result["Test Section"]["printer"] == "PDF24"
    assert input_mock.call_count == 0


def test_get_parser():
    """Test the get_parser function."""
    parser = get_parser()
    assert parser.description is not None
    assert "auto-print" in parser.description.lower()


def test_print_element(capsys, mock_config_object):
    """Test the print_element function."""
    # Call the function with index
    print_element("Test Section", mock_config_object["Test Section"], 0)

    # Capture the output
    captured = capsys.readouterr()

    # Verify the output
    assert "1. Prio config" in captured.out
    assert "Test Section" in captured.out

    # Call the function without index
    print_element("Test Section", mock_config_object["Test Section"], None)

    # Capture the output
    captured = capsys.readouterr()

    # Verify the output
    assert "Config section" in captured.out
    assert "Test Section" in captured.out


def test_generate_list_of_available_commands_empty_config():
    """Test generate_list_of_available_commands with an empty config."""
    empty_config = CaseInsensitiveDict({})
    commands = generate_list_of_available_commands(empty_config)

    # Basic commands should always be available
    assert "save" in commands
    assert "s" in commands
    assert "close" in commands
    assert "c" in commands
    assert "add" in commands
    assert "a" in commands
    assert "show" in commands
    assert "help" in commands
    assert "h" in commands

    # These commands should not be available for empty config
    assert "repair" not in commands
    assert "r" not in commands
    assert "delete" not in commands
    assert "d" not in commands
    assert "change" not in commands
    assert "edit" not in commands
    assert "e" not in commands


def test_generate_list_of_available_commands_with_config(mock_config_object):
    """Test generate_list_of_available_commands with a config."""
    commands = generate_list_of_available_commands(mock_config_object)

    # All commands should be available
    assert "save" in commands
    assert "s" in commands
    assert "close" in commands
    assert "c" in commands
    assert "add" in commands
    assert "a" in commands
    assert "show" in commands
    assert "help" in commands
    assert "h" in commands
    assert "repair" in commands
    assert "r" in commands
    assert "delete" in commands
    assert "d" in commands
    assert "edit" in commands
    assert "e" in commands

    # "change" should not be available for a config with only one section
    assert "change" not in commands

    # Add another section to the config
    config_with_two_sections = CaseInsensitiveDict(
        {
            "Test Section": mock_config_object["Test Section"],
            "Another Section": mock_config_object["Test Section"],
        }
    )

    # Now "change" should be available
    commands = generate_list_of_available_commands(config_with_two_sections)
    assert "change" in commands


@patch("webbrowser.open")
def test_show_help(mock_webbrowser_open, monkeypatch):
    """Test the show_help function."""
    # Mock os.path.realpath to return a fixed path
    monkeypatch.setattr("os.path.realpath", lambda x: "/path/to/README.html")

    # Call the function
    show_help()

    # Verify webbrowser.open was called with the correct URL
    mock_webbrowser_open.assert_called_once_with("file:///path/to/README.html")


@patch("builtins.input")
def test_edit_section(mock_input, monkeypatch, mock_config_object):
    """Test the edit_section function."""
    # Set up the input sequence
    mock_input.side_effect = [
        "new_prefix_",  # prefix
        ".pdf",  # suffix
        "y",  # print
        "Microsoft Print to PDF",  # printer
        "y",  # show
        "y",  # active
        "y",  # is correct
    ]

    # Mock get_printer_list and get_default_printer
    monkeypatch.setattr(
        "auto_print.config_generator.get_printer_list",
        lambda: ["Microsoft Print to PDF"],
    )
    monkeypatch.setattr(
        "auto_print.config_generator.get_default_printer",
        lambda: "Microsoft Print to PDF",
    )

    # Call the function
    name, section = edit_section("Test Section", {})

    # Verify the result
    assert name == "Test Section"
    assert section["prefix"] == "new_prefix_"
    assert section["suffix"] == ".pdf"
    assert section["print"] is True
    assert section["printer"] == "Microsoft Print to PDF"
    assert section["show"] is True
    assert section["active"] is True


def test_edit_section_command():
    """Test the edit_section_command function."""
    # Create a test config
    config = CaseInsensitiveDict({"Test Section": {"original": True}})

    # Mock the dependencies
    with (
        patch("auto_print.config_generator.input_choice", return_value="Test Section"),
        patch(
            "auto_print.config_generator.edit_section",
            return_value=("Test Section", {"updated": True}),
        ),
        patch("auto_print.config_generator.print_element"),
    ):
        # Call the function
        result = edit_section_command(config)

    # Verify the result
    assert "Test Section" in result
    assert result["Test Section"]["updated"] is True


def test_edit_section_command_empty_config():
    """Test the edit_section_command function with an empty config."""
    # Call the function with an empty config
    result = edit_section_command(CaseInsensitiveDict({}))

    # Verify the result is the same empty config
    assert len(result) == 0


@patch("builtins.input")
@patch("auto_print.config_generator.edit_section")
def test_create_section(mock_edit_section, mock_input, mock_config_object):
    """Test the create_section function."""
    from auto_print.config_generator import create_section

    # Set up the mocks
    mock_input.return_value = "New Section"
    mock_edit_section.return_value = ("New Section", {"new": True})

    # Call the function
    name, section = create_section(mock_config_object)

    # Verify the result
    assert name == "New Section"
    assert section["new"] is True
    mock_edit_section.assert_called_once_with("New Section", {})


@patch("builtins.input")
@patch("auto_print.config_generator.print_element")
def test_insert_section(mock_print_element, mock_input, mock_config_object):
    """Test the insert_section function."""
    from auto_print.config_generator import insert_section

    # Set up the mocks
    mock_input.return_value = "0"  # Insert at the beginning

    # Call the function
    result = insert_section(mock_config_object, "New Section", {"new": True})

    # Verify the result
    assert "New Section" in result
    assert result["New Section"]["new"] is True
    assert list(result.keys())[0] == "New Section"  # Should be first


@patch("builtins.input")
@patch("auto_print.config_generator.create_section")
@patch("auto_print.config_generator.insert_section")
def test_add_section(
    mock_insert_section, mock_create_section, mock_input, mock_config_object
):
    """Test the add_section function."""
    from auto_print.config_generator import add_section

    # Set up the mocks
    mock_create_section.return_value = ("New Section", {"new": True})
    mock_insert_section.return_value = CaseInsensitiveDict(
        {"New Section": {"new": True}}
    )

    # Call the function
    result = add_section(mock_config_object)

    # Verify the result
    assert "New Section" in result
    assert result["New Section"]["new"] is True
    mock_create_section.assert_called_once_with(mock_config_object)
    mock_insert_section.assert_called_once_with(
        mock_config_object, "New Section", {"new": True}
    )


@patch("builtins.input")
def test_delete_section(mock_input, mock_config_object):
    """Test the delete_section function."""
    from auto_print.config_generator import delete_section

    # Set up the mocks
    mock_input.return_value = "Test Section"  # Delete the test section

    # Call the function
    result = delete_section(mock_config_object)

    # Verify the result
    assert "Test Section" not in result
    assert len(result) == 0


@patch("builtins.input")
def test_delete_section_cancel(mock_input, mock_config_object):
    """Test canceling the delete_section function."""
    from auto_print.config_generator import delete_section

    # Set up the mocks
    mock_input.return_value = "cancel"  # Cancel the deletion

    # Call the function
    result = delete_section(mock_config_object)

    # Verify the result is unchanged
    assert "Test Section" in result
    assert result == mock_config_object


@patch("builtins.input")
@patch("auto_print.config_generator.insert_section")
def test_change_section_position(mock_insert_section, mock_input, mock_config_object):
    """Test the change_section_position function."""
    from auto_print.config_generator import change_section_position

    # Set up the mocks
    mock_input.return_value = "Test Section"  # Change position of test section
    mock_insert_section.return_value = mock_config_object  # Return the same config

    # Call the function
    result = change_section_position(mock_config_object)

    # Verify the result
    assert result == mock_config_object
    # Verify insert_section was called with the correct parameters
    # The temp_config passed to insert_section should be empty
    mock_insert_section.assert_called_once()
    args, _ = mock_insert_section.call_args
    assert len(args[0]) == 0  # First arg should be an empty config
    assert args[1] == "Test Section"  # Second arg should be the section name
    assert (
        args[2] == mock_config_object["Test Section"]
    )  # Third arg should be the section


@patch("auto_print.config_generator.configure_logger")
@patch("auto_print.config_generator.check_ghostscript")
@patch("auto_print.config_generator.load_config")
@patch("auto_print.config_generator.print_configuration")
@patch("auto_print.config_generator.input_choice")
@patch("auto_print.config_generator.save_config")
@patch("auto_print.config_generator.add_section")
@patch("auto_print.config_generator.delete_section")
@patch("auto_print.config_generator.repair_config")
@patch("auto_print.config_generator.change_section_position")
@patch("auto_print.config_generator.edit_section_command")
@patch("auto_print.config_generator.bool_decision")
@patch("auto_print.config_generator.show_help")
def test_main(
    mock_show_help,
    mock_bool_decision,
    mock_edit_section_command,
    mock_change_section_position,
    mock_repair_config,
    mock_delete_section,
    mock_add_section,
    mock_save_config,
    mock_input_choice,
    mock_print_configuration,
    mock_load_config,
    mock_check_ghostscript,
    mock_configure_logger,
):
    """Test the main function."""
    from auto_print.config_generator import main

    # Set up the mocks
    mock_config = CaseInsensitiveDict({"Test Section": {"printer": "Test Printer"}})
    mock_load_config.return_value = mock_config

    # Test different actions
    # First call: save, then close
    mock_input_choice.side_effect = ["save", "close"]
    mock_bool_decision.return_value = True  # Confirm close

    # Call the function
    main()

    # Verify the function calls
    mock_configure_logger.assert_called_once()
    mock_check_ghostscript.assert_called_once()
    assert mock_load_config.call_count >= 1
    mock_print_configuration.assert_called_with(mock_config)
    mock_save_config.assert_called_once_with(mock_config)
    assert mock_input_choice.call_count == 2


@patch("builtins.input")
def test_configure_prefix(mock_input):
    """Test the configure_prefix function."""
    # Test with a non-empty prefix
    mock_input.return_value = "test_prefix"
    config_element = {}
    configure_prefix(config_element)
    assert config_element["prefix"] == "test_prefix"

    # Test with an empty prefix
    mock_input.return_value = ""
    config_element = {}
    configure_prefix(config_element)
    assert "prefix" not in config_element


@patch("builtins.input")
def test_configure_suffix(mock_input):
    """Test the configure_suffix function."""
    # Test with a non-empty suffix
    mock_input.return_value = ".pdf"
    config_element = {}
    configure_suffix(config_element)
    assert config_element["suffix"] == ".pdf"

    # Test with an empty suffix
    mock_input.return_value = ""
    config_element = {}
    configure_suffix(config_element)
    assert "suffix" not in config_element


@patch("auto_print.config_generator.input_choice")
@patch("auto_print.config_generator.bool_decision")
def test_configure_print_settings(mock_bool_decision, mock_input_choice):
    """Test the configure_print_settings function."""
    # Test with print enabled
    mock_bool_decision.return_value = True
    mock_input_choice.return_value = "Test Printer"
    config_element = {}
    configure_print_settings(config_element)
    assert config_element["print"] is True
    assert config_element["printer"] == "Test Printer"

    # Test with print disabled
    mock_bool_decision.return_value = False
    config_element = {}
    configure_print_settings(config_element)
    assert config_element["print"] is False
    assert "printer" in config_element  # Should still have a default printer


@patch("auto_print.config_generator.bool_decision")
def test_configure_display_settings(mock_bool_decision):
    """Test the configure_display_settings function."""
    # Test with show enabled
    mock_bool_decision.return_value = True
    config_element = {}
    configure_display_settings(config_element)
    assert config_element["show"] is True

    # Test with show disabled
    mock_bool_decision.return_value = False
    config_element = {}
    configure_display_settings(config_element)
    assert config_element["show"] is False


@patch("auto_print.config_generator.bool_decision")
def test_configure_activation(mock_bool_decision):
    """Test the configure_activation function."""
    # Test with activation enabled
    mock_bool_decision.return_value = True
    config_element = {}
    configure_activation(config_element)
    assert config_element["active"] is True

    # Test with activation disabled
    mock_bool_decision.return_value = False
    config_element = {}
    configure_activation(config_element)
    assert config_element["active"] is False


@patch("auto_print.config_generator.print_element")
def test_display_insert_positions(mock_print_element, mock_config_object):
    """Test the display_insert_positions function."""
    # Call the function
    result = display_insert_positions(mock_config_object)

    # Verify the result
    assert result == 1  # mock_config_object has 1 section
    assert mock_print_element.call_count == 1


@patch("auto_print.config_generator.input_choice")
def test_get_insert_position(mock_input_choice):
    """Test the get_insert_position function."""
    # Test with "end"
    mock_input_choice.return_value = "end"
    result = get_insert_position(3)
    assert result == "3"

    # Test with "start"
    mock_input_choice.return_value = "start"
    result = get_insert_position(3)
    assert result == "0"

    # Test with a specific position
    mock_input_choice.return_value = "2"
    result = get_insert_position(3)
    assert result == "2"

    # Test with "cancel"
    mock_input_choice.return_value = "cancel"
    result = get_insert_position(3)
    assert result == "cancel"


@patch("auto_print.config_generator.save_config")
@patch("auto_print.config_generator.add_section")
@patch("auto_print.config_generator.delete_section")
@patch("auto_print.config_generator.repair_config")
@patch("auto_print.config_generator.print_configuration")
@patch("auto_print.config_generator.change_section_position")
@patch("auto_print.config_generator.edit_section_command")
@patch("auto_print.config_generator.bool_decision")
@patch("auto_print.config_generator.show_help")
@patch("auto_print.config_generator.load_config")
def test_handle_action(
    mock_load_config,
    mock_show_help,
    mock_bool_decision,
    mock_edit_section_command,
    mock_change_section_position,
    mock_print_configuration,
    mock_repair_config,
    mock_delete_section,
    mock_add_section,
    mock_save_config,
):
    """Test the handle_action function."""
    config = CaseInsensitiveDict({"Test Section": {"printer": "Test Printer"}})

    # Test "save" action
    result, exit_program = handle_action("save", config)
    assert result == config
    assert exit_program is False
    mock_save_config.assert_called_once_with(config)

    # Reset mocks
    mock_save_config.reset_mock()

    # Test "add" action
    mock_add_section.return_value = config
    result, exit_program = handle_action("add", config)
    assert result == config
    assert exit_program is False
    mock_add_section.assert_called_once_with(config)

    # Reset mocks
    mock_add_section.reset_mock()

    # Test "delete" action
    mock_delete_section.return_value = config
    result, exit_program = handle_action("delete", config)
    assert result == config
    assert exit_program is False
    mock_delete_section.assert_called_once_with(config)

    # Test "close" action with no changes
    mock_load_config.return_value = config
    result, exit_program = handle_action("close", config)
    assert result == config
    assert exit_program is True

    # Test "close" action with changes but confirm
    mock_load_config.return_value = CaseInsensitiveDict({"Other": {}})
    mock_bool_decision.return_value = True
    result, exit_program = handle_action("close", config)
    assert result == config
    assert exit_program is True

    # Test "close" action with changes but cancel
    mock_load_config.return_value = CaseInsensitiveDict({"Other": {}})
    mock_bool_decision.return_value = False
    result, exit_program = handle_action("close", config)
    assert result == config
    assert exit_program is False
