.. _cli:

Command Line Interface
======================

Overview
--------

auto-print is a utility that automates the printing of files based on their filenames. It provides two main entry points:

1. **Configuration Generator**: An interactive tool for setting up printer configurations
2. **Print Executor**: A command-line tool for printing files based on the configuration

Configuration Options
--------------------

The auto-print configuration consists of multiple sections, each defining how specific types of documents are handled. Sections are the core of auto-print's functionality, allowing you to create rules for different document types based on their filenames.

Each section represents a specific document handling rule that includes:

* **Name**: A unique identifier for the section (e.g., "Invoices", "Shipping Labels", "Reports")
* **Prefix**: (Optional) Files must start with this string to match this section (e.g., "INV_" for invoices)
* **Suffix**: (Optional) Files must end with this string to match this section (e.g., ".pdf", "_report.pdf")
* **Print**: Whether to print the file automatically (true/false)
* **Printer**: Which printer to use (only relevant if Print is true)
* **Show**: Whether to open the file with the system default application such as Adobe Reader (true/false)
* **Active**: Whether this section is currently active (true/false)

**How Sections Work**

When a file is processed by auto-print, it checks each active section in order until it finds a match. A section matches when:

1. The filename starts with the section's prefix (if a prefix is defined)
2. The filename ends with the section's suffix (if a suffix is defined)

Once a matching section is found, the file is handled according to that section's settings (print and/or show), and no other rules are executed.

The configuration is stored in ``%USERPROFILE%\auto-printer\auto-printer-config.json``.

**Example Sections**

Here are examples of different section configurations for various document types:

1. **Invoice Section**:
   - Name: "Invoices"
   - Prefix: "INV_"
   - Suffix: ".pdf"
   - Print: true
   - Printer: "Accounting Printer"
   - Show: false
   - Active: true

   *This section automatically prints all PDF files that start with "INV_" to the "Accounting Printer" without opening them.*

2. **Shipping Label Section**:
   - Name: "Shipping Labels"
   - Prefix: "SHIP_"
   - Suffix: ".pdf"
   - Print: true
   - Printer: "Label Printer"
   - Show: false
   - Active: true

   *This section automatically prints all PDF files that start with "SHIP_" to the "Label Printer" without opening them.*

3. **Report Section**:
   - Name: "Reports"
   - Suffix: "_report.pdf"
   - Print: false
   - Show: true
   - Active: true

   *This section automatically opens all PDF files that end with "_report.pdf" without printing them.*

4. **Default PDF Handler**:
   - Name: "All PDFs"
   - Suffix: ".pdf"
   - Print: true
   - Printer: "Default Printer"
   - Show: true
   - Active: true

   *This section handles any PDF file that didn't match previous sections, printing it to the default printer and opening it.*

Entry Points
-----------

.. _config-generator:

Configuration Generator
~~~~~~~~~~~~~~~~~~~~~~

.. argparse::
   :module: auto_print.auto_print_config_generator
   :func: get_parser
   :prog: auto_print_config_generator

The configuration generator provides an interactive interface to create and manage printer configurations.

**Usage:**

.. code-block:: bash

    python -m auto_print.auto_print_config_generator

**Interactive Commands:**

* ``save`` or ``s``: Save the current configuration
* ``add`` or ``a``: Add a new printer section
* ``delete`` or ``d``: Delete a printer section
* ``repair`` or ``r``: Repair the configuration (fix invalid printer references)
* ``show``: Display the current configuration
* ``change``: Change the position of a section
* ``edit`` or ``e``: Edit a section
* ``close`` or ``c``: Close the application
* ``help`` or ``h``: Show help

**Configuration Workflow:**

1. Run the configuration generator
2. Use ``add`` to create new sections or ``edit`` to modify existing ones
3. For each section, specify:
   - Prefix and/or suffix for filename matching
   - Whether to print automatically
   - Which printer to use (if printing)
   - Whether to show the file
   - Whether the section should be active
4. Use ``save`` to store your configuration
5. Use ``close`` to exit the application

.. _print-executor:

Print Executor
~~~~~~~~~~~~~

.. argparse::
   :module: auto_print.auto_print_execute
   :func: get_parser
   :prog: auto_print_execute

The print executor is used to print files based on the configuration.

**Usage:**

.. code-block:: bash

    python -m auto_print.auto_print_execute <file_path>

**Arguments:**

* ``file_path``: Path to the file to be printed

**Execution Workflow:**

1. The print executor checks if the specified file exists
2. It loads the printer configuration from ``%USERPROFILE%\auto-printer\auto-printer-config.json``
3. It extracts the filename from the path
4. It compares the filename against each active configuration section:
   - If both prefix and suffix match, the file is processed according to that section
   - If a prefix or suffix is not specified in a section, that part of the check is always considered a match
5. For the first matching section, the file is:
   - Printed directly to the specified printer if "print" is true
   - Opened with the default application if "show" is true
   - Both printed and shown if both are true
6. If no matching section is found, an error is logged

**Example:**

.. code-block:: bash

    python -m auto_print.auto_print_execute invoice_123.pdf

This will print the file "invoice_123.pdf" to the appropriate printer based on your configuration.

**Exit Codes:**

* ``0``: Success
* ``-1``: No file to print specified
* ``-2``: Too many arguments
* ``-3``: File does not exist
* ``-4``: Error loading configuration
* ``-5``: Ghostscript not installed or other error
