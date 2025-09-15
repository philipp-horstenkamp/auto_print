Usage
=====

Basic Usage
-----------

Auto Print routes documents based on filename patterns. It can:

1. Print the document directly to a specific printer
2. Open the document with the default application
3. Do both actions simultaneously

Command Line Usage
~~~~~~~~~~~~~~~~~~

Auto Print can be used from the command line. For detailed information about command-line usage, see the :ref:`cli` section.

Browser Integration
~~~~~~~~~~~~~~~~~~~

Auto Print proides you the ability to integrate with web browsers, allowing you to automatically route downloaded PDF documents to printers or your default application.
-co
To set up browser integration:

1. Open the settings tab in your browser
2. Navigate to the file handling or download settings
3. Set auto-print as the default application for PDF files
4. Now when you download or open documents from the browser, they will be automatically processed

.. image:: assets/Settings.PNG
   :width: 400
   :alt: Browser Settings

.. image:: assets/ChoosePrinter.PNG
   :width: 400
   :alt: Choose Auto Print

Configuration
-------------

Before using Auto Print, configure it with your printer settings using the interactive configuration generator:

.. code-block:: bash

    # If installed via MSI
    auto-print-config

    # If running from source
    python -m auto_print.auto_print_config_generator

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

For detailed CLI commands to manage configuration, see the :ref:`cli` section.

Document Routing Logic
----------------------

Auto Print uses the following logic to route documents:

1. The program receives a file path as an argument
2. It extracts the filename from the path
3. It compares the filename against each configuration section in order:
   - If both prefix and suffix match, the file is processed according to that section
   - If a prefix or suffix is not specified in a section, that part is always considered a match
4. For the first matching section, the file is:
   - Printed directly to the specified printer if "print" is true
   - Opened with the default application if "show" is true
   - Both printed and shown if both are true

Example Scenarios
-----------------

Here are some examples of how Auto Print routes different files:

1. **File: INV_12345.pdf**
   - Matches the "InvoicePrinter" section
   - Printed directly to "FinancePrinter" without opening

2. **File: SHIP_label.pdf**
   - Matches the "ShippingLabels" section
   - Printed directly to "LabelPrinter" without opening

3. **File: Report.pdf**
   - Doesn't match specific sections
   - Falls back to "ViewOnly" section
   - Opened with the default application without printing

Logging
-------

Auto Print logs all actions to a log file for troubleshooting and auditing. The log file is located at:

.. code-block::

    %USERPROFILE%\auto-printer\auto_print.log
