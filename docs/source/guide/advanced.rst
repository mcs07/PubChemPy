.. _advanced:

Advanced
========

.. _avoiding_timeouterror:

Avoiding TimeoutError
---------------------

If there are too many results for a request, you will receive a TimeoutError. There are different ways to avoid this,
depending on what type of request you are doing.

If retrieving full compound or substance records, instead request a list of cids or sids for your input, and then
request the full records for those identifiers individually or in small groups. For example::

	sids = get_sids('Aspirin', 'name')
	for sid in sids:
	    s = Substance.from_sid(sid)

When using the ``formula`` namespace or a ``searchtype``, you can also alternatively use the ``listkey_count`` and
``listkey_start`` keyword arguments to specify pagination. The ``listkey_count`` value specifies the number of
results per page, and the ``listkey_start`` value specifies which page to return. For example::

	get_compounds('CC', 'smiles', searchtype='substructure', listkey_count=5)
	get('C10H21N', 'formula', listkey_count=3, listkey_start=6)


Logging
-------

PubChemPy can generate logging statements if required. Just set the desired logging level::

    import logging
    logging.basicConfig(level=logging.DEBUG)

The logger is named 'pubchempy'. There is more information on logging in the `Python logging documentation`_.

Using behind a proxy
--------------------

When using PubChemPy behind a proxy, you may receive a ``URLError``::

    URLError: <urlopen error [Errno 65] No route to host>

A simple fix is to specify the proxy information via urllib. For Python 3::

    import urllib
    proxy_support = urllib.request.ProxyHandler({
        'http': 'http://<proxy.address>:<port>',
        'https': 'https://<proxy.address>:<port>'
    })
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)

For Python 2::

    import urllib2
    proxy_support = urllib2.ProxyHandler({
        'http': 'http://<proxy.address>:<port>',
        'https': 'https://<proxy.address>:<port>'
    })
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)

Custom requests
---------------

If you wish to perform more complicated requests, you can use the ``request`` function. This is an extremely simple
wrapper around the REST API that allows you to construct any sort of request from a few parameters. The
`PUG REST Specification`_ has all the information you will need to formulate your requests.

The ``request`` function simply returns the exact response from the PubChem server as a string. This can be parsed in
different ways depending on the output format you choose. See the Python `json`_, `xml`_ and `csv`_ packages for more
information. Additionally, cheminformatics toolkits such as `Open Babel`_ and `RDKit`_ offer tools for handling SDF
files in Python.

The ``get`` function is very similar to the ``request`` function, except it handles ``listkey`` type responses
automatically for you. This makes things simpler, however it means you can't take advantage of using the same
``listkey`` repeatedly to obtain different types of information. See the `PUG REST specification`_ for more information
on how `listkey` responses work.

Summary of possible inputs
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

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


.. _`Python logging documentation`: http://docs.python.org/2/howto/logging.html
.. _`json`: http://docs.python.org/2/library/json.html
.. _`xml`: http://docs.python.org/2/library/xml.etree.elementtree.html
.. _`csv`: http://docs.python.org/2/library/csv.html
.. _`PUG REST Specification`: https://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html
.. _`Open Babel`: http://openbabel.org/docs/current/UseTheLibrary/Python.html
.. _`RDKit`: http://www.rdkit.org
