# Auto Print

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/philipp-horstenkamp/auto_print/graph/badge.svg?token=BHJWD7F0TH)](https://codecov.io/gh/philipp-horstenkamp/auto_print)
[![CI](https://github.com/philipp-horstenkamp/auto_print/actions/workflows/ci.yml/badge.svg)](https://github.com/philipp-horstenkamp/auto_print/actions/workflows/ci.yml)

---

## 📌 What is Auto Print?

**Auto Print** is a simple automation tool for printing or opening documents (e.g., PDFs) based on filename patterns using a configuration file.  
It helps streamline office workflows by associating document types with specific printers or applications.

---

## 🚀 How to Use

### Print a Document

```bash
# If installed globally
auto-print <file_path>

# From source
poetry run python -m auto_print.auto_print_execute <file_path>
```

### Run the Configuration Generator

```bash
# If installed globally
auto-print-config

# From source
poetry run python -m auto_print.auto_print_config_generator
```

### Browser Integration (Firefox)

Use Auto Print as the default handler for PDFs in your browser:

1. Open browser settings  
   ![Settings](docs/Settings.PNG)
2. Set `auto-printer.exe` as the default PDF handler  
   ![Choose App](docs/ChoosePrinter.PNG)

---

## 📦 Installation

### ▶️ Recommended: MSI Installer (Windows)

1. Download the latest `.msi` from [releases](https://github.com/philipp-horstenkamp/auto_print/releases).
2. Follow the installation steps.

**Features**:
- Adds to `PATH`
- Start Menu shortcut
- Right-click PDF context menu integration

### ⚙️ From Source

```bash
git clone https://github.com/philipp-horstenkamp/auto_print.git
cd auto_print

pip install pipx
pipx install poetry
poetry install
```

### Build Wheel or MSI

```bash
# Build wheel
poetry build
pip install dist/*.whl

# Build MSI
poetry install --only main,build
poetry run python msi_setup.py bdist_msi
```

### Uninstall (MSI)

1. Open Control Panel
2. Locate **auto-print**
3. Click **Uninstall**

---

## ⚙️ Configuration

### Configuration Format (JSON)

```json
{
  "Marke": {
    "active": true,
    "printer": "MyPreciousPrinter",
    "prefix": "TEST_",
    "suffix": ".pdf",
    "print": true,
    "show": false
  },
  "UseDefaultPrinter": {
    "active": true,
    "prefix": "DefPrintFile",
    "suffix": ".pdf",
    "show": false,
    "print": true
  },
  "All": {
    "active": true,
    "show": true,
    "print": false
  }
}
```

### Main CLI Commands

| Command | Short | Description                                            |
|:--------|-------|:-------------------------------------------------------|
| save    | s     | Save the configuration                                |
| close   | c     | Close the config tool                                 |
| add     | a     | Add a config section                                  |
| delete  | d     | Remove a section                                      |
| show    | s     | Display the config                                    |
| change  |       | Reorder sections                                      |
| edit    | e     | Edit section content                                  |
| help    | h     | Display help                                          |
| repair  | r     | Validate printer availability                         |

---

## 🔧 Dependencies

To use Auto Print, install:

- [Ghostscript](https://www.ghostscript.com/releases/gsdnld.html)
- [Adobe PDF Reader](https://www.adobe.com/de/acrobat/pdf-reader.html)

---

## 🔍 How It Works

1. Input file name is matched to config prefixes/suffixes.
2. Config defines printer/show actions.
3. Logs stored in `auto_print.log`.

---

## 👤 Author

Created by **Philipp Horstenkamp** to simplify repetitive document handling in office environments.

## 📄 License

This project is licensed under the MIT License – see [LICENSE](LICENSE).
