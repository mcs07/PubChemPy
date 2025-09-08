"""PubChemPy: Python Interface for the PubChem Database."""

from __future__ import annotations

import enum
import functools
import json
import logging
import os
import ssl
import time
import typing as t
import warnings
from http.client import HTTPResponse
from itertools import zip_longest
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import urlopen

if t.TYPE_CHECKING:
    import pandas as pd

# Get SSL certs from env var or certifi package if available.
_CA_FILE = os.getenv("PUBCHEMPY_CA_BUNDLE") or os.getenv("REQUESTS_CA_BUNDLE")
if not _CA_FILE:
    try:
        import certifi

        _CA_FILE = certifi.where()
    except ImportError:
        _CA_FILE = None


__author__ = "Matt Swain"
__email__ = "m.swain@me.com"
__version__ = "1.0.5"
__license__ = "MIT"

__all__ = [
    # Main API functions
    "get_compounds",
    "get_substances",
    "get_assays",
    "get_properties",
    "get_synonyms",
    "get_cids",
    "get_sids",
    "get_aids",
    "get_all_sources",
    "download",
    "request",
    "get",
    "get_json",
    "get_sdf",
    # Core classes
    "Compound",
    "Substance",
    "Assay",
    "Atom",
    "Bond",
    # Enum/constant classes
    "CompoundIdType",
    "BondType",
    "CoordinateType",
    "ProjectCategory",
    # Data conversion functions
    "compounds_to_frame",
    "substances_to_frame",
    # Constants
    "API_BASE",
    "ELEMENTS",
    "PROPERTY_MAP",
    # Exceptions
    "PubChemPyError",
    "ResponseParseError",
    "PubChemHTTPError",
    "BadRequestError",
    "NotFoundError",
    "MethodNotAllowedError",
    "ServerError",
    "UnimplementedError",
    "ServerBusyError",
    "TimeoutError",
    "PubChemPyDeprecationWarning",
]

#: Base URL for the PubChem PUG REST API.
API_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

log = logging.getLogger("pubchempy")
log.addHandler(logging.NullHandler())

#: Type alias for URL query parameters.
QueryParam = str | int | float | bool | list[str] | None


class CompoundIdType(enum.IntEnum):
    """Compound record type."""

    #: Original Deposited Compound
    DEPOSITED = 0
    #: Standardized Form of a Deposited Compound
    STANDARDIZED = 1
    #: Component of a Standardized Compound
    COMPONENT = 2
    #: Neutralized Form of a Standardized Compound
    NEUTRALIZED = 3
    #: Substance that is a component of a mixture
    MIXTURE = 4
    #: Predicted Tautomer Form
    TAUTOMER = 5
    #: Predicted Ionized pKa Form
    IONIZED = 6
    #: Unknown Compound Type
    UNKNOWN = 255


class BondType(enum.IntEnum):
    """Bond Type Information."""

    #: Single Bond
    SINGLE = 1
    #: Double Bond
    DOUBLE = 2
    #: Triple Bond
    TRIPLE = 3
    #: Quadruple Bond
    QUADRUPLE = 4
    #: Dative Bond
    DATIVE = 5
    #: Complex Bond
    COMPLEX = 6
    #: Ionic Bond
    IONIC = 7
    #: Unknown/Unspecified Connectivity
    UNKNOWN = 255


class CoordinateType(enum.IntEnum):
    """Coordinate Set Type Distinctions."""

    #: 2D Coordinates
    TWO_D = 1
    #: 3D Coordinates (should also indicate units, below)
    THREE_D = 2
    #: Depositor Provided Coordinates
    SUBMITTED = 3
    #: Experimentally Determined Coordinates
    EXPERIMENTAL = 4
    #: Computed Coordinates
    COMPUTED = 5
    #: Standardized Coordinates
    STANDARDIZED = 6
    #: Hybrid Original with Computed Coordinates (e.g., explicit H)
    AUGMENTED = 7
    #: Template used to align drawing
    ALIGNED = 8
    #: Drawing uses shorthand forms (e.g., COOH, OCH3, Et, etc.)
    COMPACT = 9
    #: (3D) Coordinate units are Angstroms
    UNITS_ANGSTROMS = 10
    #: (3D) Coordinate units are nanometers
    UNITS_NANOMETERS = 11
    #: (2D) Coordinate units are pixels
    UNITS_PIXEL = 12
    #: (2D) Coordinate units are points
    UNITS_POINTS = 13
    #: (2D) Coordinate units are standard bond lengths (1.0)
    UNITS_STDBONDS = 14
    #: Coordinate units are unknown or unspecified
    UNITS_UNKNOWN = 255


class ProjectCategory(enum.IntEnum):
    """To distinguish projects funded through MLSCN, MLPCN or other."""

    #: Assay depositions from MLSCN screen center
    MLSCN = 1
    #: Assay depositions from MLPCN screen center
    MLPCN = 2
    #: Assay depositions from MLSCN assay provider
    MLSCN_AP = 3
    #: Assay depositions from MLPCN assay provider
    MLPCN_AP = 4
    #: To be deprecated and replaced by options 7, 8 & 9
    JOURNAL_ARTICLE = 5
    #: Assay depositions from assay vendors
    ASSAY_VENDOR = 6
    #: Data from literature, extracted by curators
    LITERATURE_EXTRACTED = 7
    #: Data from literature, submitted by author of articles
    LITERATURE_AUTHOR = 8
    #: Data from literature, submitted by journals/publishers
    LITERATURE_PUBLISHER = 9
    #: RNAi screenings from RNAi Global Initiative
    RNAIGI = 10
    #: Other project category
    OTHER = 255


#: Dictionary mapping atomic numbers to their element symbols.
#:
#: This dictionary includes 118 standard chemical elements from Hydrogen (1) to
#: Oganesson (118), plus special atom types used by PubChem for non-standard entities
#: like dummy atoms, R-group labels, and lone pairs.
ELEMENTS: dict[int, str] = {
    # Standard chemical elements
    1: "H",  # Hydrogen
    2: "He",  # Helium
    3: "Li",  # Lithium
    4: "Be",  # Beryllium
    5: "B",  # Boron
    6: "C",  # Carbon
    7: "N",  # Nitrogen
    8: "O",  # Oxygen
    9: "F",  # Fluorine
    10: "Ne",  # Neon
    11: "Na",  # Sodium
    12: "Mg",  # Magnesium
    13: "Al",  # Aluminium
    14: "Si",  # Silicon
    15: "P",  # Phosphorus
    16: "S",  # Sulfur
    17: "Cl",  # Chlorine
    18: "Ar",  # Argon
    19: "K",  # Potassium
    20: "Ca",  # Calcium
    21: "Sc",  # Scandium
    22: "Ti",  # Titanium
    23: "V",  # Vanadium
    24: "Cr",  # Chromium
    25: "Mn",  # Manganese
    26: "Fe",  # Iron
    27: "Co",  # Cobalt
    28: "Ni",  # Nickel
    29: "Cu",  # Copper
    30: "Zn",  # Zinc
    31: "Ga",  # Gallium
    32: "Ge",  # Germanium
    33: "As",  # Arsenic
    34: "Se",  # Selenium
    35: "Br",  # Bromine
    36: "Kr",  # Krypton
    37: "Rb",  # Rubidium
    38: "Sr",  # Strontium
    39: "Y",  # Yttrium
    40: "Zr",  # Zirconium
    41: "Nb",  # Niobium
    42: "Mo",  # Molybdenum
    43: "Tc",  # Technetium
    44: "Ru",  # Ruthenium
    45: "Rh",  # Rhodium
    46: "Pd",  # Palladium
    47: "Ag",  # Silver
    48: "Cd",  # Cadmium
    49: "In",  # Indium
    50: "Sn",  # Tin
    51: "Sb",  # Antimony
    52: "Te",  # Tellurium
    53: "I",  # Iodine
    54: "Xe",  # Xenon
    55: "Cs",  # Cesium
    56: "Ba",  # Barium
    57: "La",  # Lanthanum
    58: "Ce",  # Cerium
    59: "Pr",  # Praseodymium
    60: "Nd",  # Neodymium
    61: "Pm",  # Promethium
    62: "Sm",  # Samarium
    63: "Eu",  # Europium
    64: "Gd",  # Gadolinium
    65: "Tb",  # Terbium
    66: "Dy",  # Dysprosium
    67: "Ho",  # Holmium
    68: "Er",  # Erbium
    69: "Tm",  # Thulium
    70: "Yb",  # Ytterbium
    71: "Lu",  # Lutetium
    72: "Hf",  # Hafnium
    73: "Ta",  # Tantalum
    74: "W",  # Tungsten
    75: "Re",  # Rhenium
    76: "Os",  # Osmium
    77: "Ir",  # Iridium
    78: "Pt",  # Platinum
    79: "Au",  # Gold
    80: "Hg",  # Mercury
    81: "Tl",  # Thallium
    82: "Pb",  # Lead
    83: "Bi",  # Bismuth
    84: "Po",  # Polonium
    85: "At",  # Astatine
    86: "Rn",  # Radon
    87: "Fr",  # Francium
    88: "Ra",  # Radium
    89: "Ac",  # Actinium
    90: "Th",  # Thorium
    91: "Pa",  # Protactinium
    92: "U",  # Uranium
    93: "Np",  # Neptunium
    94: "Pu",  # Plutonium
    95: "Am",  # Americium
    96: "Cm",  # Curium
    97: "Bk",  # Berkelium
    98: "Cf",  # Californium
    99: "Es",  # Einsteinium
    100: "Fm",  # Fermium
    101: "Md",  # Mendelevium
    102: "No",  # Nobelium
    103: "Lr",  # Lawrencium
    104: "Rf",  # Rutherfordium
    105: "Db",  # Dubnium
    106: "Sg",  # Seaborgium
    107: "Bh",  # Bohrium
    108: "Hs",  # Hassium
    109: "Mt",  # Meitnerium
    110: "Ds",  # Darmstadtium
    111: "Rg",  # Roentgenium
    112: "Cn",  # Copernicium
    113: "Nh",  # Nihonium
    114: "Fl",  # Flerovium
    115: "Mc",  # Moscovium
    116: "Lv",  # Livermorium
    117: "Ts",  # Tennessine
    118: "Og",  # Oganesson
    # Special atom types
    252: "Lp",  # Lone Pair
    253: "R",  # Rgroup Label
    254: "*",  # Dummy Atom
    255: "*",  # Unspecified Atom (Asterisk)
}


