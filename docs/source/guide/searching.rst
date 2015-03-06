.. _searching:

Searching
=========

2D and 3D coordinates
---------------------

By default, compounds are returned with 2D coordinates. Use the ``record_type`` keyword argument to specify otherwise::

    pcp.get_compounds('Aspirin', 'name', record_type='3d')


Advanced search types
---------------------

By default, requests look for an exact match with the input. Alternatively, you can specify substructure,
superstructure, similarity and identity searches using the ``searchtype`` keyword argument::

    pcp.get_compounds('CC', searchtype='superstructure', listkey_count=3)

The ``listkey_count`` and ``listkey_start`` arguments can be used for pagination. Each ``searchtype`` has its own
options that can be specified as keyword arguments. For example, similarity searches have a ``Threshold``, and
super/substructure searches have ``MatchIsotopes``. A full list of options is available in the
`PUG REST Specification`_.

Note: These types of search are *slow*.


.. _`PUG REST Specification`: https://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html
