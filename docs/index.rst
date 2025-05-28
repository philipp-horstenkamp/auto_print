.. auto-print documentation master file

Welcome to auto-print's documentation!
=========================================

Auto-print is a document routing application that automatically decides whether to print documents directly or open them with the default application based on filename patterns.

How it works
------------

1. The program is started with a filepath as an argument
2. The filename gets extracted
3. The filename is compared to a list of configured suffixes and prefixes
4. If suffix and prefix match, the file gets processed according to the configuration
5. The file is then either printed directly and/or shown in the default application

Key Features
------------

* Route documents to specific printers based on filename patterns
* Configure whether to print directly or open with default application
* Easily integrate with browsers as the default PDF handler
* Simple configuration through an interactive interface

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   cli
   modules/index
   contributing

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
