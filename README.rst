PubChemPy
=========

PubChemPy provides a way to interact with PubChem in Python. It allows chemical searches by name, substructure and
similarity, chemical standardization, conversion between chemical file formats, depiction and retrieval of chemical
properties.

::

    from pubchempy import get_compounds, Compound

    comp = Compound.from_cid(1423)
    print comp.isomeric_smiles

    comps = get_compounds('Aspirin', 'name')
    print comps[0].xlogp

Installation
------------

Install PubChemPy using:

::

    pip install pubchempy

Alternatively, try one of the other `installation options`_.

Documentation
-------------

Full documentation is available at http://pubchempy.readthedocs.org.

Contribute
----------

-  Feature ideas and bug reports are welcome on the `Issue Tracker`_.
-  Fork the `source code`_ on GitHub, make changes and file a pull request.

License
-------

PubChemPy is licensed under the `MIT license`_.

.. _`installation options`: http://pubchempy.readthedocs.org/en/latest/guide/install.html
.. _`source code`: https://github.com/mcs07/PubChemPy
.. _`Issue Tracker`: https://github.com/mcs07/PubChemPy/issues
.. _`MIT license`: https://github.com/mcs07/PubChemPy/blob/master/LICENSE