def request(
    identifier: str | int | list[str | int],
    namespace: str = "cid",
    domain: str = "compound",
    operation: str | None = None,
    output: str = "JSON",
    searchtype: str | None = None,
    **kwargs: QueryParam,
) -> HTTPResponse:
    """Construct API request from parameters and return the response.

    Full specification at https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
    """
    if not identifier:
        raise ValueError("identifier/cid cannot be None")
    # If identifier is a list, join with commas into string
    if isinstance(identifier, int):
        identifier = str(identifier)
    if not isinstance(identifier, str):
        identifier = ",".join(str(x) for x in identifier)
    # Filter None values from kwargs
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    # Build API URL
    urlid, postdata = None, None
    if namespace == "sourceid":
        identifier = identifier.replace("/", ".")
    if (
        namespace in ["listkey", "formula", "sourceid"]
        or searchtype == "xref"
        or (searchtype and namespace == "cid")
        or domain == "sources"
    ):
        urlid = quote(identifier.encode("utf8"))
    else:
        postdata = urlencode([(namespace, identifier)]).encode("utf8")
    comps = filter(
        None, [API_BASE, domain, searchtype, namespace, urlid, operation, output]
    )
    apiurl = "/".join(comps)
    if kwargs:
        apiurl += f"?{urlencode(kwargs)}"
    # Make request
    try:
        log.debug(f"Request URL: {apiurl}")
        log.debug(f"Request data: {postdata}")
        context = ssl.create_default_context(cafile=_CA_FILE)
        response = urlopen(apiurl, postdata, context=context)
        return response
    except HTTPError as e:
        raise create_http_error(e) from e


def get(
    identifier: str | int | list[str | int],
    namespace: str = "cid",
    domain: str = "compound",
    operation: str | None = None,
    output: str = "JSON",
    searchtype: str | None = None,
    **kwargs: QueryParam,
) -> bytes:
    """Request wrapper that automatically handles async requests."""
    if (searchtype and searchtype != "xref") or namespace in ["formula"]:
        response = request(
            identifier, namespace, domain, None, "JSON", searchtype, **kwargs
        ).read()
        status = json.loads(response.decode())
        if "Waiting" in status and "ListKey" in status["Waiting"]:
            identifier = status["Waiting"]["ListKey"]
            namespace = "listkey"
            while "Waiting" in status and "ListKey" in status["Waiting"]:
                time.sleep(2)
                response = request(
                    identifier, namespace, domain, operation, "JSON", **kwargs
                ).read()
                status = json.loads(response.decode())
            if not output == "JSON":
                response = request(
                    identifier,
                    namespace,
                    domain,
                    operation,
                    output,
                    searchtype,
                    **kwargs,
                ).read()
    else:
        response = request(
            identifier, namespace, domain, operation, output, searchtype, **kwargs
        ).read()
    return response


def get_json(
    identifier: str | int | list[str | int],
    namespace: str = "cid",
    domain: str = "compound",
    operation: str | None = None,
    searchtype: str | None = None,
    **kwargs: QueryParam,
) -> dict[str, t.Any] | None:
    """Request wrapper that automatically parses JSON response into a python dict.

    This function suppresses NotFoundError and returns None if no results are found.
    """
    try:
        return json.loads(
            get(
                identifier, namespace, domain, operation, "JSON", searchtype, **kwargs
            ).decode()
        )
    except NotFoundError as e:
        log.info(e)
        return None


def get_sdf(
    identifier: str | int | list[str | int],
    namespace: str = "cid",
    domain: str = "compound",
    operation: str | None = None,
    searchtype: str | None = None,
    **kwargs: QueryParam,
) -> str | None:
    """Request wrapper that automatically extracts SDF from the response.

    This function suppresses NotFoundError and returns None if no results are found.
    """
    try:
        return get(
            identifier, namespace, domain, operation, "SDF", searchtype, **kwargs
        ).decode()
    except NotFoundError as e:
        log.info(e)
        return None


def get_compounds(
    identifier: str | int | list[str | int],
    namespace: str = "cid",
    searchtype: str | None = None,
    as_dataframe: bool = False,
    **kwargs: QueryParam,
) -> list[Compound] | pd.DataFrame:
    """Retrieve the specified compound records from PubChem.

    Args:
        identifier: The compound identifier to use as a search query.
        namespace: The identifier type, one of cid, name, smiles, sdf, inchi,
            inchikey or formula.
        searchtype: The advanced search type, one of substructure,
            superstructure or similarity.
        as_dataframe: Automatically extract the Compound properties into a pandas
            DataFrame and return that.
        **kwargs: Additional query parameters to pass to the API request.

    Returns:
        List of :class:`~pubchempy.Compound` objects, or a pandas DataFrame if
        ``as_dataframe=True``.
    """
    results = get_json(identifier, namespace, searchtype=searchtype, **kwargs)
    compounds = [Compound(r) for r in results["PC_Compounds"]] if results else []
    if as_dataframe:
        return compounds_to_frame(compounds)
    return compounds


def get_substances(
    identifier: str | int | list[str | int],
    namespace: str = "sid",
    as_dataframe: bool = False,
    **kwargs: QueryParam,
) -> list[Substance] | pd.DataFrame:
    """Retrieve the specified substance records from PubChem.

    Args:
        identifier: The substance identifier to use as a search query.
        namespace: The identifier type, one of sid, name or sourceid/<source name>.
        as_dataframe: Automatically extract the Substance properties into a pandas
            DataFrame and return that.
        **kwargs: Additional query parameters to pass to the API request.

    Returns:
        List of :class:`~pubchempy.Substance` objects, or a pandas DataFrame if
        ``as_dataframe=True``.
    """
    results = get_json(identifier, namespace, "substance", **kwargs)
    substances = [Substance(r) for r in results["PC_Substances"]] if results else []
    if as_dataframe:
        return substances_to_frame(substances)
    return substances


def get_assays(
    identifier: str | int | list[str | int],
    namespace: str = "aid",
    **kwargs: QueryParam,
) -> list[Assay]:
    """Retrieve the specified assay records from PubChem.

    Args:
        identifier: The assay identifier to use as a search query.
        namespace: The identifier type.
        **kwargs: Additional query parameters to pass to the API request.

    Returns:
        List of :class:`~pubchempy.Assay` objects.
    """
    results = get_json(identifier, namespace, "assay", "description", **kwargs)
    return [Assay(r) for r in results["PC_AssayContainer"]] if results else []


