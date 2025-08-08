(properties)=

# Properties

The {func}`~pubchempy.get_properties` function allows the retrieval of specific properties without having to deal with entire compound records. This is especially useful for retrieving the properties of a large number of compounds at once:

```python
p = pcp.get_properties("SMILES", "CC", "smiles", searchtype="superstructure")
```

Multiple properties may be specified in a list, or in a comma-separated string. The available properties are: MolecularFormula, MolecularWeight, ConnectivitySMILES, SMILES, InChI, InChIKey, IUPACName, XLogP, ExactMass, MonoisotopicMass, TPSA, Complexity, Charge, HBondDonorCount, HBondAcceptorCount, RotatableBondCount, HeavyAtomCount, IsotopeAtomCount, AtomStereoCount, DefinedAtomStereoCount, UndefinedAtomStereoCount, BondStereoCount, DefinedBondStereoCount, UndefinedBondStereoCount, CovalentUnitCount, Volume3D, XStericQuadrupole3D, YStericQuadrupole3D, ZStericQuadrupole3D, FeatureCount3D, FeatureAcceptorCount3D, FeatureDonorCount3D, FeatureAnionCount3D, FeatureCationCount3D, FeatureRingCount3D, FeatureHydrophobeCount3D, ConformerModelRMSD3D, EffectiveRotorCount3D, ConformerCount3D.

## Synonyms

Get a list of synonyms for a given input using the {func}`~pubchempy.get_synonyms` function:

```python
pcp.get_synonyms("Aspirin", "name")
pcp.get_synonyms("Aspirin", "name", "substance")
```

Inputs that match more than one SID/CID will have multiple, separate synonyms lists returned.

## CAS Registry Numbers

CAS Registry Numbers are not officially supported by PubChem, but they are often present in the synonyms associated with a compound. Therefore it is straightforward to retrieve them by filtering the synonyms to just those with the CAS Registry Number format:

```python
for result in pcp.get_synonyms("Aspirin", "name"):
    cid = result["CID"]
    cas_rns = []
    for syn in result.get("Synonym", []):
        match = re.match(r"(\d{2,7}-\d\d-\d)", syn)
        if match:
            cas_rns.append(match.group(1))
    print(f"CAS registry numbers for CID {cid}: {cas_rns}")
```

## Identifiers

There are three functions for getting a list of identifiers for a given input:

- {func}`~pubchempy.get_cids`
- {func}`~pubchempy.get_sids`
- {func}`~pubchempy.get_aids`

For example, passing a CID to {func}`~pubchempy.get_sids` will return a list of SIDs corresponding to the {class}`~pubchempy.Substance` records that were standardised and merged to produce the given {class}`~pubchempy.Compound`.
