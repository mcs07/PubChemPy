.. _install:

Installation
============

PubChemPy supports Python versions 2.7, 3.5, and 3.6. There are no other dependencies.

There are a variety of ways to download and install PubChemPy.

Option 1: Use pip (recommended)
-------------------------------

The easiest and recommended way to install is using pip::

    pip install pubchempy

This will download the latest version of PubChemPy, and place it in your `site-packages` folder so it is automatically
available to all your python scripts.

If you don't already have pip installed, you can `install it using get-pip.py`_::

       curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
       python get-pip.py

Option 2: Use conda
-------------------

If you use `Anaconda Python`_, install with conda::

    conda install -c mcs07 pubchempy

Option 3: Download the latest release
-------------------------------------

Alternatively, `download the latest release`_ manually and install yourself::

    tar -xzvf PubChemPy-1.0.4.tar.gz
    cd PubChemPy-1.0.4
    python setup.py install

The setup.py command will install PubChemPy in your `site-packages` folder so it is automatically available to all your
python scripts. Instead, you may prefer to just copy the pubchempy.py file into the desired project directory to only
make it available to that project.

Option 4: Clone the repository
------------------------------

The latest development version of PubChemPy is always `available on GitHub`_. This version is not guaranteed to be
stable, but may include new features that have not yet been released. Simply clone the repository and install as usual::

    git clone https://github.com/mcs07/PubChemPy.git
    cd PubChemPy
    python setup.py install

.. _`install it using get-pip.py`: http://www.pip-installer.org/en/latest/installing.html
.. _`Anaconda Python`: https://www.continuum.io/anaconda-overview
.. _`download the latest release`: https://github.com/mcs07/PubChemPy/releases/
.. _`available on GitHub`: https://github.com/mcs07/PubChemPy
