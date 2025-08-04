# PubChemPy documentation

PubChemPy provides a way to interact with the PubChem database in Python, via the PUG REST API. PubChem is a comprehensive chemical information resource that contains millions of chemical structures and their associated biological, physical, and toxicological data.

This package handles the complexity of the PubChem PUG REST API, providing a simple Pythonic interface for chemical informatics workflows. It allows retrieval of chemical structures, properties, and experimental data, including molecular descriptors, fingerprints, 3D conformer data, and biological assay results. It also enables chemical searches by name, substructure and similarity, conversion between different chemical formats, chemical standardization, and depiction.

Here's a quick example showing how to get calculated properties for a specific compound:

```python
>>> import pubchempy as pcp
>>> compound = pcp.Compound.from_cid(2244)  # Aspirin
>>> print(compound.molecular_formula)
C9H8O4
>>> print(compound.iupac_name)
2-acetyloxybenzoic acid
>>> print(compound.molecular_weight)
180.16
>>> print(compound.xlogp)
1.2
```

Here's how to search for a compound by name:

```python
>>> for compound in pcp.get_compounds('glucose', 'name'):
...     print(compound.cid)
...     print(compound.smiles)
...
5793
C([C@@H]1[C@H]([C@@H]([C@H](C(O1)O)O)O)O)O
```

All the heavy lifting is done by PubChem's servers, using their database and chemical toolkits.

## Features

- Search PubChem Substance and Compound databases by name, SMILES, InChI and SDF.
- Retrieve the standardised Compound record for a given input structure.
- Convert between SDF, SMILES, InChI, PubChem CID and more.
- Retrieve calculated properties, fingerprints and descriptors.
- Generate 2D and 3D coordinates.
- Get IUPAC systematic names, trade names and all known synonyms for a given Compound.
- Download compound records as XML, ASNT/B, JSON, SDF and depiction as a PNG image.
- Construct property tables using *pandas* DataFrames.
- A complete Python wrapper around the [PubChem PUG REST web service].
- Supports Python versions 3.9+.

## Useful links

- Source code is available on [GitHub].
- Ask a question or report a bug on the [Issue Tracker].
- PUG REST API [tutorial] and [documentation].

## User guide

A step-by-step guide to getting started with PubChemPy.

```{toctree}
:maxdepth: 2

guide/introduction
guide/install
guide/gettingstarted
guide/searching
guide/compound
guide/substance
guide/properties
guide/pandas
guide/download
guide/advanced
guide/contribute
```

## API documentation

Comprehensive API documentation with information on every function, class and method.

```{toctree}
:maxdepth: 2

api
```

[documentation]: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
[GitHub]: https://github.com/mcs07/PubChemPy
[Issue Tracker]: https://github.com/mcs07/PubChemPy/issues
[PubChem PUG REST web service]: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
[tutorial]: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest-tutorial
