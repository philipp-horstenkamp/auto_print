"""Auto Print package for automatic document printing and routing.

This package provides functionality to automatically route documents to printers
or default applications based on filename patterns and configurations.
"""

from importlib.metadata import metadata
from typing import Final

_DISTRIBUTION_METADATA = metadata("auto-print")

__author__: Final[str] = _DISTRIBUTION_METADATA["Author"]
__email__: Final[str] = _DISTRIBUTION_METADATA["Author-email"]
__version__: Final[str] = _DISTRIBUTION_METADATA["Version"]
__description__: Final[str] = _DISTRIBUTION_METADATA["Description"]
__LICENSE__: Final[str] = _DISTRIBUTION_METADATA["Version"]
