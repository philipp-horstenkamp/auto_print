Command Line Interface
======================

Overview
--------

**Auto Print** provides two main command-line tools:

#. **Configuration Generator** – Interactive tool for setting up printing rules
#. **Print Executor** – Command-line tool to apply those rules to files

.. note::

   If installed via the MSI installer:

   - Use ``auto-print.exe`` to print files (also available in the right-click context menu for PDF files)
   - Use ``auto-print-config.exe`` or launch **Auto Print Config** from the Start Menu to configure rules

Configuration
-------------

The configuration file is stored at:

::

    %USERPROFILE%\auto-printer\auto-printer-config.json

For details about the configuration file structure, see the :ref:`Configuration File Structure <configuration-file-structure>` section in the usage documentation.

Configuration Generator Commands
--------------------------------

.. argparse::
   :module: auto_print.auto_print_config_generator
   :func: get_parser
   :prog: auto_print_config_generator

The configuration generator provides an interactive interface with the following commands:

+----------+--------+------------------------------------------------+
| Command  | Short  | Description                                    |
+==========+========+================================================+
| save     | s      | Save the configuration                         |
+----------+--------+------------------------------------------------+
| close    | c      | Close the config tool                          |
+----------+--------+------------------------------------------------+
| add      | a      | Add a config section                           |
+----------+--------+------------------------------------------------+
| delete   | d      | Remove a section                               |
+----------+--------+------------------------------------------------+
| show     | s      | Display the config                             |
+----------+--------+------------------------------------------------+
| change   |        | Reorder sections                               |
+----------+--------+------------------------------------------------+
| edit     | e      | Edit section content                           |
+----------+--------+------------------------------------------------+
| help     | h      | Display help                                   |
+----------+--------+------------------------------------------------+
| repair   | r      | Validate printer availability                  |
+----------+--------+------------------------------------------------+

Configuration Workflow
~~~~~~~~~~~~~~~~~~~~~~

The configuration workflow follows these steps:

1. Launch the generator (via CLI or GUI)
2. Use the commands listed above to create and manage configuration sections
3. Use ``save`` to persist changes
4. Exit with ``close``

For details about configuration options and matching rules, see the :ref:`Configuration File Structure <configuration-file-structure>` and :ref:`Document Routing Logic <document-routing-logic>` sections in the usage documentation.

Print Executor
--------------

.. argparse::
   :module: auto_print.auto_print_execute
   :func: get_parser
   :prog: auto_print_execute

Usage
~~~~~

**From MSI installer:**

::

    auto-print.exe <file_path>

**From source (Python):**

::

    python -m auto_print.auto_print_execute <file_path>

Execution Workflow
~~~~~~~~~~~~~~~~~~

The print executor:

1. Confirms the file exists
2. Loads the configuration file
3. Processes the file according to the document routing logic

For detailed information about how files are matched and processed, see the :ref:`Document Routing Logic <document-routing-logic>` section in the usage documentation.

Example
~~~~~~~

::

    auto-print.exe invoice_123.pdf

This processes the file based on the matching configuration section.

Exit Codes
~~~~~~~~~~

- ``0``: Success
- ``-1``: No file specified
- ``-2``: Too many arguments
- ``-3``: File not found
- ``-4``: Failed to load configuration
- ``-5``: Ghostscript not found or other runtime error
