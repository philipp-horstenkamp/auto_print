"""Pytest configuration file for auto_print tests.

Contains fixtures and configuration shared across test files.
"""

import json
import sys
from pathlib import Path

import pytest

# Add the src directory to the Python path so we can import the auto_print package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_config_dict():
    """Returns a sample configuration dictionary for testing."""
    return {
        "Test Section": {
            "printer": "Microsoft Print to PDF",
            "prefix": "test_",
            "suffix": "_document",
            "software": "",
            "delete": False,
        }
    }


@pytest.fixture
def temp_config_file(
    tmp_path: Path, sample_config_dict: dict[str, dict[str, str | bool]]
):
    """Creates a temporary config file for testing."""
    config_path = tmp_path / "test_config.json"
    config_path.write_text(
        '{"Test Section": {"printer": "Microsoft Print to PDF", "prefix": "test_", "suffix": "_document", "software": "", "delete": false}}'
    )
    return config_path


@pytest.fixture
def temp_empty_config_file(
    tmp_path: Path, sample_config_dict: dict[str, dict[str, str | bool]]
):
    """Creates a temporary empty config file for testing."""
    config_path = tmp_path / "test_config.json"
    config_path.write_text("")
    return config_path


@pytest.fixture
def temp_broken_config_file(
    tmp_path: Path, sample_config_dict: dict[str, dict[str, str | bool]]
):
    """Creates a temporary broken config file for testing."""
    config_path = tmp_path / "test_config.json"
    config_path.write_text("{")
    return config_path


@pytest.fixture
def basic_config_file(tmp_path):
    """Creates a basic temporary config file for testing.

    This fixture creates a simple configuration with one section.

    Args:
        tmp_path: Pytest fixture that provides a temporary directory

    Returns:
        Path: Path to the temporary configuration file
    """
    config_path = tmp_path / "basic_config.json"
    config_content = {
        "PDF Documents": {
            "printer": "Microsoft Print to PDF",
            "prefix": "invoice_",
            "suffix": ".pdf",
            "print": True,
            "show": False,
            "active": True,
        }
    }
    config_path.write_text(json.dumps(config_content, indent=2), encoding="utf-8")
    return config_path


@pytest.fixture
def multi_section_config_file(tmp_path):
    """Creates a config file with multiple sections for testing.

    This fixture creates a configuration with multiple sections to test
    handling of different file types and configurations.

    Args:
        tmp_path: Pytest fixture that provides a temporary directory

    Returns:
        Path: Path to the temporary configuration file
    """
    config_path = tmp_path / "multi_section_config.json"
    config_content = {
        "PDF Documents": {
            "printer": "Microsoft Print to PDF",
            "prefix": "invoice_",
            "suffix": ".pdf",
            "print": True,
            "show": False,
            "active": True,
        },
        "Word Documents": {
            "printer": "Microsoft Print to PDF",
            "suffix": ".pdf",
            "print": False,
            "show": True,
            "active": True,
        },
        "Excel Files": {
            "printer": "Microsoft Print to PDF",
            "suffix": ".xlsx",
            "print": True,
            "show": True,
            "active": True,
        },
        "All": {"active": True, "show": True, "print": False},
    }
    config_path.write_text(json.dumps(config_content, indent=2), encoding="utf-8")
    return config_path


@pytest.fixture
def edge_case_config_file(tmp_path):
    """Creates a config file with edge cases for testing.

    This fixture creates a configuration with special characters,
    empty values, and other edge cases to test robustness.

    Args:
        tmp_path: Pytest fixture that provides a temporary directory

    Returns:
        Path: Path to the temporary configuration file
    """
    config_path = tmp_path / "edge_case_config.json"
    config_content = {
        "Empty Section": {"printer": "Microsoft Print to PDF", "active": True},
        "Special Characters!@#$": {
            "printer": "Microsoft Print to PDF",
            "prefix": "test!@#_",
            "suffix": "_$pecial.pdf",
            "print": True,
            "show": True,
            "active": True,
        },
        "Very Long Section Name That Might Cause Display Issues In The User Interface": {
            "printer": "Microsoft Print to PDF",
            "prefix": "very_long_prefix_name_",
            "suffix": "_very_long_suffix.pdf",
            "print": True,
            "show": False,
            "active": True,
        },
    }
    config_path.write_text(json.dumps(config_content, indent=2), encoding="utf-8")
    return config_path
