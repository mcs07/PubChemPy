.. _install:

Installation
============

PubChemPy supports Python versions 3.9+. There are no required dependencies.

There are a variety of ways to download and install PubChemPy.

Option 1: Use pip (recommended)
-------------------------------

The easiest and recommended way to install is using pip, the package installer for
Python. It comes included with most modern Python distrubtions and you can use it to
install packages from the `Python Package Index`_. Install PubChemPy using pip by
running the following command in your terminal or command prompt::

    pip install pubchempy

This will download the latest version of PubChemPy, and place it in your `site-packages`
folder so it is automatically available to all your python scripts.

If pip is missing from your Python distribution, you can `install it by following the
official guide`_.

Option 2: Use conda
-------------------

Conda is a cross-platform package manager that is popular in the scientific Python
community. It provides an alternative to pip for installing Python packages and managing
environments. Conda can be installed using the `Miniforge`_ installer, which is free and
open-source, or the `Anaconda`_ installer, which is a commercial distribution that
includes many scientific packages by default. Once you have conda installed, you can
install PubChmePy from the conda-forge channel with the following command::

    conda install -c conda-forge pubchempy

The conda-forge channel is a community-driven collection of conda packages that provides
up-to-date and well-maintained packages for the conda package manager.

Option 3: Clone the repository
------------------------------

The latest development version of PubChemPy is always `available on GitHub`_. This
version is not guaranteed to be stable, but may include new features that have not yet
been released. Simply clone the repository and install as usual::

    git clone https://github.com/mcs07/PubChemPy.git
    cd PubChemPy
    pip install .

.. _`Python Package Index`: https://pypi.org/
.. _`install it by following the official guide`: https://pip.pypa.io/en/stable/installation/
.. _`Miniforge`: https://conda-forge.org/download/
.. _`Anaconda`: https://www.anaconda.com/download
.. _`download the latest release`: https://github.com/mcs07/PubChemPy/releases/
.. _`available on GitHub`: https://github.com/mcs07/PubChemPy
