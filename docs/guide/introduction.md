(introduction)=

# Introduction

## How PubChemPy works

PubChemPy relies entirely on the PubChem database and chemical toolkits provided via their PUG REST web service [^f1]. This service provides an interface for programs to automatically carry out the tasks that you might otherwise perform manually via the [PubChem website].

This is important to remember when using PubChemPy: Every request you make is transmitted to the PubChem servers, evaluated, and then a response is sent back. There are some downsides to this: It is less suitable for confidential work, it requires a constant internet connection, and some tasks will be slower than if they were performed locally on your own computer. On the other hand, this means we have the vast resources of the PubChem database and chemical toolkits at our disposal. As a result, it is possible to do complex similarity and substructure searching against a database containing tens of millions of compounds in seconds, without needing any of the storage space or computational power on your own local computer.

See the {doc}`pugrest` page for more information about how PubChemPy uses the PubChem web service.

## PubChemPy license

```{eval-rst}
.. include:: ../../LICENSE
```

```{rubric} Footnotes
```

[^f1]: That's a lot of acronyms! PUG stands for "Power User Gateway", a term used to describe a variety of methods for programmatic access to PubChem data and services. REST stands for [Representational State Transfer], which describes the specific architectural style of the web service.

[pubchem website]: https://pubchem.ncbi.nlm.nih.gov
[representational state transfer]: https://en.wikipedia.org/wiki/Representational_state_transfer
