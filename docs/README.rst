PubChemPy Documentation
=======================

This file provides a quick guide on how to compile the PubChemPy documentation.

You will find all the documentation source files in the ``docs/source`` directory, written in reStructuredText format.
All generated documentation is saved to the ``docs/build`` directory.

Requirements
------------

Sphinx is required to compile the documentation. Sphinx also requires docutils and jinja. Install them all using::

    pip install Sphinx

Compile the documentation
-------------------------

To compile the documentation and produce HTML output, run the following command from this ``docs`` directory::

    make html

Documentation will be generated in HTML format and saved to the ``build/html`` directory. Open the ``index.html`` file
in a browser to view it.

Reset
-----

To clear all generated documentation files and start over from scratch, run::

    make clean

This will not delete any of the source files.