#: Dictionary mapping property names to their PubChem API equivalents.
#:
#: Allows properties to optionally be specified as underscore_separated,
#: consistent with Compound attributes.
PROPERTY_MAP: dict[str, str] = {
    "molecular_formula": "MolecularFormula",
    "molecular_weight": "MolecularWeight",
    "smiles": "SMILES",
    "connectivity_smiles": "ConnectivitySMILES",
    "canonical_smiles": "CanonicalSMILES",
    "isomeric_smiles": "IsomericSMILES",
    "inchi": "InChI",
    "inchikey": "InChIKey",
    "iupac_name": "IUPACName",
    "xlogp": "XLogP",
    "exact_mass": "ExactMass",
    "monoisotopic_mass": "MonoisotopicMass",
    "tpsa": "TPSA",
    "complexity": "Complexity",
    "charge": "Charge",
    "h_bond_donor_count": "HBondDonorCount",
    "h_bond_acceptor_count": "HBondAcceptorCount",
    "rotatable_bond_count": "RotatableBondCount",
    "heavy_atom_count": "HeavyAtomCount",
    "isotope_atom_count": "IsotopeAtomCount",
    "atom_stereo_count": "AtomStereoCount",
    "defined_atom_stereo_count": "DefinedAtomStereoCount",
    "undefined_atom_stereo_count": "UndefinedAtomStereoCount",
    "bond_stereo_count": "BondStereoCount",
    "defined_bond_stereo_count": "DefinedBondStereoCount",
    "undefined_bond_stereo_count": "UndefinedBondStereoCount",
    "covalent_unit_count": "CovalentUnitCount",
    "volume_3d": "Volume3D",
    "conformer_rmsd_3d": "ConformerModelRMSD3D",
    "conformer_model_rmsd_3d": "ConformerModelRMSD3D",
    "x_steric_quadrupole_3d": "XStericQuadrupole3D",
    "y_steric_quadrupole_3d": "YStericQuadrupole3D",
    "z_steric_quadrupole_3d": "ZStericQuadrupole3D",
    "feature_count_3d": "FeatureCount3D",
    "feature_acceptor_count_3d": "FeatureAcceptorCount3D",
    "feature_donor_count_3d": "FeatureDonorCount3D",
    "feature_anion_count_3d": "FeatureAnionCount3D",
    "feature_cation_count_3d": "FeatureCationCount3D",
    "feature_ring_count_3d": "FeatureRingCount3D",
    "feature_hydrophobe_count_3d": "FeatureHydrophobeCount3D",
    "effective_rotor_count_3d": "EffectiveRotorCount3D",
    "conformer_count_3d": "ConformerCount3D",
}


def get_properties(
    properties: str | list[str],
    identifier: str | int | list[str | int],
    namespace: str = "cid",
    searchtype: str | None = None,
    as_dataframe: bool = False,
    **kwargs: QueryParam,
) -> list[dict[str, t.Any]] | pd.DataFrame:
    """Retrieve the specified compound properties from PubChem.

    Args:
        properties: The properties to retrieve.
        identifier: The compound  identifier to use as a search query.
        namespace: The identifier type.
        searchtype: The advanced search type, one of substructure, superstructure
            or similarity.
        as_dataframe: Automatically extract the properties into a pandas DataFrame.
        **kwargs: Additional query parameters to pass to the API request.
    """
    if isinstance(properties, str):
        properties = properties.split(",")
    properties = ",".join([PROPERTY_MAP.get(p, p) for p in properties])
    properties = f"property/{properties}"
    results = get_json(
        identifier, namespace, "compound", properties, searchtype=searchtype, **kwargs
    )
    results = results["PropertyTable"]["Properties"] if results else []
    if as_dataframe:
        import pandas as pd

        return pd.DataFrame.from_records(results, index="CID")
    return results


def get_synonyms(
    identifier: str | int | list[str | int],
    namespace: str = "cid",
    domain: str = "compound",
    searchtype: str | None = None,
    **kwargs: QueryParam,
) -> list[dict[str, t.Any]]:
    """Retrieve synonyms (alternative names) for the specified records from PubChem.

    Synonyms include systematic names, common names, trade names, registry numbers,
    and other identifiers associated with compounds, substances, or assays.

    Args:
        identifier: The identifier to use as a search query.
        namespace: The identifier type (e.g., cid, name, smiles for compounds).
        domain: The PubChem domain to search (compound or substance).
        searchtype: The advanced search type, one of substructure, superstructure
            or similarity.
        **kwargs: Additional parameters to pass to the request.

    Returns:
        List of dictionaries containing synonym information for each matching record.
        Each dictionary contains the record identifier and a list of synonyms.
    """
    results = get_json(
        identifier, namespace, domain, "synonyms", searchtype=searchtype, **kwargs
    )
    return results["InformationList"]["Information"] if results else []


def get_cids(
    identifier: str | int | list[str | int],
    namespace: str = "name",
    domain: str = "compound",
    searchtype: str | None = None,
    **kwargs: QueryParam,
) -> list[int]:
    """Retrieve Compound Identifiers (CIDs) for the specified query from PubChem.

    CIDs are unique numerical identifiers assigned to each standardized compound
    record in the PubChem Compound database. This function is useful for converting
    between different identifier types (names, SMILES, InChI, etc.) and CIDs.

    Args:
        identifier: The identifier to use as a search query.
        namespace: The identifier type (e.g. name, smiles, inchi, formula).
        domain: The PubChem domain to search (compound, substance, or assay).
        searchtype: The advanced search type, one of substructure, superstructure
            or similarity.
        **kwargs: Additional parameters to pass to the request.

    Returns:
        List of CIDs (integers) that match the search criteria. Empty list if no
        matches found.
    """
    results = get_json(
        identifier, namespace, domain, "cids", searchtype=searchtype, **kwargs
    )
    if not results:
        return []
    elif "IdentifierList" in results:
        return results["IdentifierList"]["CID"]
    elif "InformationList" in results:
        return results["InformationList"]["Information"]


def get_sids(
    identifier: str | int | list[str | int],
    namespace: str = "cid",
    domain: str = "compound",
    searchtype: str | None = None,
    **kwargs: QueryParam,
) -> list[int]:
    """Retrieve Substance Identifiers (SIDs) for the specified query from PubChem.

    SIDs are unique numerical identifiers assigned to each substance record
    in the PubChem Substance database. This function is useful for finding
    which substance records are associated with a given compound or other identifier.

    Args:
        identifier: The identifier to use as a search query.
        namespace: The identifier type (e.g., cid, name, smiles for compounds).
        domain: The PubChem domain to search (compound, substance, or assay).
        searchtype: The advanced search type, one of substructure, superstructure
            or similarity.
        **kwargs: Additional parameters to pass to the request.

    Returns:
        List of SIDs (integers) that match the search criteria. Empty list if no
        matches found.
    """
    results = get_json(
        identifier, namespace, domain, "sids", searchtype=searchtype, **kwargs
    )
    if not results:
        return []
    elif "IdentifierList" in results:
        return results["IdentifierList"]["SID"]
    elif "InformationList" in results:
        return results["InformationList"]["Information"]


def get_aids(
    identifier: str | int | list[str | int],
    namespace: str = "cid",
    domain: str = "compound",
    searchtype: str | None = None,
    **kwargs: QueryParam,
) -> list[int]:
    """Retrieve Assay Identifiers (AIDs) for the specified query from PubChem.

    AIDs are unique numerical identifiers assigned to each biological assay
    record in the PubChem BioAssay database. This function is useful for finding
    which assays have tested a given compound or substance.

    Args:
        identifier: The identifier to use as a search query.
        namespace: The identifier type (e.g., cid, name, smiles).
        domain: The PubChem domain to search (compound, substance, or assay).
        searchtype: The advanced search type, one of substructure, superstructure
            or similarity.
        **kwargs: Additional parameters to pass to the request.

    Returns:
        List of AIDs (integers) that match the search criteria. Empty list if no
        matches found.
    """
    results = get_json(
        identifier, namespace, domain, "aids", searchtype=searchtype, **kwargs
    )
    if not results:
        return []
    elif "IdentifierList" in results:
        return results["IdentifierList"]["AID"]
    elif "InformationList" in results:
        return results["InformationList"]["Information"]


def get_all_sources(domain: str = "substance") -> list[str]:
    """Return a list of all current depositors of substances or assays."""
    results = json.loads(get(domain, None, "sources").decode())
    return results["InformationList"]["SourceName"]


def download(
    outformat: str,
    path: str | os.PathLike,
    identifier: str | int | list[str | int],
    namespace: str = "cid",
    domain: str = "compound",
    operation: str | None = None,
    searchtype: str | None = None,
    overwrite: bool = False,
    **kwargs: QueryParam,
) -> None:
    """Format can be  XML, ASNT/B, JSON, SDF, CSV, PNG, TXT."""
    response = get(
        identifier, namespace, domain, operation, outformat, searchtype, **kwargs
    )
    if not overwrite and os.path.isfile(path):
        raise OSError(f"{path} already exists. Use 'overwrite=True' to overwrite it.")
    with open(path, "wb") as f:
        f.write(response)


