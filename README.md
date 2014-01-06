# PubChemPy

A simple Python wrapper around the [PubChem PUG REST API](http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html).

## Installation

**Option 1**: Use [pip](http://www.pip-installer.org/en/latest/).

    pip install PubChemPy

**Option 2**: [Download the latest release](https://github.com/mcs07/PubChemPy/releases/) and install yourself:

    tar xzvf PubChemPy-1.0.1.tar.gz
    cd PubChemPy-1.0.1
    sudo python setup.py install

**Option 3**: [Download pubchempy.py](https://github.com/mcs07/PubChemPy/raw/master/pubchempy.py) and manually place it in your project directory or anywhere on your PYTHONPATH.

**Option 4**: Get the latest development version by cloning the Git repository.

    git clone https://github.com/mcs07/PubChemPy.git

## Basic usage

PubChemPy provides a variety of functions and classes that allow you to retrieve information from PubChem.

    from pubchempy import Compound, get_compounds
    
    comp = Compound.from_cid(1423)
    comps = get_compounds('Aspirin', 'name')

## Substances and compounds

The `get_substances` and `get_compounds` functions allow retrieval of PubChem Substance and Compound records. The functions take a wide variety of inputs, and return a list of results, even if only a single match was found.

For a specific CID or SID:

    get_compounds(1234)
    get_substances(4321)

A second `namespace` argument allows you to use different types of input:

    get_compounds('Aspirin', 'name')
    get_compounds('C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1', 'smiles')
    
Beware that line notation inputs like SMILES and InChI can return automatically generated records that aren't actually present in PubChem, and therefore have no CID or SID and are missing many properties.
    
By default, compounds are returned with 2D coordinates. Use the `record_type` keyword argument to specify otherwise:

    get_compounds('Aspirin', 'name', record_type='3d')
    
### Advanced search types

By default, requests look for an exact match with the input. Alternatively, you can specify substructure, superstructure, similarity and identity searches using the `searchtype` keyword argument:

    get_compounds('CC', searchtype='superstructure', listkey_count=3)
    
The `listkey_count` and `listkey_start` arguments can be used for pagination. Each `searchtype` has its own options that can be specified as keyword arguments. For example, similarity searches have a `Threshold`, and super/substructure searches have `MatchIsotopes`. A full list of options is available at the [PUG REST specification](http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html).

Note: These types of search are *slow*.

## The Compound class

The `get_compounds` function returns a list of `Compound` objects. You can also instantiate a `Compound` object from a CID:

    c = Compound.from_cid(6819)
    
Each `Compound` has a `record` property, which is a dictionary that contains the all the information about the compound. All other properties are derived from this record.

Compounds with regular 2D coordinates have the following properties: cid, record, atoms, bonds, elements, synonyms, sids, aids, coordinate_type, charge, molecular_formula, molecular_weight, canonical_smiles, isomeric_smiles, inchi, inchikey, iupac_name, xlogp, exact_mass, monoisotopic_mass, tpsa, complexity, h_bond_donor_count, h_bond_acceptor_count, rotatable_bond_count, fingerprint, heavy_atom_count, isotope_atom_count, atom_stereo_count, defined_atom_stereo_count, undefined_atom_stereo_count, bond_stereo_count, defined_bond_stereo_count, undefined_bond_stereo_count, covalent_unit_count.

Many of the above properties are missing from 3D records, however they do have the following additional properties: volume_3d, multipoles_3d, conformer_rmsd_3d, effective_rotor_count_3d, pharmacophore_features_3d, mmff94_partial_charges_3d, mmff94_energy_3d, conformer_id_3d, shape_selfoverlap_3d, feature_selfoverlap_3d, shape_fingerprint_3d.

## Properties

The `get_properties` function allows the retrieval of specific properties without having to deal with entire compound records. This is especially useful for retrieving the properties of a large number of compounds at once.

    p = get_properties('IsomericSMILES', 'CC', 'smiles', searchtype='superstructure')

Multiple properties may be specified in a list, or in a comma-separated string. The available properties are: MolecularFormula,MolecularWeight, CanonicalSMILES, IsomericSMILES, InChI, InChIKey, IUPACName, XLogP, ExactMass, MonoisotopicMass, TPSA, Complexity, Charge, HBondDonorCount, HBondAcceptorCount, RotatableBondCount, HeavyAtomCount, IsotopeAtomCount, AtomStereoCount, DefinedAtomStereoCount, UndefinedAtomStereoCount, BondStereoCount, DefinedBondStereoCount, UndefinedBondStereoCount, CovalentUnitCount, Volume3D, XStericQuadrupole3D, YStericQuadrupole3D, ZStericQuadrupole3D, FeatureCount3D, FeatureAcceptorCount3D, FeatureDonorCount3D, FeatureAnionCount3D, FeatureCationCount3D, FeatureRingCount3D, FeatureHydrophobeCount3D, ConformerModelRMSD3D, EffectiveRotorCount3D, ConformerCount3D.

## Synonyms

Get a list of synonyms for a given input using the `get_synonyms` function:

    get_synonyms('Aspirin', 'name')
    get_synonyms('Aspirin', 'name', 'substance')
    
Inputs that match more than one SID/CID will have multiple, separate synonyms lists returned.

## Identifier lists

There are three functions for getting a list of identifiers for a given input:

- get_cids
- get_sids
- get_aids

For example, passing a CID to get_sids will return a list of SIDs corresponding to the Substance records that were standardised and merged to produce the given Compound.

## Download

The download function is for saving a file to disk. The following formats are available: XML, ASNT/B, JSON, SDF, CSV, PNG, TXT. Beware that not all formats are available for all types of information. SDF and PNG are only available for full Compound and Substance records, and CSV is best suited to tables of properties and identifiers.

Examples:

    download('PNG', 'asp.png', 'Aspirin', 'name')
    download('CSV', 's.csv', [1,2,3], operation='property/CanonicalSMILES,IsomericSMILES')

For PNG images, the `image_size` argument can be used to specfiy `large`, `small` or `<width>x<height>`.

## The Substance class

This class has the following properties: sid, synonyms, source_name, source_id, cids, aids, deposited_compound and standardized_compound.

The deposited_compound is a Compound object that corresponds to the deposited Substance record. The standardized_compound is the corresponding record in the Compound database.

## Assays

TODO

## Custom requests

If you wish to perform more complicated requests, you can use the `request` function. This is an extremely simple wrapper around the REST API that allows you to construct any sort of request from a few parameters. The [PUG REST specification](http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html) has all the information you will need to formulate your requests.

The `request` function simply returns the exact response from the PubChem server as a string. This can be parsed in different ways depending on the output format you choose. See the Python [json](http://docs.python.org/2/library/json.html), [xml](http://docs.python.org/2/library/xml.etree.elementtree.html) and [csv](http://docs.python.org/2/library/csv.html) packages for more information. Additionally, cheminformatics toolkits such as [Open Babel](http://openbabel.org/docs/current/UseTheLibrary/Python.html) and [RDKit](http://www.rdkit.org) offer tools for handling SDF files in Python.

The `get` function is very similar to the `request` function, except it handles `listkey` type responses automatically for you. This makes things simpler, however it means you can't take advantage of using the same `listkey` repeatedly to obtain different types of information. See the [PUG REST specification](http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html) for more information on how `listkey` responses work.

### Summary of possible inputs

    <identifier> = list of cid, sid, aid, source, inchikey, listkey; string of name, smiles, xref, inchi, sdf;
    <domain> = substance | compound | assay

    compound domain
    <namespace> = cid | name | smiles | inchi | sdf | inchikey | <structure search> | <xref> | listkey | formula
    <operation> = record | property/[comma-separated list of property tags] | synonyms | sids | cids | aids | assaysummary | classification

    substance domain
    <namespace> = sid | sourceid/<source name> | sourceall/<source name> | name | <xref> | listkey
    <operation> = record | synonyms | sids | cids | aids | assaysummary | classification

    assay domain
    <namespace> = aid | listkey | type/<assay type> | sourceall/<source name>
    <assay type> = all | confirmatory | doseresponse | onhold | panel | rnai | screening | summary
    <operation> = record | aids | sids | cids | description | targets/{ProteinGI, ProteinName, GeneID, GeneSymbol} | doseresponse/sid

    <structure search> = {substructure | superstructure | similarity | identity}/{smiles | inchi | sdf | cid}
    <xref> = xref/{RegistryID | RN | PubMedID | MMDBID | ProteinGI | NucleotideGI | TaxonomyID | MIMID | GeneID | ProbeID | PatentID}
    <output> = XML | ASNT | ASNB | JSON | JSONP [ ?callback=<callback name> ] | SDF | CSV | PNG | TXT


## Avoiding TimeoutError

If there are too many results for a request, you will receive a TimeoutError. There are different ways to avoid this, depending on what type of request you are doing. 

If retrieving full compound or substance records, instead request a list cids or sids for your input, and then request the full records for those identifiers individually or in small groups. For example:

	sids = get_sids('Aspirin', 'name')
	for sid in sids:
		s = Substance.from_sid(sid)

When using the `formula` namespace or a `searchtype`, you can also alternatively use the `listkey_count` and `listkey_start` keyword arguments to specify pagination. For example:

	get_compounds('CC', 'smiles', searchtype='substructure', listkey_count=5)
	get('C10H21N', 'formula', listkey_count=3, listkey_start=6)


