.. _compound:

Compound
========

The :func:`~pubchempy.get_compounds` function returns a list of :class:`~pubchempy.Compound` objects. You can also
instantiate a :class:`~pubchempy.Compound` object directly if you know its CID::

    c = pcp.Compound.from_cid(6819)


Dictionary representation
-------------------------

Each :class:`~pubchempy.Compound` has a ``record`` property, which is a dictionary that contains the all the information
about the compound, produced exactly from the JSON response from the PubChem API. All other properties are derived from
this record.

Additionally, each :class:`~pubchempy.Compound` provides a ``to_dict()`` method that returns PubChemPy's own dictionary
representation of the Compound data. As well as being more concisely formatted than the raw ``record``, this method also
takes an optional parameter to filter the list of the desired properties::


    >>> c = pcp.Compound.from_cid(962)
    >>> c.to_dict(properties=['atoms', 'bonds', 'inchi'])
    {'atoms': [{'aid': 1, 'element': 'o', 'x': 2.5369, 'y': -0.155},
               {'aid': 2, 'element': 'h', 'x': 3.0739, 'y': 0.155},
               {'aid': 3, 'element': 'h', 'x': 2, 'y': 0.155}],
     'bonds': [{'aid1': 1, 'aid2': 2, 'order': 'single'},
               {'aid1': 1, 'aid2': 3, 'order': 'single'}],
     'inchi': u'InChI=1S/H2O/h1H2'}

3D Compounds
------------

Many properties are missing from 3D records, and the following properties are *only* available on 3D records:

- ``volume_3d``
- ``multipoles_3d``
- ``conformer_rmsd_3d``
- ``effective_rotor_count_3d``
- ``pharmacophore_features_3d``
- ``mmff94_partial_charges_3d``
- ``mmff94_energy_3d``
- ``conformer_id_3d``
- ``shape_selfoverlap_3d``
- ``feature_selfoverlap_3d``
- ``shape_fingerprint_3d``
