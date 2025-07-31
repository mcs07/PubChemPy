.. _api:

API documentation
=================

.. module:: pubchempy

This part of the documentation is automatically generated from the PubChemPy source code and comments.

Search functions
----------------


.. autofunction:: get_compounds
.. autofunction:: get_substances
.. autofunction:: get_assays
.. autofunction:: get_properties
.. autofunction:: get_synonyms

Identifiers
-----------

.. autofunction:: get_cids
.. autofunction:: get_sids
.. autofunction:: get_aids

Request functions
-----------------

.. autofunction:: download
.. autofunction:: request
.. autofunction:: get
.. autofunction:: get_json
.. autofunction:: get_sdf

Compound
--------

.. autoclass:: pubchempy.Compound
   :members:

Atom
----

.. autoclass:: pubchempy.Atom
   :members:

Bond
----

.. autoclass:: pubchempy.Bond
   :members:

Substance
---------

.. autoclass:: pubchempy.Substance
   :members:

Assay
-----

.. autoclass:: pubchempy.Assay
   :members:

*pandas* functions
------------------

Each of the search functions, :func:`~pubchempy.get_compounds`, :func:`~pubchempy.get_substances` and
:func:`~pubchempy.get_properties` has an ``as_dataframe`` parameter. When set to ``True``, these functions automatically
extract properties from each result in the list into a pandas :class:`~pandas.DataFrame` and return that instead of
the results themselves.

If you already have a list of Compounds or Substances, the functions below allow a :class:`~pandas.DataFrame` to be
constructed easily.

.. autofunction:: compounds_to_frame
.. autofunction:: substances_to_frame

Constants
---------

.. autodata:: pubchempy.API_BASE
.. autodata:: pubchempy.ELEMENTS
.. autodata:: pubchempy.PROPERTY_MAP
.. autoclass:: pubchempy.CompoundIdType
   :members:
.. autoclass:: pubchempy.BondType
   :members:
.. autoclass:: pubchempy.CoordinateType
   :members:
.. autoclass:: pubchempy.ProjectCategory
   :members:

Exceptions
----------

.. autoexception:: pubchempy.PubChemPyError
.. autoexception:: pubchempy.ResponseParseError
   :show-inheritance:
.. autoexception:: pubchempy.PubChemHTTPError
   :show-inheritance:
   :members:
.. autoexception:: pubchempy.BadRequestError
   :show-inheritance:
.. autoexception:: pubchempy.NotFoundError
   :show-inheritance:
.. autoexception:: pubchempy.MethodNotAllowedError
   :show-inheritance:
.. autoexception:: pubchempy.ServerError
   :show-inheritance:
.. autoexception:: pubchempy.UnimplementedError
   :show-inheritance:
.. autoexception:: pubchempy.ServerBusyError
   :show-inheritance:
.. autoexception:: pubchempy.TimeoutError
   :show-inheritance:

Changes
-------

-  As of v1.0.3, the ``atoms`` and ``bonds`` properties on :class:`Compounds <pubchempy.Compound>` now return lists of
   :class:`~pubchempy.Atom` and :class:`~pubchempy.Bond` objects, rather than dicts.

-  As of v1.0.2, search functions now return an empty list instead of raising a :class:`~pubchempy.NotFoundError`
   exception when no results are found. :class:`~pubchempy.NotFoundError` is still raised when attempting to create a
   :class:`~pubchempy.Compound` using the ``from_cid`` class method with an invalid CID.