def memoized_property(fget: t.Callable[[t.Any], t.Any]) -> property:
    """Decorator to create memoized properties.

    Used to cache :class:`~pubchempy.Compound` and :class:`~pubchempy.Substance`
    properties that require an additional request.
    """
    attr_name = f"_{fget.__name__}"

    @functools.wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)

    return property(fget_memoized)


def deprecated(message: str) -> t.Callable[[t.Callable], t.Callable]:
    """Decorator to mark as deprecated and emit a warning when used."""

    def deco(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated: {message}",
                category=PubChemPyDeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapped

    return deco


class Atom:
    """Class to represent an atom in a :class:`~pubchempy.Compound`."""

    def __init__(
        self,
        aid: int,
        number: int,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
        charge: int = 0,
    ) -> None:
        """Initialize with an atom ID, atomic number, coordinates and optional charge.

        Args:
            aid: Atom ID.
            number: Atomic number.
            x: X coordinate.
            y: Y coordinate.
            z: Z coordinate.
            charge: Formal charge on atom.
        """
        self.aid = aid
        """The atom ID within the owning Compound."""
        self.number = number
        """The atomic number for this atom."""
        self.x = x
        """The x coordinate for this atom."""
        self.y = y
        """The y coordinate for this atom."""
        self.z = z
        """The z coordinate for this atom. Will be ``None`` in 2D Compound records."""
        self.charge = charge
        """The formal charge on this atom."""

    def __repr__(self) -> str:
        return f"Atom({self.aid!r}, {self.element!r})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self))
            and self.aid == other.aid
            and self.element == other.element
            and self.x == other.x
            and self.y == other.y
            and self.z == other.z
            and self.charge == other.charge
        )

    @deprecated("Dictionary style access to Atom attributes is deprecated")
    def __getitem__(self, prop):
        """Allow dict-style access to attributes for backwards compatibility."""
        if prop in {"element", "x", "y", "z", "charge"}:
            return getattr(self, prop)
        raise KeyError(prop)

    @deprecated("Dictionary style access to Atom attributes is deprecated")
    def __setitem__(self, prop, val):
        """Allow dict-style setting of attributes for backwards compatibility."""
        setattr(self, prop, val)

    @deprecated("Dictionary style access to Atom attributes is deprecated")
    def __contains__(self, prop):
        """Allow dict-style checking of attributes for backwards compatibility."""
        if prop in {"element", "x", "y", "z", "charge"}:
            return getattr(self, prop) is not None
        return False

    @property
    def element(self) -> str:
        """The element symbol for this atom."""
        return ELEMENTS.get(self.number, str(self.number))

    def to_dict(self) -> dict[str, t.Any]:
        """Return a dictionary containing Atom data."""
        data = {"aid": self.aid, "number": self.number, "element": self.element}
        for coord in {"x", "y", "z"}:
            if getattr(self, coord) is not None:
                data[coord] = getattr(self, coord)
        if self.charge != 0:
            data["charge"] = self.charge
        return data

    def set_coordinates(self, x: float, y: float, z: float | None = None) -> None:
        """Set all coordinate dimensions at once."""
        self.x = x
        self.y = y
        self.z = z

    @property
    def coordinate_type(self) -> str:
        """Whether this atom has 2D or 3D coordinates."""
        return "2d" if self.z is None else "3d"


class Bond:
    """Class to represent a bond between two atoms in a :class:`~pubchempy.Compound`."""

    def __init__(
        self,
        aid1: int,
        aid2: int,
        order: BondType = BondType.SINGLE,
        style: int | None = None,
    ) -> None:
        """Initialize with begin and end atom IDs, bond order and bond style.

        Args:
            aid1: Begin atom ID.
            aid2: End atom ID.
            order: Bond order.
            style: Bond style annotation.
        """
        self.aid1 = aid1
        """ID of the begin atom of this bond."""
        self.aid2 = aid2
        """ID of the end atom of this bond."""
        self.order = order
        """Bond order."""
        self.style = style
        """Bond style annotation."""

    def __repr__(self) -> str:
        return f"Bond({self.aid1!r}, {self.aid2!r}, {self.order!r})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self))
            and self.aid1 == other.aid1
            and self.aid2 == other.aid2
            and self.order == other.order
            and self.style == other.style
        )

    @deprecated("Dictionary style access to Bond attributes is deprecated")
    def __getitem__(self, prop):
        """Allow dict-style access to attributes for backwards compatibility."""
        if prop in {"order", "style"}:
            return getattr(self, prop)
        raise KeyError(prop)

    @deprecated("Dictionary style access to Bond attributes is deprecated")
    def __setitem__(self, prop, val):
        """Allow dict-style setting of attributes for backwards compatibility."""
        setattr(self, prop, val)

    @deprecated("Dictionary style access to Bond attributes is deprecated")
    def __contains__(self, prop):
        """Allow dict-style checking of attributes for backwards compatibility."""
        if prop in {"order", "style"}:
            return getattr(self, prop) is not None
        return False

    @deprecated("Dictionary style access to Bond attributes is deprecated")
    def __delitem__(self, prop):
        """Allow dict-style deletion of attributes for backwards compatibility."""
        if not hasattr(self.__wrapped, prop):
            raise KeyError(prop)
        delattr(self.__wrapped, prop)

    def to_dict(self) -> dict[str, t.Any]:
        """Return a dictionary containing Bond data."""
        data = {"aid1": self.aid1, "aid2": self.aid2, "order": self.order}
        if self.style is not None:
            data["style"] = self.style
        return data


