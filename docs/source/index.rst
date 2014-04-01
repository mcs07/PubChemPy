.. PubChemPy documentation master file, created by
   sphinx-quickstart on Thu Jan 23 10:39:02 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PubChemPy documentation
=======================

PubChemPy provides a way to interact with PubChem in Python. It allows chemical searches by name,
substructure and similarity, chemical standardization, conversion between chemical file formats, depiction and
retrieval of chemical properties.

Here's a quick example showing how to search for a compound by name::

    for compound in get_compounds('glucose', 'name'):
        print compound.cid
        print compound.isomeric_smiles

Here's how you get calculated properties for a specific compound::

    vioxx = Compound.from_cid(5090)
    print vioxx.molecular_formula
    print vioxx.molecular_weight
    print vioxx.xlogp

All the heavy lifting is done by PubChem's servers, using their database and chemical toolkits.

Features
--------

- Search PubChem Substance and Compound databases by name, SMILES, InChI and SDF.
- Retrieve the standardised Compound record for a given input structure.
- Convert between SDF, SMILES, InChI, PubChem CID and more.
- Retrieve calculated properties, fingerprints and descriptors.
- Generate 2D and 3D coordinates.
- Get IUPAC systematic names, trade names and all known synonyms for a given Compound.
- Download compound records as XML, ASNT/B, JSON, SDF and depiction as a PNG image.
- Construct property tables using *pandas* DataFrames.
- A complete Python wrapper around the `PubChem PUG REST web service`_.
- Supports Python versions 2.7 – 3.4.

User guide
----------

A step-by-step guide to getting started with PubChemPy.

.. toctree::
   :maxdepth: 2

   guide/intro
   guide/install
   guide/gettingstarted
   guide/search
   guide/compound
   guide/substance
   guide/properties
   guide/pandas
   guide/download
   guide/advanced
   guide/contribute

API documentation
-----------------

Comprehensive API documentation with information on every function, class and method.

.. toctree::
   :maxdepth: 2

   api

.. _`PubChem PUG REST web service`: https://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST_Tutorial.html
