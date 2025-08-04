# PubChemPy

[![PyPI Version](https://img.shields.io/pypi/v/PubChemPy.svg?style=flat)](https://pypi.python.org/pypi/PubChemPy)
[![License](https://img.shields.io/pypi/l/PubChemPy.svg?style=flat)](https://github.com/mcs07/PubChemPy/blob/main/LICENSE)

PubChemPy provides a way to interact with PubChem in Python. It allows chemical searches by name, substructure and
similarity, chemical standardization, conversion between chemical file formats, depiction and retrieval of chemical
properties.

```python
>>> from pubchempy import get_compounds, Compound
>>> comp = Compound.from_cid(1423)
>>> print(comp.smiles)
CCCCCCCNC1CCCC1CCCCCCC(=O)O
>>> comps = get_compounds('Aspirin', 'name')
>>> print(comps[0].xlogp)
1.2
```

## Installation

Install PubChemPy using:

```shell
pip install pubchempy
```

Alternatively, try one of the other [installation options](https://pubchempy.readthedocs.io/en/latest/guide/install.html).

## Documentation

Full documentation is available at https://pubchempy.readthedocs.io.

## Contribute

- Feature ideas and bug reports are welcome on the [Issue Tracker](https://github.com/mcs07/PubChemPy/issues).
- Fork the [source code](https://github.com/mcs07/PubChemPy) on GitHub, make changes and file a pull request.

## License

PubChemPy is licensed under the [MIT license](https://github.com/mcs07/PubChemPy/blob/main/LICENSE).