class Compound:
    """Represents a standardized chemical structure record from PubChem.

    The PubChem Compound database contains standardized and deduplicated chemical
    structures derived from the Substance database. Each Compound is uniquely identified
    by a CID (Compound Identifier) and represents a unique chemical structure with
    calculated properties, descriptors, and associated experimental data.

    Examples:
        >>> compound = Compound.from_cid(2244)  # Aspirin
        >>> print(f"Formula: {compound.molecular_formula}")
        Formula: C9H8O4
        >>> print(f"IUPAC: {compound.iupac_name}")
        IUPAC: 2-acetyloxybenzoic acid
        >>> print(f"MW: {compound.molecular_weight}")
        MW: 180.16
    """

    def __init__(self, record: dict[str, t.Any]) -> None:
        """Initialize a Compound with a record dict from the PubChem PUG REST service.

        Args:
            record: Compound record returned by the PubChem PUG REST service.

        Note:
            Most users will not need to instantiate a Compound instance directly from a
            record. The :meth:`from_cid()` class method and the :func:`~get_compounds()`
            function offer more convenient ways to obtain Compound instances, as they
            also handle the retrieval of the record from PubChem.
        """
        self._record = None
        self._atoms = {}
        self._bonds = {}
        self.record = record

    def _setup_atoms(self) -> None:
        """Derive Atom objects from the record."""
        # Delete existing atoms
        self._atoms = {}
        # Create atoms
        aids = self.record["atoms"]["aid"]
        elements = self.record["atoms"]["element"]
        if not len(aids) == len(elements):
            raise ResponseParseError("Error parsing atom elements")
        for aid, element in zip(aids, elements):
            self._atoms[aid] = Atom(aid=aid, number=element)
        # Add coordinates
        if "coords" in self.record:
            coord_ids = self.record["coords"][0]["aid"]
            xs = self.record["coords"][0]["conformers"][0]["x"]
            ys = self.record["coords"][0]["conformers"][0]["y"]
            zs = self.record["coords"][0]["conformers"][0].get("z", [])
            if not len(coord_ids) == len(xs) == len(ys) == len(self._atoms) or (
                zs and not len(zs) == len(coord_ids)
            ):
                raise ResponseParseError("Error parsing atom coordinates")
            for aid, x, y, z in zip_longest(coord_ids, xs, ys, zs):
                self._atoms[aid].set_coordinates(x, y, z)
        # Add charges
        if "charge" in self.record["atoms"]:
            for charge in self.record["atoms"]["charge"]:
                self._atoms[charge["aid"]].charge = charge["value"]

    def _setup_bonds(self) -> None:
        """Derive Bond objects from the record."""
        self._bonds = {}
        if "bonds" not in self.record:
            return
        # Create bonds
        aid1s = self.record["bonds"]["aid1"]
        aid2s = self.record["bonds"]["aid2"]
        orders = self.record["bonds"]["order"]
        if not len(aid1s) == len(aid2s) == len(orders):
            raise ResponseParseError("Error parsing bonds")
        for aid1, aid2, order in zip(aid1s, aid2s, orders):
            self._bonds[frozenset((aid1, aid2))] = Bond(
                aid1=aid1, aid2=aid2, order=order
            )
        # Add styles
        if (
            "coords" in self.record
            and "style" in self.record["coords"][0]["conformers"][0]
        ):
            aid1s = self.record["coords"][0]["conformers"][0]["style"]["aid1"]
            aid2s = self.record["coords"][0]["conformers"][0]["style"]["aid2"]
            styles = self.record["coords"][0]["conformers"][0]["style"]["annotation"]
            for aid1, aid2, style in zip(aid1s, aid2s, styles):
                self._bonds[frozenset((aid1, aid2))].style = style

    @classmethod
    def from_cid(cls, cid: int, **kwargs: QueryParam) -> Compound:
        """Retrieve the Compound record for the specified CID.

        Args:
            cid: The PubChem Compound Identifier (CID) to retrieve.
            **kwargs: Additional parameters to pass to the request.

        Example:
            c = Compound.from_cid(6819)
        """
        record = json.loads(request(cid, **kwargs).read().decode())["PC_Compounds"][0]
        return cls(record)

    @property
    def record(self) -> dict[str, t.Any]:
        """The full compound record returned by the PubChem PUG REST service."""
        return self._record

    @record.setter
    def record(self, record: dict[str, t.Any]) -> None:
        self._record = record
        log.debug(f"Created {self}")
        self._setup_atoms()
        self._setup_bonds()

    def __repr__(self) -> str:
        return f"Compound({self.cid if self.cid else ''})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.record == other.record

    def to_dict(self, properties: list[str] | None = None) -> dict[str, t.Any]:
        """Return a dict containing Compound property data.

        Optionally specify a list of the desired properties to include. If
        ``properties`` is not specified, all properties are included, with the following
        exceptions:

        :attr:`synonyms`, :attr:`aids` and :attr:`sids` are not included unless
        explicitly specified. This is because they each require an extra request to the
        PubChem API to retrieve.

        :attr:`canonical_smiles` and :attr:`isomeric_smiles` are not included by
        default, as they are deprecated and have been replaced by
        :attr:`connectivity_smiles` and :attr:`smiles` respectively.

        Args:
            properties: List of desired properties.

        Returns:
            Dictionary of compound data.
        """
        if not properties:
            skip = {
                "record",
                "aids",
                "sids",
                "synonyms",
                "canonical_smiles",
                "isomeric_smiles",
            }
            properties = [
                p
                for p, v in Compound.__dict__.items()
                if isinstance(v, property) and p not in skip
            ]
        return {
            p: [i.to_dict() for i in getattr(self, p)]
            if p in {"atoms", "bonds"}
            else getattr(self, p)
            for p in properties
        }

    def to_series(self, properties: list[str] | None = None) -> pd.Series:
        """Return a pandas :class:`~pandas.Series` containing Compound data.

        Optionally specify a list of the desired properties to include as columns. If
        ``properties`` is not specified, all properties are included, with the following
        exceptions:

        :attr:`synonyms`, :attr:`aids` and :attr:`sids` are not included unless
        explicitly specified. This is because they each require an extra request to the
        PubChem API to retrieve.

        :attr:`canonical_smiles` and :attr:`isomeric_smiles` are not included by
        default, as they are deprecated and have been replaced by
        :attr:`connectivity_smiles` and :attr:`smiles` respectively.

        Args:
            properties: List of desired properties.
        """
        import pandas as pd

        return pd.Series(self.to_dict(properties))

    @property
    def cid(self) -> int | None:
        """The PubChem Compound Identifier (CID).

        .. note::

            When searching using a SMILES or InChI query that is not present in the
            PubChem Compound database, an automatically generated record may be returned
            that contains properties that have been calculated on the fly. These records
            will not have a CID property.
        """
        try:
            return self.record["id"]["id"]["cid"]
        except KeyError:
            return None

    @property
    def elements(self) -> list[str]:
        """List of element symbols for atoms in this Compound."""
        return [a.element for a in self.atoms]

    @property
    def atoms(self) -> list[Atom]:
        """List of :class:`Atoms <pubchempy.Atom>` in this Compound."""
        return sorted(self._atoms.values(), key=lambda x: x.aid)

    @property
    def bonds(self) -> list[Bond]:
        """List of :class:`Bonds <pubchempy.Bond>` in this Compound."""
        return sorted(self._bonds.values(), key=lambda x: (x.aid1, x.aid2))

    @memoized_property
    def synonyms(self) -> list[str] | None:
        """Ranked list of all the names associated with this Compound.

        Requires an extra request. Result is cached.
        """
        if self.cid:
            results = get_json(self.cid, operation="synonyms")
            return (
                results["InformationList"]["Information"][0]["Synonym"]
                if results
                else []
            )

    @memoized_property
    def sids(self) -> list[int] | None:
        """List of Substance Identifiers associated with this Compound.

        Requires an extra request. Result is cached.
        """
        if self.cid:
            results = get_json(self.cid, operation="sids")
            return (
                results["InformationList"]["Information"][0]["SID"] if results else []
            )

    @memoized_property
    def aids(self) -> list[int] | None:
        """List of Assay Identifiers associated with this Compound.

        Requires an extra request. Result is cached.
        """
        if self.cid:
            results = get_json(self.cid, operation="aids")
            return (
                results["InformationList"]["Information"][0]["AID"] if results else []
            )

    @property
    def coordinate_type(self) -> str | None:
        """Whether this Compound has 2D or 3D coordinates."""
        if CoordinateType.TWO_D in self.record["coords"][0]["type"]:
            return "2d"
        elif CoordinateType.THREE_D in self.record["coords"][0]["type"]:
            return "3d"

    @property
    def charge(self) -> int:
        """Formal charge on this Compound."""
        return self.record["charge"] if "charge" in self.record else 0

    @property
    def molecular_formula(self) -> str | None:
        """Molecular formula.

        The molecular formula represents the number of atoms of each element in a
        compound. It does not contain any information about connectivity or structure.
        """
        return _parse_prop({"label": "Molecular Formula"}, self.record["props"])

    @property
    def molecular_weight(self) -> float | None:
        """Molecular weight in g/mol.

        The molecular weight is the sum of all atomic weights of the constituent
        atoms in a compound, measured in g/mol. In the absence of explicit isotope
        labelling, averaged natural abundance is assumed. If an atom bears an
        explicit isotope label, 100% isotopic purity is assumed at this location.
        """
        sval = _parse_prop({"label": "Molecular Weight"}, self.record["props"])
        return float(sval) if sval else None

    @property
    @deprecated("Use connectivity_smiles instead")
    def canonical_smiles(self) -> str | None:
        """Canonical SMILES, with no stereochemistry information (deprecated).

        .. deprecated:: 1.0.5
           :attr:`canonical_smiles` is deprecated, use :attr:`connectivity_smiles`
           instead.
        """
        return self.connectivity_smiles

    @property
    @deprecated("Use smiles instead")
    def isomeric_smiles(self) -> str | None:
        """Isomeric SMILES.

        .. deprecated:: 1.0.5
           :attr:`isomeric_smiles` is deprecated, use :attr:`smiles` instead.
        """
        return self.smiles

    @property
    def connectivity_smiles(self) -> str | None:
        """Connectivity SMILES string.

        A canonical SMILES string that includes connectivity information only. It
        excludes stereochemical and isotopic information.

        Replaces the deprecated :attr:`canonical_smiles` property.
        """
        return _parse_prop(
            {"label": "SMILES", "name": "Connectivity"}, self.record["props"]
        )

    @property
    def smiles(self) -> str | None:
        """Absolute SMILES string (isomeric and canonical).

        A canonical SMILES string that includes both stereochemical and isotopic
        information. This provides the most complete linear representation of the
        molecular structure.

        Replaces the deprecated :attr:`isomeric_smiles` property.
        """
        return _parse_prop(
            {"label": "SMILES", "name": "Absolute"}, self.record["props"]
        )

    @property
    def inchi(self) -> str | None:
        """Standard IUPAC International Chemical Identifier (InChI).

        The InChI provides a unique, standardized representation of molecular
        structure that is not dependent on the software used to generate it.
        It includes connectivity, stereochemistry, and isotopic information
        in a layered format. This standard version does not allow for user
        selectable options in dealing with stereochemistry and tautomer layers.
        """
        return _parse_prop({"label": "InChI", "name": "Standard"}, self.record["props"])

    @property
    def inchikey(self) -> str | None:
        """Standard InChIKey.

        A hashed version of the full standard InChI, consisting of 27 characters
        divided into three blocks separated by hyphens. The InChIKey provides a
        fixed-length identifier that is more suitable for database indexing and
        web searches than the full InChI string.
        """
        return _parse_prop(
            {"label": "InChIKey", "name": "Standard"}, self.record["props"]
        )

    @property
    def iupac_name(self) -> str | None:
        """Preferred IUPAC name.

        The chemical name systematically determined according to IUPAC
        (International Union of Pure and Applied Chemistry) nomenclature rules.
        This is the preferred systematic name among the available IUPAC naming
        styles (Allowed, CAS-like Style, Preferred, Systematic, Traditional).
        """
        # Note: record has Allowed, CAS-like Style, Preferred, Systematic, Traditional
        return _parse_prop(
            {"label": "IUPAC Name", "name": "Preferred"}, self.record["props"]
        )

    @property
    def xlogp(self) -> float | None:
        """XLogP octanol-water partition coefficient.

        A computationally generated octanol-water partition coefficient that
        measures the hydrophilicity or hydrophobicity of a molecule. Higher
        values indicate more lipophilic (fat-soluble) compounds, while lower
        values indicate more hydrophilic (water-soluble) compounds.
        """
        return _parse_prop({"label": "Log P"}, self.record["props"])

    @property
    def exact_mass(self) -> float | None:
        """Exact mass in Da (Daltons).

        The mass of the most likely isotopic composition for a single molecule,
        corresponding to the most intense ion/molecule peak in a mass spectrum.
        This differs from molecular weight in that it uses the exact masses of
        specific isotopes rather than averaged atomic weights.
        """
        sval = _parse_prop({"label": "Mass", "name": "Exact"}, self.record["props"])
        return float(sval) if sval else None

    @property
    def monoisotopic_mass(self) -> float | None:
        """Monoisotopic mass in Da (Daltons).

        The mass of a molecule calculated using the mass of the most abundant
        isotope of each element. This provides a single, well-defined mass value
        useful for high-resolution mass spectrometry applications.
        """
        sval = _parse_prop(
            {"label": "Weight", "name": "MonoIsotopic"}, self.record["props"]
        )
        return float(sval) if sval else None

    @property
    def tpsa(self) -> float | None:
        """Topological Polar Surface Area (TPSA).

        The topological polar surface area computed using the algorithm described
        by Ertl et al. TPSA is a commonly used descriptor for predicting drug
        absorption, as it correlates well with passive molecular transport through
        membranes. Values are typically expressed in square Ångströms.
        """
        return _parse_prop({"implementation": "E_TPSA"}, self.record["props"])

    @property
    def complexity(self) -> float | None:
        """Molecular complexity rating.

        A measure of molecular complexity computed using the Bertz/Hendrickson/
        Ihlenfeldt formula. This descriptor quantifies the structural complexity
        of a molecule based on factors such as the number of atoms, bonds,
        rings, and branching patterns.
        """
        return _parse_prop({"implementation": "E_COMPLEXITY"}, self.record["props"])

    @property
    def h_bond_donor_count(self) -> int | None:
        """Number of hydrogen-bond donors in the structure.

        Counts functional groups that can donate hydrogen bonds, such as
        -OH, -NH, and -SH groups. This descriptor is important for predicting
        drug-like properties and molecular interactions.
        """
        return _parse_prop({"implementation": "E_NHDONORS"}, self.record["props"])

    @property
    def h_bond_acceptor_count(self) -> int | None:
        """Number of hydrogen-bond acceptors in the structure.

        Counts functional groups that can accept hydrogen bonds, such as
        oxygen and nitrogen atoms with lone pairs. This descriptor is important
        for predicting drug-like properties and molecular interactions.
        """
        return _parse_prop({"implementation": "E_NHACCEPTORS"}, self.record["props"])

    @property
    def rotatable_bond_count(self) -> int | None:
        """Number of rotatable bonds.

        Counts single bonds that can freely rotate, excluding bonds in rings
        and terminal bonds to hydrogen or methyl groups.
        """
        return _parse_prop({"implementation": "E_NROTBONDS"}, self.record["props"])

    @property
    def fingerprint(self) -> str | None:
        """Raw padded and hex-encoded structural fingerprint from PubChem.

        Returns the raw padded and hex-encoded fingerprint as returned by the PUG REST
        API. This is the underlying data used to generate the human-readable binary
        fingerprint via the ``cactvs_fingerprint`` property. Most users should use
        ``cactvs_fingerprint`` instead for substructure analysis and similarity
        calculations.

        The PubChem fingerprint data is 881 bits in length. Binary data is stored in one
        byte increments. This fingerprint is, therefore, 111 bytes in length (888 bits),
        which includes padding of seven bits at the end to complete the last byte. A
        four-byte prefix, containing the bit length of the fingerprint (881 bits),
        increases the stored PubChem fingerprint size to 115 bytes (920 bits). This is
        then hex-encoded, resulting in a 230-character string.

        More information at:
        ftp://ftp.ncbi.nlm.nih.gov/pubchem/specifications/pubchem_fingerprints.txt
        """
        return _parse_prop({"implementation": "E_SCREEN"}, self.record["props"])

    @property
    def cactvs_fingerprint(self) -> str | None:
        """PubChem CACTVS structural fingerprint as 881-bit binary string.

        Returns a binary fingerprint string where each character is a bit representing
        the presence (1) or absence (0) of specific chemical substructures and features.
        The 881-bit fingerprint is organized into sections covering:

        - Section 1: Hierarchical element counts (1-115)
        - Section 2: Rings in a canonical ring set (116-163)
        - Section 3: Simple atom pairs (164-218)
        - Section 4: Simple atom nearest neighbors (219-242)
        - Section 5: Detailed atom neighborhoods (243-707)
        - Section 6: Simple SMARTS patterns (708-881)

        This fingerprint enables efficient substructure searching, similarity
        calculations, and chemical clustering.

        More information at:
        ftp://ftp.ncbi.nlm.nih.gov/pubchem/specifications/pubchem_fingerprints.txt
        """
        # Skip first 4 bytes (contain length of fingerprint) and last 7 bits (padding)
        # then re-pad to 881 bits
        return f"{int(self.fingerprint[8:], 16):020b}"[:-7].zfill(881)

    @property
    def heavy_atom_count(self) -> int | None:
        """Number of heavy atoms (non-hydrogen atoms).

        Counts all atoms in the molecule except hydrogen. This is a basic descriptor of
        molecular size and is used in various chemical calculations and molecular
        property predictions.
        """
        if "count" in self.record and "heavy_atom" in self.record["count"]:
            return self.record["count"]["heavy_atom"]

    @property
    def isotope_atom_count(self) -> int | None:
        """Number of atoms with enriched isotopes.

        Counts atoms that are specified with non-standard isotopes (e.g., ²H, ¹³C). Most
        organic molecules have a value of 0 unless they are isotopically labeled for
        research or analytical purposes.
        """
        if "count" in self.record and "isotope_atom" in self.record["count"]:
            return self.record["count"]["isotope_atom"]

    @property
    def atom_stereo_count(self) -> int | None:
        """Total number of atoms with tetrahedral (sp³) stereochemistry.

        Counts atoms that have tetrahedral stereochemistry. This includes both defined
        and undefined stereocenters in the molecule.
        """
        if "count" in self.record and "atom_chiral" in self.record["count"]:
            return self.record["count"]["atom_chiral"]

    @property
    def defined_atom_stereo_count(self) -> int | None:
        """Number of atoms with defined tetrahedral (sp³) stereochemistry.

        Counts stereocenters where the absolute configuration is explicitly specified
        (e.g. R or S). This excludes stereocenters where the  configuration is unknown
        or unspecified.
        """
        if "count" in self.record and "atom_chiral_def" in self.record["count"]:
            return self.record["count"]["atom_chiral_def"]

    @property
    def undefined_atom_stereo_count(self) -> int | None:
        """Number of atoms with undefined tetrahedral (sp³) stereochemistry.

        Counts stereocenters where the absolute configuration is not specified or is
        unknown. These represent potential stereocenters that could have either R or S
        configuration, but this is not explicitly defined.
        """
        if "count" in self.record and "atom_chiral_undef" in self.record["count"]:
            return self.record["count"]["atom_chiral_undef"]

    @property
    def bond_stereo_count(self) -> int | None:
        """Bond stereocenter count."""
        if "count" in self.record and "bond_chiral" in self.record["count"]:
            return self.record["count"]["bond_chiral"]

    @property
    def defined_bond_stereo_count(self) -> int | None:
        """Defined bond stereocenter count."""
        if "count" in self.record and "bond_chiral_def" in self.record["count"]:
            return self.record["count"]["bond_chiral_def"]

    @property
    def undefined_bond_stereo_count(self) -> int | None:
        """Undefined bond stereocenter count."""
        if "count" in self.record and "bond_chiral_undef" in self.record["count"]:
            return self.record["count"]["bond_chiral_undef"]

    @property
    def covalent_unit_count(self) -> int | None:
        """Covalently-bonded unit count."""
        if "count" in self.record and "covalent_unit" in self.record["count"]:
            return self.record["count"]["covalent_unit"]

    @property
    def volume_3d(self) -> float | None:
        """Analytic volume of the first diverse conformer.

        The 3D molecular volume calculated for the default (first diverse) conformer.
        This descriptor provides information about the space occupied by the molecule in
        three dimensions.
        """
        conf = self.record["coords"][0]["conformers"][0]
        if "data" in conf:
            return _parse_prop({"label": "Shape", "name": "Volume"}, conf["data"])

    @property
    def multipoles_3d(self) -> list[float] | None:
        conf = self.record["coords"][0]["conformers"][0]
        if "data" in conf:
            return _parse_prop({"label": "Shape", "name": "Multipoles"}, conf["data"])

    @property
    def conformer_rmsd_3d(self) -> float | None:
        """Conformer sampling RMSD in Å.

        The root-mean-square deviation of atomic positions between different conformers
        in the conformer model. This measures the structural diversity of the generated
        conformer ensemble.
        """
        coords = self.record["coords"][0]
        if "data" in coords:
            return _parse_prop({"label": "Conformer", "name": "RMSD"}, coords["data"])

    @property
    def effective_rotor_count_3d(self) -> int | None:
        """Number of effective rotors in the 3D structure.

        A count of rotatable bonds that significantly contribute to conformational
        flexibility. This is often less than the total rotatable bond count as it
        excludes rotors that have restricted rotation due to steric or electronic
        effects.
        """
        return _parse_prop(
            {"label": "Count", "name": "Effective Rotor"}, self.record["props"]
        )

    @property
    def pharmacophore_features_3d(self) -> list[str] | None:
        """3D pharmacophore features present in the molecule.

        A list of pharmacophore feature types identified in the 3D structure, such as
        hydrogen bond donors, acceptors, aromatic rings, and hydrophobic regions. These
        features are important for drug-target interactions.
        """
        return _parse_prop(
            {"label": "Features", "name": "Pharmacophore"}, self.record["props"]
        )

    @property
    def mmff94_partial_charges_3d(self) -> list[str] | None:
        return _parse_prop(
            {"label": "Charge", "name": "MMFF94 Partial"}, self.record["props"]
        )

    @property
    def mmff94_energy_3d(self) -> float | None:
        conf = self.record["coords"][0]["conformers"][0]
        if "data" in conf:
            return _parse_prop(
                {"label": "Energy", "name": "MMFF94 NoEstat"}, conf["data"]
            )

    @property
    def conformer_id_3d(self) -> str | None:
        conf = self.record["coords"][0]["conformers"][0]
        if "data" in conf:
            return _parse_prop({"label": "Conformer", "name": "ID"}, conf["data"])

    @property
    def shape_selfoverlap_3d(self) -> float | None:
        conf = self.record["coords"][0]["conformers"][0]
        if "data" in conf:
            return _parse_prop({"label": "Shape", "name": "Self Overlap"}, conf["data"])

    @property
    def feature_selfoverlap_3d(self) -> float | None:
        conf = self.record["coords"][0]["conformers"][0]
        if "data" in conf:
            return _parse_prop(
                {"label": "Feature", "name": "Self Overlap"}, conf["data"]
            )

    @property
    def shape_fingerprint_3d(self) -> list[str] | None:
        conf = self.record["coords"][0]["conformers"][0]
        if "data" in conf:
            return _parse_prop({"label": "Fingerprint", "name": "Shape"}, conf["data"])


