.. _substance:

Substance
=========

The PubChem Substance database contains all chemical records deposited in PubChem in their most raw form, before any
significant processing is applied. As a result, it contains duplicates, mixtures, and some records that don't make
chemical sense. This means that Substance records contain fewer calculated properties, however they do have additional
information about the original source that deposited the record.

The PubChem Compound database is constructed from the Substance database using a standardization and deduplication
process. Hence each Compound may be derived from a number of different Substances.

Retrieving substances
---------------------

Retrieve Substances using the :func:`~pubchempy.get_substances` function::

    >>> results = pcp.get_substances('Coumarin 343', 'name')
    >>> print results
    [Substance(24864499), Substance(85084977), Substance(126686397), Substance(143491255), Substance(152243230), Substance(162092514), Substance(162189467), Substance(186021999), Substance(206257050)]


You can also instantiate a Substance directly from its SID::

    >>> substance = pcp.Substance.from_sid(223766453)
    >>> print substance.synonyms
    ['2-(Acetyloxy)-benzoic acid', '2-(acetyloxy)benzoic acid', '2-acetoxy benzoic acid', '2-acetoxy-benzoic acid', '2-acetoxybenzoic acid', '2-acetyloxybenzoic acid', 'BSYNRYMUTXBXSQ-UHFFFAOYSA-N', 'acetoxybenzoic acid', 'acetyl salicylic acid', 'acetyl-salicylic acid', 'acetylsalicylic acid', 'aspirin', 'o-acetoxybenzoic acid']
    >>> print substance.source_id
    BSYNRYMUTXBXSQ-UHFFFAOYSA-N
    >>> print substance.standardized_cid
    2244
    >>> print substance.standardized_compound
    Compound(2244)
