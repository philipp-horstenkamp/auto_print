"""Auto-print package for automatic document routing and printing.

This package provides functionality to automatically route documents to printers
or other applications based on filename patterns.
"""

from importlib.metadata import metadata
from typing import Final

_DISTRIBUTION_METADATA = metadata("auto-print")

__author__: Final[str] = _DISTRIBUTION_METADATA["Author"]
__email__: Final[str] = _DISTRIBUTION_METADATA["Author-email"]
__version__: Final[str] = _DISTRIBUTION_METADATA["Version"]
__description__: Final[str] = _DISTRIBUTION_METADATA["Description"]
__LICENSE__: Final[str] = _DISTRIBUTION_METADATA["Version"]