def _parse_prop(search: dict[str, str], proplist: list[dict[str, t.Any]]) -> t.Any:
    """Extract property value from record using the given urn search filter."""
    props = [
        i for i in proplist if all(item in i["urn"].items() for item in search.items())
    ]
    if len(props) > 0:
        return props[0]["value"][list(props[0]["value"].keys())[0]]


class Substance:
    """Represents a raw chemical record as originally deposited to PubChem.

    The PubChem Substance database contains chemical records in their original deposited
    form, before standardization or processing. As a result, it contains duplicates,
    mixtures, and some records that don't make chemical sense. This means that Substance
    records contain fewer calculated properties, however they do have additional
    information about the original source that deposited the record.

    During PubChem's standardization process, Substances are processed to create
    standardized Compound records. Multiple Substances may map to the same Compound
    if they represent the same unique chemical structure. Some Substances may not
    map to any Compound if they cannot be standardized.

    Examples:
        >>> substance = Substance.from_sid(12345)
        >>> print(f"Source: {substance.source_name}")
        Source: KEGG
        >>> print(f"Depositor ID: {substance.source_id}")
        Depositor ID: C10159
        >>> print(f"Standardized to CID: {substance.standardized_cid}")
        Standardized to CID: 169683
    """

    def __init__(self, record: dict[str, t.Any]) -> None:
        """Initialize a Substance with a record dict from the PubChem PUG REST service.

        Args:
            record: Substance record returned by the PubChem PUG REST service.

        Note:
            Most users will not need to instantiate a Substance instance directly from a
            record. The :meth:`from_sid()` class method and the
            :func:`~get_substances()` function offer more convenient ways to obtain
            Substance instances, as they also handle the retrieval of the record from
            PubChem.
        """
        self._record = record

    @classmethod
    def from_sid(cls, sid: int, **kwargs: QueryParam) -> Substance:
        """Retrieve the Substance record for the specified SID.

        Args:
            sid: The PubChem Substance Identifier (SID).
            **kwargs: Additional parameters to pass to the request.

        Example:
            s = Substance.from_sid(12345)
        """
        response = request(sid, "sid", "substance", **kwargs).read().decode()
        record = json.loads(response)["PC_Substances"][0]
        return cls(record)

    @property
    def record(self) -> dict[str, t.Any]:
        """The full substance record returned by the PubChem PUG REST service."""
        return self._record

    def __repr__(self) -> str:
        return f"Substance({self.sid if self.sid else ''})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.record == other.record

    def to_dict(self, properties: list[str] | None = None) -> dict[str, t.Any]:
        """Return a dict containing Substance property data.

        Optionally specify a list of the desired properties to include. If
        ``properties`` is not specified, all properties are included, with the following
        exceptions:

        :attr:`cids` and :attr:`aids` are not included unless explicitly specified. This
        is because they each require an extra request to the PubChem API to retrieve.

        Args:
            properties: List of desired properties.

        Returns:
            Dictionary of substance data.
        """
        if not properties:
            skip = {
                "record",
                "deposited_compound",
                "standardized_compound",
                "cids",
                "aids",
            }
            properties = [
                p
                for p, v in Substance.__dict__.items()
                if isinstance(v, property) and p not in skip
            ]
        return {p: getattr(self, p) for p in properties}

    def to_series(self, properties: list[str] | None = None) -> pd.Series:
        """Return a pandas :class:`~pandas.Series` containing Substance data.

        Optionally specify a list of the desired properties to include as columns. If
        ``properties`` is not specified, all properties are included, with the following
        exceptions:

        :attr:`cids` and :attr:`aids` are not included unless explicitly specified. This
        is because they each require an extra request to the PubChem API to retrieve.

        Args:
            properties: List of desired properties.
        """
        import pandas as pd

        return pd.Series(self.to_dict(properties))

    @property
    def sid(self) -> int:
        """The PubChem Substance Idenfitier (SID)."""
        return self.record["sid"]["id"]

    @property
    def synonyms(self) -> list[str] | None:
        """A ranked list of all the names associated with this Substance."""
        if "synonyms" in self.record:
            return self.record["synonyms"]

    @property
    def source_name(self) -> str:
        """The name of the PubChem depositor that was the source of this Substance."""
        return self.record["source"]["db"]["name"]

    @property
    def source_id(self) -> str:
        """Unique ID for this Substance from the PubChem depositor source."""
        return self.record["source"]["db"]["source_id"]["str"]

    @property
    def standardized_cid(self) -> int | None:
        """The CID of the Compound that was standardized from this Substance.

        May not exist if this Substance was not standardizable.
        """
        for c in self.record.get("compound", []):
            if c["id"]["type"] == CompoundIdType.STANDARDIZED:
                return c["id"]["id"]["cid"]

    @memoized_property
    def standardized_compound(self) -> Compound | None:
        """The :class:`~pubchempy.Compound` that was standardized from this Substance.

        Requires an extra request. Result is cached. May not exist if this Substance was
        not standardizable.
        """
        cid = self.standardized_cid
        if cid:
            return Compound.from_cid(cid)

    @property
    def deposited_compound(self) -> Compound | None:
        """A :class:`~pubchempy.Compound` derived from the unstandardized Substance.

        This :class:`~pubchempy.Compound` is produced from the unstandardized Substance
        record as deposited. It will not have a ``cid`` and will be missing most
        properties.
        """
        for c in self.record.get("compound", []):
            if c["id"]["type"] == CompoundIdType.DEPOSITED:
                return Compound(c)

    @memoized_property
    def cids(self) -> list[int]:
        """A list of all CIDs for Compounds that were standardized from this Substance.

        Requires an extra request. Result is cached.
        """
        results = get_json(self.sid, "sid", "substance", "cids")
        return results["InformationList"]["Information"][0]["CID"] if results else []

    @memoized_property
    def aids(self) -> list[int]:
        """A list of all AIDs for Assays associated with this Substance.

        Requires an extra request. Result is cached.
        """
        results = get_json(self.sid, "sid", "substance", "aids")
        return results["InformationList"]["Information"][0]["AID"] if results else []


