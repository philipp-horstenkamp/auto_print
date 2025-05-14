# Auto Print

<!--TOC-->



- [Auto Print](#auto-print)

  - [Rust Implementation](#rust-implementation)

  - [Python Implementation](#python-implementation)
    - [Installation](#installation)
      - [Using MSI Installer](#using-msi-installer)
      - [From Source (Python)](#from-source-python)

  - [Integrate in browser workflow](#integrate-in-browser-workflow)

  - [Main commands](#main-commands)

  - [Configuration example](#configuration-example)

  - [Software dependencies](#software-dependencies)

  - [How it works](#how-it-works)

  - [About](#about)

  - [License](#license)



<!--TOC-->


## Rust Implementation

This project has been translated from Python to Rust. The Rust implementation provides the same functionality with improved performance and memory safety.

### Requirements

- Rust 1.70 or later
- Windows operating system
- Ghostscript (for printing without showing documents)

### Installation

#### From Source

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/auto_print.git
   cd auto_print
   ```

2. Build the application:
   ```
   cargo build --release
   ```

3. The executables will be available in the `target/release` directory:
   - `auto_print_execute.exe`: The main document processing application
   - `auto_print_config_generator.exe`: The configuration tool

### Usage

#### Configuration

Run the configuration generator:

```
cargo run --bin auto_print_config_generator
```

#### Processing Documents

To process a document:

```
cargo run --bin auto_print_execute -- path/to/your/document.pdf
```










## Python Implementation

### Installation

#### Using MSI Installer

An MSI installer is available for Windows users. This installer:
- Installs the application with all necessary dependencies
- Creates shortcuts in the Start Menu
- Adds a file association for PDF files (without overriding your default PDF application)

To build the MSI installer:

1. Ensure you have Python 3.11 or later installed
2. Install the required dependencies:
   ```
   pip install poetry
   poetry install --with build
   ```
3. Run the MSI setup script:
   ```
   python msi_setup.py bdist_msi
   ```
4. The MSI installer will be created in the `dist` directory

#### From Source (Python)

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/auto_print.git
   cd auto_print
   ```

2. Install dependencies:
   ```
   pip install poetry
   poetry install
   ```

3. Run the application:
   ```
   poetry run auto-print path/to/your/document.pdf
   ```

## Integrate in browser workflow
One of the use cases is to use this software as a default PDF executable from Firefox or Chrome:
Here some images on how to configure that:

1. Open the Settings Tab in your Browser as shown by the firefox browser:
![go to settings](docs/Settings.PNG)
2. Choose the auto-printer.exe as your default executable for pdf and all pdf like formats.
![Choose auto-printer.exe as your default software](docs/ChoosePrinter.PNG)

## Main commands

| Command | Short | Result                                                    |
|:-------:|-------|:----------------------------------------------------------|
|  save   | s     | Save the configuration.                                   |
|  close  | c     | Closes the configuration generator.                       |
|   add   | a     | Add a new section to the configuration.                   | 
| delete  | d     | Delete a section from the configuration.                  |
|  show   | s     | Show the configuration in text form.                      |
| change  |       | Changes the section order.                                |
|  edit   | e     | Edits a section.                                          |
|  help   | h     | Show the help information.                                |
| repair  | r     | Repair the config file by checking if all printers exist. |



## Configuration example

The below file is an example with comments.
The file `TEST_something.pdf` would be printed with the first printer.
The file `Something_to_print.pdf` would be used by the second printer.
The file `ABC.docx` would be shown with MS Word (if installed).
```json
{
  "Marke": {
    "active": true,                 // Section active. Should be used.
    "printer": "MyPreciousPrinter",
    "prefix": "TEST_",              // How the file should start.
    "suffix": ".pdf",               // How the file should end.
    "print": true,                  // Prints the file.
    "show": false                   // Does not show the file.
  },
  "SomeOtherCategory": {
    "active": false,                // Section not active. Can't be used.
    "printer": "AnotherPrinter",
    "prefix": "Something",
    "suffix": ".pdf",
    "show": true,                   // Printing via default windows application
    "print": true
  },
  "UseDefaultPrinter": {
    "active": true,
                                    //no printer is given therefore the default printer is used."
    "prefix": "DefPrintFile",
    "suffix": ".pdf",
    "show": false,
    "print": true
  },
  "All": {                          // Default action (No requirements)
    "active": true,               
    "show": true,                   // Show without printing (Windows Default action)
    "print": false
  }
}
```


## Software dependencies
To use the software effectively, the following programs are needed:

- [Ghostscript](https://www.ghostscript.com/releases/gsdnld.html)
- [Adobe PDF Reader](https://www.adobe.com/de/acrobat/pdf-reader.html)
- [Rust](https://www.rust-lang.org/tools/install) (for building from source)

## How it works 

The goal of this project is to simplify the tedious task or printing similar forms.

1. The program is started with a filepath as an argument.
2. The filename gets extracted.
3. The filename is compared to a list of suffixes and prefixes.
4. If suffix and prefix are a match the file gets executed.
If a suffix or a prefix is not given the comparison is true either way.
5. The file is then eiter Printed and/or shown depending on the configuration.

Everything is logged and can be locked up in the auto_print.log file!

## About

This project was originally written in Python by Philipp Horstenkamp in the hope 
that it will make some office processes a bit more smooth.

The Rust implementation maintains the same functionality while providing improved 
performance and memory safety.

## License

This project is licensed under the MIT License.
