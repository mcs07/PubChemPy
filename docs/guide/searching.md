(searching)=

# Searching

PubChemPy provides powerful search capabilities that leverage PubChem's extensive chemical databases. Understanding the different search types and their performance characteristics can help you choose the most efficient approach for your needs.

By default, requests look for an exact match with the input. Alternatively, you can specify a search type using the `searchtype` parameter to perform chemical substructure, superstructure, similarity, or identity searches.

```python
pcp.get_compounds('CC', 'smiles', searchtype='superstructure', listkey_count=3)
```

The `listkey_count` and `listkey_start` arguments can be used for pagination. Each `searchtype` has its own options that can be specified as keyword arguments. For example, similarity searches have a `Threshold`, and super/substructure searches have `MatchIsotopes`. A full list of options is available in the [PUG REST Specification].

Note: These types of search are *slow*.

## Getting a full results list for common compound names

For some very common names, PubChem maintains a filtered whitelist of human-chosen CIDs with the intention of reducing confusion about which is the 'right' result. In the past, a search for Glucose would return four different results, each with different stereochemistry information. But now, a single result is returned, which has been chosen as 'correct' by the PubChem team.

Unfortunately it isn't directly possible to return to the previous behaviour, but there is a straightforward workaround: Search for Substances with that name (which are completely unfiltered) and then get the compounds that are derived from those substances.

There area a few different ways you can do this using PubChemPy, but the easiest is probably using the {func}`~pubchempy.get_cids` function:

> ```pycon
> >>> pcp.get_cids('2-nonenal', 'name', 'substance', list_return='flat')
> [17166, 5283335, 5354833]
> ```

This searches the substance database for '2-nonenal', and gets the CID for the compound associated with each substance. By default, this returns a mapping between each SID and CID, but the `list_return='flat'` parameter flattens this into just a single list of unique CIDs.

You can then use {meth}`~pubchempy.Compound.from_cid` to get the full {class}`~pubchempy.Compound` record, equivalent to what is returned by {func}`~pubchempy.get_compounds`:

> ```pycon
> >>> cids = pcp.get_cids('2-nonenal', 'name', 'substance', list_return='flat')
> >>> [pcp.Compound.from_cid(cid) for cid in cids]
> [Compound(17166), Compound(5283335), Compound(5354833)]
> ```

[pug rest specification]: https://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html