class Assay:
    """Represents a biological assay record from the PubChem BioAssay database.

    The PubChem BioAssay database contains experimental data from biological screening
    and testing programs. Each assay record describes the experimental conditions,
    methodology, and results for testing chemical compounds against biological targets.

    BioAssay records include:

    - Assay protocol and experimental conditions
    - Target information (proteins, genes, pathways)
    - Activity outcome definitions and thresholds
    - Results data linking compounds to biological activities
    - Source information and literature references

    Assays are identified by their AID (Assay Identifier) and can be retrieved
    using the ``from_aid()`` class method. The assay data provides the experimental
    context for understanding compound bioactivity data stored in PubChem.
    """

    def __init__(self, record: dict[str, t.Any]) -> None:
        """Initialize an Assay with a record dict from the PubChem PUG REST service.

        Args:
            record: Assay record returned by the PubChem PUG REST service.

        Note:
            Most users will not need to instantiate an Assay instance directly from a
            record. The :meth:`from_aid()` class method and the :func:`~get_assays()`
            function offer more convenient ways to obtain Assay instances, as they
            also handle the retrieval of the record from PubChem.
        """
        self._record = record

    @classmethod
    def from_aid(cls, aid: int, **kwargs: QueryParam) -> Assay:
        """Retrieve the Assay record for the specified AID.

        Args:
            aid: The PubChem Assay Identifier (AID).
            **kwargs: Additional parameters to pass to the request.

        Example:
            a = Assay.from_aid(1234)
        """
        response = request(aid, "aid", "assay", "description", **kwargs).read().decode()
        record = json.loads(response)["PC_AssayContainer"][0]
        return cls(record)

    @property
    def record(self) -> dict[str, t.Any]:
        """The full assay record returned by the PubChem PUG REST service."""
        return self._record

    def __repr__(self) -> str:
        return f"Assay({self.aid if self.aid else ''})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.record == other.record

    def to_dict(self, properties: list[str] | None = None) -> dict[str, t.Any]:
        """Return a dict containing Assay property data.

        Optionally specify a list of the desired properties to include. If
        ``properties`` is not specified, all properties are included.

        Args:
            properties: List of desired properties.

        Returns:
            Dictionary of assay data.
        """
        if not properties:
            skip = {"record"}
            properties = [
                p
                for p, v in Assay.__dict__.items()
                if isinstance(v, property) and p not in skip
            ]
        return {p: getattr(self, p) for p in properties}

    @property
    def aid(self) -> int:
        """The PubChem Assay Idenfitier (AID)."""
        return self.record["assay"]["descr"]["aid"]["id"]

    @property
    def name(self) -> str:
        """The short assay name, used for display purposes."""
        return self.record["assay"]["descr"]["name"]

    @property
    def description(self) -> str:
        """Description."""
        return self.record["assay"]["descr"]["description"]

    @property
    def project_category(self) -> ProjectCategory | None:
        """Category to distinguish projects funded through MLSCN, MLPCN or other.

        Possible values include mlscn, mlpcn, mlscn-ap, mlpcn-ap, literature-extracted,
        literature-author, literature-publisher, rnaigi.
        """
        if "project_category" in self.record["assay"]["descr"]:
            return ProjectCategory(self.record["assay"]["descr"]["project_category"])

    @property
    def comments(self) -> list[str]:
        """Comments and additional information."""
        return [
            comment for comment in self.record["assay"]["descr"]["comment"] if comment
        ]

    @property
    def results(self) -> list[dict[str, t.Any]]:
        """A list of dictionaries containing details of the results from this Assay."""
        return self.record["assay"]["descr"]["results"]

    @property
    def target(self) -> list[dict[str, t.Any]] | None:
        """A list of dictionaries containing details of the Assay targets."""
        if "target" in self.record["assay"]["descr"]:
            return self.record["assay"]["descr"]["target"]

    @property
    def revision(self) -> int:
        """Revision identifier for textual description."""
        return self.record["assay"]["descr"]["revision"]

    @property
    def aid_version(self) -> int:
        """Incremented when the original depositor updates the record."""
        return self.record["assay"]["descr"]["aid"]["version"]


