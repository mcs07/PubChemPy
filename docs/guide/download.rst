.. _download:

Download
========

The download function is for saving a file to disk. The following formats are available: XML, ASNT/B, JSON, SDF, CSV,
PNG, TXT. Beware that not all formats are available for all types of information. SDF and PNG are only available for
full Compound and Substance records, and CSV is best suited to tables of properties and identifiers.

Examples::

    pcp.download('PNG', 'asp.png', 'Aspirin', 'name')
    pcp.download('CSV', 's.csv', [1,2,3], operation='property/CanonicalSMILES,IsomericSMILES')

For PNG images, the ``image_size`` argument can be used to specfiy ``large``, ``small`` or ``<width>x<height>``.
