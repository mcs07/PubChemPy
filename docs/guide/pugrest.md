(pugrest)=

# PUG REST

PUG (Power User Gateway) REST is a web service that PubChem provides for programmatic access to its data. PubChemPy uses this web service to interact with the PubChem database, allowing you to search for compounds, substances, and assays, retrieve their properties, and perform various operations without needing to download or store large datasets locally.

You don't need to worry too much about how the PubChem web service works, because PubChemPy handles all of the details for you. But understanding the underlying architecture can help you use PubChemPy more effectively and troubleshoot issues.

## PUG REST Architecture

The PUG REST API is built around a three-part request pattern:

1. **Input**: Specifies which records you're interested in (by CID, name, SMILES, etc.)
2. **Operation**: Defines what to do with those records (retrieve properties, search, etc.)
3. **Output**: Determines the format of the returned data (JSON, XML, CSV, etc.)

This modular design allows for flexible combinations. For example, you can combine structure input via SMILES with property retrieval operations and CSV output - all handled seamlessly by PubChemPy.

## Request Flow

When you make a request with PubChemPy:

1. Your Python request is translated into a PUG REST URL (and possibly some POST data).
2. The request is sent to PubChem's servers via HTTPS.
3. PubChem processes the request using their chemical databases and toolkits.
4. Results are returned and parsed by PubChemPy into Python objects.

PubChem contains over 300 million substance records, over 100 million standardized compound records, and over 1 million biological assays. All this data may be accessed and processed through PubChemPy without requiring local storage or computational resources.

## When to Use Alternatives

While PubChemPy and PUG REST are excellent for many tasks, consider alternatives for:

- **Bulk data processing**: Use PubChem's bulk download services for large datasets
- **Confidential work**: Consider local chemical toolkits for sensitive data
- **Offline work**: The PUG REST API requires an internet connection

## Further Reading

If you want to go beyond the capabilities of PubChemPy, there is helpful documentation about programmatic access to PubChem data on the PubChem website:

- [Programmatic Access to PubChem](https://pubchem.ncbi.nlm.nih.gov/docs/programmatic-access): Overview of how to access PubChem data programmatically.
- [PUG REST Tutorial](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest): Explains how the web service works with a variety of usage examples.
- [PUG REST Specification](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest-tutorial): A more comprehensive but dense specification that details every possible way to use the web service.
