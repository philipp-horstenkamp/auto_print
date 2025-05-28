Contributing
============

Thank you for considering contributing to auto-print! This document provides guidelines for contributing to the project.

Development Setup
-----------------

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/philipp-horstenkamp/auto-print.git
       cd auto-print

2. Install development dependencies:

   .. code-block:: bash

       poetry install

3. Set up pre-commit hooks:

   .. code-block:: bash

       pre-commit install

Code Style
----------

This project uses:

* |ruff| for linting and formatting
* |mypy| for type checking

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff

.. |mypy| image:: https://img.shields.io/badge/mypy-checked-blue
   :target: https://mypy-lang.org/
   :alt: MyPy

You can run these tools using pre-commit:

.. code-block:: bash

    pre-commit run --all-files

Testing
-------

Run tests using pytest:

.. code-block:: bash

    poetry run pytest

Documentation
-------------

To build the documentation:

.. code-block:: bash

    cd docs
    make html

For the German translation:

.. code-block:: bash

    cd docs
    make gettext
    sphinx-intl update -p _build/gettext -l de
    # Edit the .po files in locale/de/LC_MESSAGES/
    make -e SPHINXOPTS="-D language='de'" html

Pull Request Process
--------------------

1. Create a new branch for your feature or bugfix
2. Make your changes
3. Run tests and linting
4. Submit a pull request
5. Ensure CI checks pass
