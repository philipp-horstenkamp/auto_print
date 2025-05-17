"""Tests for the fixtures defined in conftest.py.

This file contains tests that verify the content of the temporary files
created by the fixtures in conftest.py.
"""

import json
from pathlib import Path

import pytest


def test_temp_config_file(temp_config_file: Path):
    """Test that the temp_config_file fixture creates a file with the expected content."""
    # Verify that the file exists
    assert temp_config_file.exists()

    # Read the content of the file
    content = temp_config_file.read_text()

    # Parse the JSON content
    config = json.loads(content)

    # Verify the content matches the expected structure
    assert "Test Section" in config
    assert config["Test Section"]["printer"] == "Microsoft Print to PDF"
    assert config["Test Section"]["prefix"] == "test_"
    assert config["Test Section"]["suffix"] == "_document"
    assert config["Test Section"]["software"] == ""
    assert config["Test Section"]["delete"] is False


def test_temp_empty_config_file(temp_empty_config_file: Path):
    """Test that the temp_empty_config_file fixture creates an empty file."""
    # Verify that the file exists
    assert temp_empty_config_file.exists()

    # Read the content of the file
    content = temp_empty_config_file.read_text()

    # Verify the content is empty
    assert content == ""


def test_temp_broken_config_file(temp_broken_config_file: Path):
    """Test that the temp_broken_config_file fixture creates a file with broken JSON."""
    # Verify that the file exists
    assert temp_broken_config_file.exists()

    # Read the content of the file
    content = temp_broken_config_file.read_text()

    # Verify the content is a broken JSON (just an opening brace)
    assert content == "{"

    # Verify that the content cannot be parsed as valid JSON
    with pytest.raises(json.JSONDecodeError):
        json.loads(content)


def test_basic_config_file(basic_config_file: Path):
    """Test that the basic_config_file fixture creates a file with the expected content."""
    # Verify that the file exists
    assert basic_config_file.exists()

    # Read the content of the file
    content = basic_config_file.read_text(encoding="utf-8")

    # Parse the JSON content
    config = json.loads(content)

    # Verify the content matches the expected structure
    assert "PDF Documents" in config
    assert config["PDF Documents"]["printer"] == "Microsoft Print to PDF"
    assert config["PDF Documents"]["prefix"] == "invoice_"
    assert config["PDF Documents"]["suffix"] == ".pdf"
    assert config["PDF Documents"]["print"] is True
    assert config["PDF Documents"]["show"] is False
    assert config["PDF Documents"]["active"] is True


def test_multi_section_config_file(multi_section_config_file: Path):
    """Test that the multi_section_config_file fixture creates a file with the expected content."""
    # Verify that the file exists
    assert multi_section_config_file.exists()

    # Read the content of the file
    content = multi_section_config_file.read_text(encoding="utf-8")

    # Parse the JSON content
    config = json.loads(content)

    # Verify the content matches the expected structure
    assert "PDF Documents" in config
    assert "Long PDF Documents" in config
    assert "Short PDF Files" in config
    assert "All" in config

    # Check PDF Documents section
    assert config["PDF Documents"]["printer"] == "Microsoft Print to PDF"
    assert config["PDF Documents"]["prefix"] == "invoice_"
    assert config["PDF Documents"]["suffix"] == ".pdf"
    assert config["PDF Documents"]["print"] is True
    assert config["PDF Documents"]["show"] is False
    assert config["PDF Documents"]["active"] is True

    # Check Word Documents section
    assert config["Long PDF Documents"]["printer"] == "Microsoft Print to PDF"
    assert config["Long PDF Documents"]["prefix"] == "Long"
    assert config["Long PDF Documents"]["print"] is False
    assert config["Long PDF Documents"]["show"] is True
    assert config["Long PDF Documents"]["active"] is True

    # Check Excel Files section
    assert config["Short PDF Files"]["printer"] == "Microsoft Print to PDF"
    assert config["Short PDF Files"]["prefix"] == "Sort"
    assert config["Short PDF Files"]["print"] is True
    assert config["Short PDF Files"]["show"] is True
    assert config["Short PDF Files"]["active"] is False

    # Check All section
    assert config["All"]["active"] is False
    assert config["All"]["show"] is True
    assert config["All"]["print"] is False


def test_edge_case_config_file(edge_case_config_file: Path):
    """Test that the edge_case_config_file fixture creates a file with the expected content."""
    # Verify that the file exists
    assert edge_case_config_file.exists()

    # Read the content of the file
    content = edge_case_config_file.read_text(encoding="utf-8")

    # Parse the JSON content
    config = json.loads(content)

    # Verify the content matches the expected structure
    assert "Empty Section" in config
    assert "Special Characters!@#$" in config
    assert (
        "Very Long Section Name That Might Cause Display Issues In The User Interface"
        in config
    )

    # Check Empty Section
    assert config["Empty Section"]["printer"] == "Microsoft Print to PDF"
    assert config["Empty Section"]["active"] is True

    # Check Special Characters section
    assert config["Special Characters!@#$"]["printer"] == "Microsoft Print to PDF"
    assert config["Special Characters!@#$"]["prefix"] == "test!@#_"
    assert config["Special Characters!@#$"]["suffix"] == "_$pecial.pdf"
    assert config["Special Characters!@#$"]["print"] is True
    assert config["Special Characters!@#$"]["show"] is True
    assert config["Special Characters!@#$"]["active"] is True

    # Check Very Long Section Name section
    assert (
        config[
            "Very Long Section Name That Might Cause Display Issues In The User Interface"
        ]["printer"]
        == "Microsoft Print to PDF"
    )
    assert (
        config[
            "Very Long Section Name That Might Cause Display Issues In The User Interface"
        ]["prefix"]
        == "very_long_prefix_name_"
    )
    assert (
        config[
            "Very Long Section Name That Might Cause Display Issues In The User Interface"
        ]["suffix"]
        == "_very_long_suffix.pdf"
    )
    assert (
        config[
            "Very Long Section Name That Might Cause Display Issues In The User Interface"
        ]["print"]
        is True
    )
    assert (
        config[
            "Very Long Section Name That Might Cause Display Issues In The User Interface"
        ]["show"]
        is False
    )
    assert (
        config[
            "Very Long Section Name That Might Cause Display Issues In The User Interface"
        ]["active"]
        is True
    )
