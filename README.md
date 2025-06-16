# Auto Print

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://img.shields.io/badge/mypy-checked-blue)](https://mypy-lang.org/)
[![codecov](https://codecov.io/gh/philipp-horstenkamp/auto_print/graph/badge.svg?token=BHJWD7F0TH)](https://codecov.io/gh/philipp-horstenkamp/auto_print)
[![CI](https://github.com/philipp-horstenkamp/auto_print/actions/workflows/ci.yml/badge.svg)](https://github.com/philipp-horstenkamp/auto_print/actions/workflows/ci.yml)

---

## 📌 What is Auto Print?

**Auto Print** is a simple automation tool for printing or opening documents (e.g., PDFs) based on filename patterns using a configuration file.  
It helps streamline office workflows by associating document types with specific printers or applications.

---

## 🚀 Quick Start

### Installation

Download and use the MSI form the [GitHub Release Page](https://github.com/philipp-horstenkamp/auto_print/releases).
Additional prerequiremnts such as Ghostscript and Adobe Reader should be Instaled.

### Basic Usage

```bash
# Print a document
auto-print <file_path>

# Configure printing rules
auto-print-config
```
Alternativly Auto Print registers in the Context Menu under the `Open with` section.

For detailed installation and usage instructions, see the [full documentation](docs/index.rst).

---

## 📚 Documentation

- [Installation Guide](docs/installation.rst)
- [Usage Guide](docs/usage.rst)
- [CLI Reference](docs/cli.rst)
- [Contributing](docs/contributing.rst)

---

## 🔧 Dependencies

- [Ghostscript](https://www.ghostscript.com/releases/gsdnld.html)
- [Adobe PDF Reader](https://www.adobe.com/de/acrobat/pdf-reader.html) (recommended)

---

## 👤 Author

Created by **Philipp Horstenkamp** to simplify repetitive document handling in office environments.

## 📄 License

This project is licensed under the MIT License – see [LICENSE](LICENSE).
