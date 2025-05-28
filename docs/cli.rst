Command Line Interface
======================

Overview
--------

**auto-print** automates printing and viewing of files based on filename rules.

It includes:

1. **Configuration Generator** – Interactive tool for setting up printing rules
2. **Print Executor** – Command-line tool to apply those rules to files

.. note::

   If installed via the MSI installer:

   - Use ``auto-print.exe`` to print files the executable should now also be associated directly with PDF files in the context menu
   - Use ``auto-print-config.exe`` or launch **Auto Print Config** from the Start Menu to configure rules

Configuration
-------------

The configuration file is stored at:

::

    %USERPROFILE%\auto-printer\auto-printer-config.json

Sections define how specific file types should be handled.

Section Properties
~~~~~~~~~~~~~~~~~~

Each section includes the following fields:

- **Name**: Unique identifier (e.g., ``Invoices``)
- **Prefix** *(optional)*: File must start with this string
- **Suffix** *(optional)*: File must end with this string
- **Print**: ``true`` to print the file
- **Printer**: *(optional)* Printer name to use if `Print` is set to true and something other than the default printer should be used.
- **Show**: ``true`` to open with the default application
- **Active**: Whether this section is enabled

Matching Logic
~~~~~~~~~~~~~~

Each file is matched against active sections in order.

A section matches if:

1. The filename starts with the ``Prefix`` (if defined)
2. The filename ends with the ``Suffix`` (if defined)

Only the **first matching** section is used to determine how the file is handled.

Example Sections
~~~~~~~~~~~~~~~~

**Invoices**

::

    Name: "Invoices"
    Prefix: "INV_"
    Suffix: ".pdf"
    Print: true
    Printer: "Accounting Printer"
    Show: false
    Active: true

**Shipping Labels**

::

    Name: "Shipping Labels"
    Prefix: "SHIP_"
    Suffix: ".pdf"
    Print: true
    Printer: "Label Printer"
    Show: false
    Active: true

**Reports**

::

    Name: "Reports"
    Suffix: "_report.pdf"
    Print: false
    Show: true
    Active: true

**Default PDFs**
PDFs that should be shown as normal.
::

    Name: "All PDFs"
    Print: false
    Show: true
    Active: true

Configuration Generator
-----------------------

.. argparse::
   :module: auto_print.auto_print_config_generator
   :func: get_parser
   :prog: auto_print_config_generator

Configuration Workflow
~~~~~~~~~~~~~~~~~~~~~~

1. Launch the generator (via CLI or GUI)
2. Use ``add`` to create or ``edit`` to modify a section
3. For each section, define:
   - Matching rules (`Prefix`, `Suffix`)
   - Actions (`Print`, `Show`)
   - Printer (if applicable)
   - Active status
4. Use ``save`` to persist changes
5. Exit with ``close``

Print Executor
--------------

.. argparse::
   :module: auto_print.auto_print_execute
   :func: get_parser
   :prog: auto_print_execute

Usage
~~~~~

**From source (Python):**

::

    python -m auto_print.auto_print_execute <file_path>

**From MSI installer:**

::

    auto-print.exe print <file_path>

Execution Workflow
~~~~~~~~~~~~~~~~~~

1. Confirm the file exists
2. Load configuration from:

::

    %USERPROFILE%\auto-printer\auto-printer-config.json

3. Extract filename from path
4. Match it against active sections
5. For the first matching section:
   - Print if ``Print`` is ``true``
   - Open if ``Show`` is ``true``
6. Log an error if no match is found

Example
~~~~~~~

::

    auto-print.exe invoice_123.pdf

This prints the file based on the rules defined for "Invoices".

Exit Codes
~~~~~~~~~~

- ``0``: Success
- ``-1``: No file specified
- ``-2``: Too many arguments
- ``-3``: File not found
- ``-4``: Failed to load configuration
- ``-5``: Ghostscript not found or other runtime error
