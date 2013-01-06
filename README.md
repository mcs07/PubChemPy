# PubChemPy

A Python interface for the [PubChem PUG REST service](http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html).

## Install



## Basic usage

To use PubChemPy in your Python script, just import it and make use of the functions and classes it provides.

    from pubchempy import *
    
    c = Compound.from_cid(1423)
    cs = get_compounds('Aspirin', 'name')



## Substances and compounds

If you what the record for a specific CID or SID:

By name, smiles, inchi, formula

record_type=2d or 3d

get_compounds
get_substances

Substructure / Superstructure / Similarity / Identity search - options for each

## Properties

get_properties

MolecularFormula,MolecularWeight,CanonicalSMILES,IsomericSMILES,InChI,InChIKey,IUPACName,XLogP,ExactMass,MonoisotopicMass,TPSA,Complexity,Charge,HBondDonorCount,HBondAcceptorCount,RotatableBondCount,HeavyAtomCount,IsotopeAtomCount,AtomStereoCount,DefinedAtomStereoCount,UndefinedAtomStereoCount,BondStereoCount,DefinedBondStereoCount,UndefinedBondStereoCount,CovalentUnitCount,Volume3D,XStericQuadrupole3D,YStericQuadrupole3D,ZStericQuadrupole3D,FeatureCount3D,FeatureAcceptorCount3D,FeatureDonorCount3D,FeatureAnionCount3D,FeatureCationCount3D,FeatureRingCount3D,FeatureHydrophobeCount3D,ConformerModelRMSD3D,EffectiveRotorCount3D,ConformerCount3D

## Synonyms

get_synonyms

## Identifier lists

get_cids
get_sids
get_aids

## Download

For PNG: image_size=large, small, WxH

## Assays


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


