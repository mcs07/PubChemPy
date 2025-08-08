(gettingstarted)=

# Getting started

This page gives a introduction on how to get started with PubChemPy. This assumes you already have PubChemPy {ref}`installed <install>`.

## Retrieving a Compound

Retrieving information about a specific Compound in the PubChem database is simple.

Begin by importing PubChemPy:

```pycon
>>> import pubchempy as pcp
```

Let's get the {class}`~pubchempy.Compound` with [CID 5090]:

```pycon
>>> c = pcp.Compound.from_cid(5090)
```

Now we have a {class}`~pubchempy.Compound` object called `c`. We can get all the information we need from this object:

```pycon
>>> print(c.molecular_formula)
C17H14O4S
>>> print(c.molecular_weight)
314.4
>>> print(c.smiles)
CS(=O)(=O)C1=CC=C(C=C1)C2=C(C(=O)OC2)C3=CC=CC=C3
>>> print(c.xlogp)
2.3
>>> print(c.iupac_name)
3-(4-methylsulfonylphenyl)-4-phenyl-2H-furan-5-one
>>> print(c.synonyms)
['rofecoxib', 'Vioxx', 'Ceoxx', '162011-90-7', 'MK 966', ... ]
```

````{note}
All the code examples in this documentation will assume you have imported PubChemPy as `pcp`. If you prefer, you can alternatively import specific functions and classes by name and use them directly:

```python
from pubchempy import Compound, get_compounds
c = Compound.from_cid(1423)
cs = get_compounds("Aspirin", "name")
```
````

## Searching

What if you don't know the PubChem CID of the Compound you want? Just use the {func}`~pubchempy.get_compounds` function, for example with a compound name input:

```pycon
>>> results = pcp.get_compounds("Glucose", "name")
>>> print(results)
[Compound(5793)]
```

The first argument is the identifier, and the second argument is the identifier type, which must be one of `name`, `smiles`, `sdf`, `inchi`, `inchikey` or `formula`. More often than not, only a single result will be returned, but sometimes there are multiple results for a given identifier. Therefore, {func}`~pubchempy.get_compounds` returns a list of {class}`~pubchempy.Compound` objects (even if there is only one result).

It is possible to iterate over this list to get the individual {class}`~pubchempy.Compound` objects:

```pycon
>>> for compound in results:
...    print(compound.smiles)
C([C@@H]1[C@H]([C@@H]([C@H](C(O1)O)O)O)O)O
```

Or you can access the first result directly:

```pycon
>>> compound = results[0]
>>> print(compound.smiles)
C([C@@H]1[C@H]([C@@H]([C@H](C(O1)O)O)O)O)O
```

Retrieving the compound record(s) for a SMILES input is just as easy:

```pycon
>>> pcp.get_compounds("C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1", "smiles")
[Compound(1318)]
```

```{note}
Beware that line notation inputs like SMILES and InChI can return automatically generated records that aren't actually present in PubChem, and therefore have no CID and are missing many properties that are too complicated to calculate on the fly.
```

That's all the most basic things you can do with PubChemPy. Read on for more some more advanced usage examples.

[cid 5090]: https://pubchem.ncbi.nlm.nih.gov/summary/summary.cgi?cid=5090
