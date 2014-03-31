.. _gettingstarted:

Getting started
===============

This page gives a introduction on how to get started with PubChemPy. This assumes you already have PubChemPy
:ref:`installed <install>`.

Retrieving a Compound
---------------------

Retrieving information about a specific Compound in the PubChem database is simple.

Begin by importing PubChemPy::

    >>> import pubchempy as pcp

Let's get the Compound with `CID 5090`_::

    >>> c = pcp.Compound.from_cid(5090)

Now we have a :class:`~pubchempy.Compound` object called ``c``. We can get all the information we need from this
object::

    >>> print c.molecular_formula
    C17H14O4S
    >>> print c.molecular_weight
    314.35566
    >>> print c.isomeric_smiles
    CS(=O)(=O)C1=CC=C(C=C1)C2=C(C(=O)OC2)C3=CC=CC=C3
    >>> print c.xlogp
    2.3
    >>> print c.iupac_name
    3-(4-methylsulfonylphenyl)-4-phenyl-2H-furan-5-one
    >>> print c.synonyms
    [u'rofecoxib', u'Vioxx', u'Ceoxx', u'162011-90-7', u'MK 966', ... ]

.. note::

   All the code examples in this documentation will assume you have imported PubChemPy as `pcp`. If you prefer, you can
   alternatively import specific functions and classes by name and use them directly::

       from pubchempy import Compound, get_compounds
       c = Compound.from_cid(1423)
       cs = get_compounds('Aspirin', 'name')

Searching
---------

What if you don't know the PubChem CID of the Compound you want? Just use the :func:`~pubchempy.get_compounds`
function::

    >>> results = pcp.get_compounds('Glucose', 'name')
    >>> print results
    [Compound(79025), Compound(5793), Compound(64689), Compound(206)]

The first argument is the identifier, and the second argument is the identifier type, which must be one of ``name``,
``smiles``, ``sdf``, ``inchi``, ``inchikey`` or ``formula``. It looks like there are 4 compounds in the PubChem
Database that have the name Glucose associated with them. Let's take a look at them in more detail::

    >>> for compound in results:
    ...    print compound.isomeric_smiles
    C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O
    C([C@@H]1[C@H]([C@@H]([C@H](C(O1)O)O)O)O)O
    C([C@@H]1[C@H]([C@@H]([C@H]([C@@H](O1)O)O)O)O)O
    C(C1C(C(C(C(O1)O)O)O)O)O

It looks like they all have different stereochemistry information.

Retrieving the record for a SMILES string is just as easy::

    >>> pcp.get_compounds('C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1', 'smiles')
    [Compound(1318)]

.. note::

   Beware that line notation inputs like SMILES and InChI can return automatically generated records that aren't
   actually present in PubChem, and therefore have no CID and are missing many properties that are too complicated to
   calculate on the fly.

That's all the most basic things you can do with PubChemPy. Read on for more some more advanced usage examples.

.. _`CID 5090`: https://pubchem.ncbi.nlm.nih.gov/summary/summary.cgi?cid=5090
