# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from importlib.metadata import metadata
from pathlib import Path

sys.path.insert(0, Path("..").resolve())  # type: ignore

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

# Read metadata from package
_DISTRIBUTION_METADATA = metadata("auto-print")

# Extract metadata
project = str(_DISTRIBUTION_METADATA["Name"]).replace("-", " ")
author = _DISTRIBUTION_METADATA["Author"].split("<")[0].strip()
copyright = f"2025, {author}"  # noqa: A001
release = _DISTRIBUTION_METADATA["Version"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # Automatically generate API documentation from docstrings
    # "sphinx.ext.viewcode",   # Add links to highlighted source code
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    "sphinx.ext.intersphinx",  # Link to another project's documentation
    "sphinxarg.ext",  # Document command-line arguments
    "sphinx_copybutton",  # Add copy buttons to code blocks
    "sphinx_autodoc_typehints",  # Better type hint documentation
    "sphinx_markdown_tables",  # Better rendering of markdown tables
    "sphinx_rtd_dark_mode",  # Dark mode toggle for Read the Docs theme
    "sphinxcontrib.mermaid",  # Mermaid diagrams support
    "sphinx_prompt",  # Better command prompt examples
    "sphinx_tabs.tabs",  # Tabbed content for code examples
    "notfound.extension",
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
html_logo = "auto-printer-img.png"
html_favicon = "../printer.ico"

# -- Options for autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

autodoc_member_order = "bysource"
autoclass_content = "both"

notfound_urls_prefix = "/"
