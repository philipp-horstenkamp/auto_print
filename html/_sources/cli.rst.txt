.. _cli:

Command Line Interface
======================

auto-print provides two command-line interfaces:

1. Configuration Generator: For setting up printer configurations
2. Print Executor: For printing files based on the configuration

.. _config-generator:

Configuration Generator
-----------------------

.. argparse::
   :module: auto_print.auto_print_config_generator
   :func: get_parser
   :prog: auto_print_config_generator

The configuration generator provides an interactive interface to create and manage printer configurations.

.. code-block:: bash

    python -m auto_print.auto_print_config_generator

Interactive Commands
~~~~~~~~~~~~~~~~~~~~

Once the configuration generator is running, you can use the following interactive commands:

* ``save`` or ``s``: Save the current configuration
* ``add`` or ``a``: Add a new printer section
* ``delete`` or ``d``: Delete a printer section
* ``repair`` or ``r``: Repair the configuration (fix invalid printer references)
* ``show``: Display the current configuration
* ``change``: Change the position of a section
* ``edit`` or ``e``: Edit a section
* ``close`` or ``c``: Close the application
* ``help`` or ``h``: Show help

.. _print-executor:

Print Executor
--------------

.. argparse::
   :module: auto_print.auto_print_execute
   :func: get_parser
   :prog: auto_print_execute

The print executor is used to print files based on the configuration.

.. code-block:: bash

    python -m auto_print.auto_print_execute <file_path>

Arguments:
    * ``file_path``: Path to the file to be printed

Process Flow
~~~~~~~~~~~~

When you run the print executor with a file path, it follows this process:

1. Checks if the file exists
2. Loads the printer configuration from ``%USERPROFILE%\auto-printer\auto-printer-config.json``
3. Extracts the filename from the path
4. Compares the filename against each configuration section:
   - If both prefix and suffix match, the file is processed according to that section
   - If a prefix or suffix is not specified in a section, that part of the check is always considered a match
5. For the first matching section, the file is:
   - Printed directly to the specified printer if "print" is true
   - Opened with the default application if "show" is true
   - Both printed and shown if both are true
6. If no matching section is found, an error is logged

Example:

.. code-block:: bash

    python -m auto_print.auto_print_execute invoice_123.pdf

This will print the file "invoice_123.pdf" to the appropriate printer based on your configuration.

Exit Codes
~~~~~~~~~~

The print executor returns the following exit codes:

* ``0``: Success
* ``-1``: No file to print specified
* ``-2``: Too many arguments
* ``-3``: File does not exist
* ``-4``: Error loading configuration
* ``-5``: Ghostscript not installed or other error
