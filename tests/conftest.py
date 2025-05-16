"""Pytest configuration file for auto_print tests.

Contains fixtures and configuration shared across test files.
"""

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
def temp_config_file(tmp_path):
    """Creates a temporary config file for testing."""
    config_path = tmp_path / "test_config.json"
    config_path.write_text(
        '{"Test Section": {"printer": "Microsoft Print to PDF", "prefix": "test_", "suffix": "_document", "software": "", "delete": false}}'
    )
    return config_path