def compounds_to_frame(
    compounds: list[Compound] | Compound, properties: list[str] | None = None
) -> pd.DataFrame:
    """Create a :class:`~pandas.DataFrame` from a :class:`~pubchempy.Compound` list.

    Optionally specify the desired :class:`~pubchempy.Compound` properties to include as
    columns in the pandas DataFrame.
    """
    import pandas as pd

    if isinstance(compounds, Compound):
        compounds = [compounds]
    properties = set(properties) | {"cid"} if properties else None
    return pd.DataFrame.from_records(
        [c.to_dict(properties) for c in compounds], index="cid"
    )


def substances_to_frame(
    substances: list[Substance] | Substance, properties: list[str] | None = None
) -> pd.DataFrame:
    """Create a :class:`~pandas.DataFrame` from a :class:`~pubchempy.Substance` list.

    Optionally specify a list of the desired :class:`~pubchempy.Substance` properties to
    include as columns in the pandas DataFrame.
    """
    import pandas as pd

    if isinstance(substances, Substance):
        substances = [substances]
    properties = set(properties) | {"sid"} if properties else None
    return pd.DataFrame.from_records(
        [s.to_dict(properties) for s in substances], index="sid"
    )


class PubChemPyDeprecationWarning(Warning):
    """Warning category for deprecated features."""


class PubChemPyError(Exception):
    """Base class for all PubChemPy exceptions."""


class ResponseParseError(PubChemPyError):
    """PubChem response is uninterpretable."""


class PubChemHTTPError(PubChemPyError):
    """Generic error class to handle HTTP error codes."""

    def __init__(self, code: int, msg: str, details: list[str]) -> None:
        """Initialize with HTTP status code, message, and additional details.

        Args:
            code: HTTP status code.
            msg: Error message.
            details: Additional error details from PubChem API.
        """
        super().__init__(msg)
        self.code = code
        self.msg = msg
        self.details = details

    def __str__(self) -> str:
        output = f"PubChem HTTP Error {self.code} {self.msg}"
        if self.details:
            details = ", ".join(self.details)
            output = f"{output} ({details})"
        return output

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.code!r}, {self.msg!r}, {self.details!r})"
        )


def create_http_error(e: HTTPError) -> PubChemHTTPError:
    """Create appropriate PubChem HTTP error subclass based on status code."""
    code = e.code
    msg = e.msg
    details = []
    try:
        fault = json.loads(e.read().decode())["Fault"]
        msg = fault.get("Code", msg)
        if "Message" in fault:
            msg = f"{msg}: {fault['Message']}"
        details = fault.get("Details", [])
    except (ValueError, IndexError, KeyError):
        pass

    error_map = {
        400: BadRequestError,
        404: NotFoundError,
        405: MethodNotAllowedError,
        500: ServerError,
        501: UnimplementedError,
        503: ServerBusyError,
        504: TimeoutError,
    }
    error_class = error_map.get(code, PubChemHTTPError)
    return error_class(code, msg, details)


class BadRequestError(PubChemHTTPError):
    """400: Request is improperly formed (e.g. syntax error in the URL or POST body)."""


class NotFoundError(PubChemHTTPError):
    """404: The input record was not found (e.g. invalid CID)."""


class MethodNotAllowedError(PubChemHTTPError):
    """405: Request not allowed (e.g. invalid MIME type in the HTTP Accept header)."""


class ServerError(PubChemHTTPError):
    """500: Some problem on the server side (e.g. a database server down)."""


class UnimplementedError(PubChemHTTPError):
    """501: The requested operation has not (yet) been implemented by the server."""


class ServerBusyError(PubChemHTTPError):
    """503: Too many requests or server is busy, retry later."""


class TimeoutError(PubChemHTTPError):
    """504: The request timed out, from server overload or too broad a request.

    See :ref:`Avoiding TimeoutError <avoiding_timeouterror>` for more information.
    """


if __name__ == "__main__":
    print(__version__)
