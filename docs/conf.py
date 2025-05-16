# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from importlib.metadata import metadata

sys.path.insert(0, os.path.abspath(".."))  # noqa: PTH100

from unittest.mock import MagicMock


class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        # Return None for special attributes to prevent recursion
        if name.startswith("_"):
            return None
        return Mock()


MOCK_MODULES = ["win32api", "win32print"]
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Get metadata from the package
_DISTRIBUTION_METADATA = metadata("auto-print")

project = _DISTRIBUTION_METADATA["Name"]
copyright = "2025, Philipp Horstenkamp"  # noqa: A001
author = _DISTRIBUTION_METADATA["Author"]

# The full version, including alpha/beta/rc tags
release = _DISTRIBUTION_METADATA["Version"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    # "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinxarg.ext",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for language switcher ------------------------------------------
html_context = {
    "languages": [
        ("en", "English"),
        ("de", "Deutsch"),
    ],
}

# -- Options for internationalization ----------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-internationalization

language = "en"
locale_dirs = ["locale/"]
gettext_compact = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Options for autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

autodoc_member_order = "bysource"
autoclass_content = "both"
