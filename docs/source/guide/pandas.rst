.. _pandas:

*pandas* integration
====================

It is possible for ``get_compounds``, ``get_substances`` and ``get_properties`` to return a pandas DataFrame::

    df1 = pcp.get_compounds('C20H41Br', 'formula', as_dataframe=True)
    df2 = pcp.get_substances([1,2,3,4], as_dataframe=True)
    df3 = pcp.get_properties(['isomeric_smiles', 'xlogp', 'rotatable_bond_count'], 'C20H41Br', 'formula', as_dataframe=True)

An existing list of Compound objects can be converted into a dataframe, optionally specifying the desired columns::

    cs = pcp.get_compounds('C20H41Br', 'formula')
    df4 = pcp.compounds_to_frame(cs, properties=['isomeric_smiles', 'xlogp', 'rotatable_bond_count'])
