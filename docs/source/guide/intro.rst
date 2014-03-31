.. _introduction:

Introduction
============

How PubChemPy works
-------------------

PubChemPy relies entirely on the PubChem database and chemical toolkits provided via their PUG REST web service [#f1]_.
This service provides an interface for programs to automatically carry out the tasks that you might otherwise perform
manually via the `PubChem website`_.

This is important to remember when using PubChemPy: Every request you make is transmitted to the PubChem servers,
evaluated, and then a response is sent back. There are some downsides to this: It is less suitable for confidential
work, it requires a constant internet connection, and some tasks will be slower than if they were performed locally on
your own computer. On the other hand, this means we have the vast resources of the PubChem database and chemical
toolkits at our disposal. As a result, it is possible to do complex similarity and substructure searching against a
database containing tens of millions of compounds in seconds, without needing any of the storage space or computational
power on your own local computer.

The PUG REST web service
------------------------

You don't need to worry too much about how the PubChem web service works, because PubChemPy handles all of the details
for you. But if you want to go beyond the capabilities of PubChemPy, there is some helpful documentation on the
PubChem website.

-  `PUG REST Tutorial`_: Explains how the web service works with a variety of usage examples.
-  `PUG REST Specification`_: A more comprehensive but dense specification that details every possible way to use the
   web service.

PubChemPy license
-----------------

.. include:: ../../../LICENSE

.. rubric:: Footnotes

.. [#f1] That's a lot of acronyms! PUG stands for "Power User Gateway", a term used to describe a variety of  methods
   for programmatic access to PubChem data and services. REST stands for `Representational State Transfer`_, which
   describes the specific architectural style of the web service.


.. _`PubChem website`: https://pubchem.ncbi.nlm.nih.gov
.. _`PUG REST Tutorial`: https://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST_Tutorial.html
.. _`PUG REST Specification`: https://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html
.. _`Representational State Transfer`: https://en.wikipedia.org/wiki/Representational_state_transfer
