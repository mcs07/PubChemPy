.. _compound:

Compound
========

The ``get_compounds`` function returns a list of ``Compound`` objects. You can also instantiate a `Compound` object from
a CID::

    c = pcp.Compound.from_cid(6819)

Each ``Compound`` has a ``record`` property, which is a dictionary that contains the all the information about the
compound. All other properties are derived from this record.

Compounds with regular 2D coordinates have the following properties: cid, record, atoms, bonds, elements, synonyms,
sids, aids, coordinate_type, charge, molecular_formula, molecular_weight, canonical_smiles, isomeric_smiles, inchi,
inchikey, iupac_name, xlogp, exact_mass, monoisotopic_mass, tpsa, complexity, h_bond_donor_count, h_bond_acceptor_count,
rotatable_bond_count, fingerprint, heavy_atom_count, isotope_atom_count, atom_stereo_count, defined_atom_stereo_count,
undefined_atom_stereo_count, bond_stereo_count, defined_bond_stereo_count, undefined_bond_stereo_count,
covalent_unit_count.

Many of the above properties are missing from 3D records, however they do have the following additional properties:
volume_3d, multipoles_3d, conformer_rmsd_3d, effective_rotor_count_3d, pharmacophore_features_3d,
mmff94_partial_charges_3d, mmff94_energy_3d, conformer_id_3d, shape_selfoverlap_3d, feature_selfoverlap_3d,
shape_fingerprint_3d.

