# PubChemPy

[![PyPI Version](https://img.shields.io/pypi/v/PubChemPy.svg?style=flat)](https://pypi.python.org/pypi/PubChemPy)
![Conda Version](https://img.shields.io/conda/vn/conda-forge/pubchempy)
[![License](https://img.shields.io/pypi/l/PubChemPy.svg?style=flat)](https://github.com/mcs07/PubChemPy/blob/main/LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.541438.svg)](https://doi.org/10.5281/zenodo.593126)
[![Tests](https://github.com/mcs07/PubChemPy/actions/workflows/test.yml/badge.svg)](https://github.com/mcs07/PubChemPy/actions/workflows/test.yml)

PubChemPy provides a way to interact with PubChem in Python. It allows chemical searches by name, substructure and similarity, chemical standardization, conversion between chemical file formats, depiction and retrieval of chemical properties.

## Installation

Install PubChemPy with pip:

```shell
pip install pubchempy
```

Or with conda:

```shell
conda install -c conda-forge pubchempy
```

For detailed instructions, see the [installation guide](https://docs.pubchempy.org/en/latest/guide/install.html).

## Example usage

Retrieve a compound by its PubChem Compound Identifier (CID) and print its SMILES and IUPAC name:

```pycon
>>> import pubchempy as pcp
>>> comp = pcp.Compound.from_cid(1423)
>>> print(comp.smiles)
CCCCCCCNC1CCCC1CCCCCCC(=O)O
>>> print(comp.iupac_name)
7-[2-(heptylamino)cyclopentyl]heptanoic acid
```

Search compounds by name and print the SMILES and molecular weight of the first result:

```pycon
>>> results = pcp.get_compounds("Aspirin", "name")
>>> print(results[0].smiles)
CC(=O)OC1=CC=CC=C1C(=O)O
>>> print(results[0].molecular_weight)
180.16
```

## Documentation

Full documentation is available at <https://docs.pubchempy.org>.

This includes a [step-by-step guide on how to use PubChemPy](https://docs.pubchempy.org/en/latest/guide/gettingstarted.html), as well as a [complete API reference](https://docs.pubchempy.org/en/latest/api.html).

## Contributing

- Feature ideas and bug reports are welcome on the [Issue Tracker](https://github.com/mcs07/PubChemPy/issues).
- Fork the [source code](https://github.com/mcs07/PubChemPy) on GitHub, make changes and file a pull request.

## License

PubChemPy is licensed under the [MIT license](https://github.com/mcs07/PubChemPy/blob/main/LICENSE).
