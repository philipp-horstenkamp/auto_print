"""Example tests demonstrating how to use the new fixtures.

This file contains example tests that show how to use the new fixtures
for testing both the auto_print_config_generator and auto_print_execute applications.
"""

from unittest.mock import patch

import pytest

from auto_print.auto_print_config_generator import load_config
from auto_print.auto_print_execute import main as execute_main


# Example test for auto_print_config_generator
def test_load_config_with_basic_file(basic_config_file):
    """Test loading a basic configuration file."""
    with patch(
        "auto_print.auto_print_config_generator.PRINTER_CONFIG_PATH", basic_config_file
    ):
        # Call the function under test
        result = load_config()

    # Verify the results
    assert "PDF Documents" in result
    assert result["PDF Documents"]["printer"] == "Microsoft Print to PDF"
    assert result["PDF Documents"]["prefix"] == "invoice_"
    assert result["PDF Documents"]["suffix"] == ".pdf"
    assert result["PDF Documents"]["print"] is True
    assert result["PDF Documents"]["show"] is False
    assert result["PDF Documents"]["active"] is True


def test_load_config_with_multi_section_file(multi_section_config_file):
    """Test loading a configuration file with multiple sections."""
    with patch(
        "auto_print.auto_print_config_generator.PRINTER_CONFIG_PATH",
        multi_section_config_file,
    ):
        # Call the function under test
        result = load_config()

    # Check that all sections are loaded
    assert "PDF Documents" in result
    assert "Long PDF Documents" in result
    assert "Short PDF Files" in result

    # Check specific values in each section
    assert "suffix" not in result["Long PDF Documents"]
    assert result["Long PDF Documents"]["print"] is False
    assert result["Long PDF Documents"]["show"] is True

    assert result["Short PDF Files"]["suffix"] == ".pdf"
    assert result["Short PDF Files"]["active"] is False


def test_load_config_with_edge_case_file(edge_case_config_file):
    """Test loading a configuration file with edge cases."""
    with patch(
        "auto_print.auto_print_config_generator.PRINTER_CONFIG_PATH",
        edge_case_config_file,
    ):
        # Call the function under test
        result = load_config()

    # Check that all sections are loaded
    assert "Empty Section" in result
    assert "Special Characters!@#$" in result
    assert (
        "Very Long Section Name That Might Cause Display Issues In The User Interface"
        in result
    )

    # Check that the empty section has only the required fields
    assert "printer" in result["Empty Section"]
    assert "active" in result["Empty Section"]
    assert "prefix" not in result["Empty Section"]

    # Check that special characters are handled correctly
    assert result["Special Characters!@#$"]["prefix"] == "test!@#_"
    assert result["Special Characters!@#$"]["suffix"] == "_$pecial.pdf"


# Example test for auto_print_execute
@patch("auto_print.auto_print_execute.win32api.ShellExecute")
@patch("auto_print.auto_print_execute.check_ghostscript")
def test_execute_with_matching_file(
    mock_shell_execute, mock_check_ghostscript, basic_config_file, tmp_path
):
    """Test the execute function with a file that matches configuration."""
    # Create a test PDF file that matches the configuration
    test_file = tmp_path / "invoice_test.pdf"
    test_file.write_text("Test content")

    # Mock sys.argv to simulate command line arguments
    with (
        patch("sys.argv", ["auto_print", str(test_file)]),
        patch("auto_print.auto_print_execute.PRINTER_CONFIG_PATH", basic_config_file),
    ):
        # Check that the program exits with success (0)
        # This would indicate that a matching section was found and processed
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            execute_main()
        assert pytest_wrapped_e.value.code == 0


@pytest.mark.working_on
def test_execute_with_non_matching_file(multi_section_config_file, tmp_path):
    """Test the execute function with a file that doesn't match any configuration."""
    # Create a test file that doesn't match any configuration
    test_file = tmp_path / "non_matching_file.pdf"
    test_file.write_text("Test content")

    # Mock sys.argv to simulate command line arguments
    with (
        patch("sys.argv", ["auto_print", str(test_file)]),
        patch(
            "auto_print.auto_print_execute.PRINTER_CONFIG_PATH",
            multi_section_config_file,
        ),
    ):
        # The function should complete without raising SystemExit
        # since no matching section was found
        execute_main()

    # If we reach this point, the test passes because no SystemExit was raised


def test_execute_with_show_only_config(
    mock_os_startfile, multi_section_config_file, tmp_path
):
    """Test the execute function with a configuration that only shows the file."""
    # Create a test file that matches the "Long PDF Documents" section
    test_file = tmp_path / "Long_test.pdf"
    test_file.write_text("Test content")

    # Mock sys.argv to simulate command line arguments
    with (
        patch("sys.argv", ["auto_print", str(test_file)]),
        patch(
            "auto_print.auto_print_execute.PRINTER_CONFIG_PATH",
            multi_section_config_file,
        ),
    ):
        # The function should complete without raising SystemExit
        # since it's just showing the file
        execute_main()

    mock_os_startfile.assert_called_once()
    # Check that startfile was called to show the file
    mock_os_startfile.assert_called_with(str(test_file))
    # If we reach this point, the test passes because no SystemExit was raised
