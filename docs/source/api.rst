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

Compound, Substance and Assay
-----------------------------

.. autoclass:: pubchempy.Compound
   :members:
.. autoclass:: pubchempy.Substance
   :members:
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

Exceptions
----------

.. autoexception:: pubchempy.PubChemHTTPError()
.. autoexception:: pubchempy.BadRequestError()
.. autoexception:: pubchempy.NotFoundError()
.. autoexception:: pubchempy.MethodNotAllowedError()
.. autoexception:: pubchempy.TimeoutError()
.. autoexception:: pubchempy.UnimplementedError()
.. autoexception:: pubchempy.ServerError()

Changes
-------

-  As of v1.0.2, search functions now return an empty list instead of raising a
   ``NotFoundError`` exception when no results are found. ``NotFoundError`` is still
   raised when attempting to create a ``Compound`` using ``Compound.from_cid`` with
   an invalid CID.
