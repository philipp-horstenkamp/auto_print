.. _usage:

Usage
=====

Basic Usage
----------

Auto-print is a document routing application that acts as a switch for incoming documents. Based on the filename, it will either:

1. Print the document directly to a specific printer
2. Open the document with the default application

Command Line Usage
~~~~~~~~~~~~~~~~~

The simplest way to use auto-print is from the command line:

.. code-block:: bash

    python -m auto_print.auto_print_execute path/to/your/file.pdf

Browser Integration
~~~~~~~~~~~~~~~~~

One of the most powerful features of auto-print is its ability to integrate with web browsers. This allows you to automatically route downloaded documents to the appropriate printer or application.

To set up browser integration:

1. Open the settings tab in your browser
2. Navigate to the file handling or download settings
3. Set auto-print as the default application for PDF files and other document types
4. Now when you download or open documents from the browser, they will be automatically processed by auto-print

Configuration
-------------

Before using auto-print, you need to configure it with your printer settings. The easiest way is to use the interactive configuration generator:

.. code-block:: bash

    python -m auto_print.auto_print_config_generator

This will guide you through setting up your printer configurations.

Configuration File Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The configuration is stored in a JSON file with the following structure:

.. code-block:: json

    {
      "InvoicePrinter": {
        "active": true,
        "printer": "FinancePrinter",
        "prefix": "INV_",
        "suffix": ".pdf",
        "print": true,
        "show": false
      },
      "ShippingLabels": {
        "active": true,
        "printer": "LabelPrinter",
        "prefix": "SHIP_",
        "suffix": ".pdf",
        "show": false,
        "print": true
      },
      "ViewOnly": {
        "active": true,
        "show": true,
        "print": false
      }
    }

Configuration Options:

* **active**: Whether this section is active (true/false)
* **printer**: The name of the printer to use (if omitted, uses default printer)
* **prefix**: The filename must start with this prefix (optional)
* **suffix**: The filename must end with this suffix (optional)
* **print**: Whether to print the document (true/false)
* **show**: Whether to open the document with the default application (true/false)

Document Routing Logic
---------------------

Auto-print uses the following logic to route documents:

1. The program receives a file path as an argument
2. It extracts the filename from the path
3. It compares the filename against each configuration section:
   - If both prefix and suffix match, the file is processed according to that section
   - If a prefix or suffix is not specified in a section, that part of the check is always considered a match
4. For the first matching section, the file is:
   - Printed directly to the specified printer if "print" is true
   - Opened with the default application if "show" is true
   - Both printed and shown if both are true

Example Scenarios
----------------

Here are some examples of how auto-print routes different files:

1. **File: INV_12345.pdf**
   - Matches the "InvoicePrinter" section
   - Printed directly to "FinancePrinter" without opening

2. **File: SHIP_label.pdf**
   - Matches the "ShippingLabels" section
   - Printed directly to "LabelPrinter" without opening

3. **File: Report.docx**
   - Doesn't match specific sections
   - Falls back to "ViewOnly" section
   - Opened with the default application (e.g., Microsoft Word) without printing

Logging
-------

Auto-print logs all actions to a log file (auto_print.log). This is useful for troubleshooting and auditing which documents were processed and how.

To enable logging in your code:

.. code-block:: python

    from auto_print.auto_print_execute import configure_logger, print_file

    # Set up logging
    configure_logger()

    # Print a file
    print_file("invoice_123.pdf")
