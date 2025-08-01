"""
PubChemPy

Python interface for the PubChem PUG REST service.
https://github.com/mcs07/PubChemPy
"""

import enum
import functools
import json
import logging
import os
import ssl
import time
import warnings
from itertools import zip_longest
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import urlopen

# Get SSL certs from env var or certifi package if available.
_CA_FILE = os.getenv("PUBCHEMPY_CA_BUNDLE") or os.getenv("REQUESTS_CA_BUNDLE")
if not _CA_FILE:
    try:
        import certifi
        _CA_FILE = certifi.where()
    except ImportError:
        _CA_FILE = None


__author__ = 'Matt Swain'
__email__ = 'm.swain@me.com'
__version__ = '1.0.4'
__license__ = 'MIT'

__all__ = [
    # Main API functions
    'get_compounds',
    'get_substances',
    'get_assays',
    'get_properties',
    'get_synonyms',
    'get_cids',
    'get_sids',
    'get_aids',
    'get_all_sources',
    'download',
    'request',
    'get',
    'get_json',
    'get_sdf',

    # Core classes
    'Compound',
    'Substance',
    'Assay',
    'Atom',
    'Bond',

    # Enum/constant classes
    'CompoundIdType',
    'BondType',
    'CoordinateType',
    'ProjectCategory',

    # Data conversion functions
    'compounds_to_frame',
    'substances_to_frame',

    # Constants
    'API_BASE',
    'ELEMENTS',
    'PROPERTY_MAP',

    # Exceptions
    'PubChemPyError',
    'ResponseParseError',
    'PubChemHTTPError',
    'BadRequestError',
    'NotFoundError',
    'MethodNotAllowedError',
    'ServerError',
    'UnimplementedError',
    'ServerBusyError',
    'TimeoutError',
    'PubChemPyDeprecationWarning',
]

#: Base URL for the PubChem PUG REST API.
API_BASE = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'

log = logging.getLogger('pubchempy')
log.addHandler(logging.NullHandler())


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
    """Coordinate Set Type Distinctions"""
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
    MPLCN = 2
    #: Assay depositions from MLSCN assay provider
    MLSCN_AP = 3
    #: Assay depositions from MLPCN assay provider
    MPLCN_AP = 4
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
ELEMENTS = {
    # Standard chemical elements
    1: 'H',  # Hydrogen
    2: 'He',  # Helium
    3: 'Li',  # Lithium
    4: 'Be',  # Beryllium
    5: 'B',  # Boron
    6: 'C',  # Carbon
    7: 'N',  # Nitrogen
    8: 'O',  # Oxygen
    9: 'F',  # Fluorine
    10: 'Ne',  # Neon
    11: 'Na',  # Sodium
    12: 'Mg',  # Magnesium
    13: 'Al',  # Aluminium
    14: 'Si',  # Silicon
    15: 'P',  # Phosphorus
    16: 'S',  # Sulfur
    17: 'Cl',  # Chlorine
    18: 'Ar',  # Argon
    19: 'K',  # Potassium
    20: 'Ca',  # Calcium
    21: 'Sc',  # Scandium
    22: 'Ti',  # Titanium
    23: 'V',  # Vanadium
    24: 'Cr',  # Chromium
    25: 'Mn',  # Manganese
    26: 'Fe',  # Iron
    27: 'Co',  # Cobalt
    28: 'Ni',  # Nickel
    29: 'Cu',  # Copper
    30: 'Zn',  # Zinc
    31: 'Ga',  # Gallium
    32: 'Ge',  # Germanium
    33: 'As',  # Arsenic
    34: 'Se',  # Selenium
    35: 'Br',  # Bromine
    36: 'Kr',  # Krypton
    37: 'Rb',  # Rubidium
    38: 'Sr',  # Strontium
    39: 'Y',  # Yttrium
    40: 'Zr',  # Zirconium
    41: 'Nb',  # Niobium
    42: 'Mo',  # Molybdenum
    43: 'Tc',  # Technetium
    44: 'Ru',  # Ruthenium
    45: 'Rh',  # Rhodium
    46: 'Pd',  # Palladium
    47: 'Ag',  # Silver
    48: 'Cd',  # Cadmium
    49: 'In',  # Indium
    50: 'Sn',  # Tin
    51: 'Sb',  # Antimony
    52: 'Te',  # Tellurium
    53: 'I',  # Iodine
    54: 'Xe',  # Xenon
    55: 'Cs',  # Cesium
    56: 'Ba',  # Barium
    57: 'La',  # Lanthanum
    58: 'Ce',  # Cerium
    59: 'Pr',  # Praseodymium
    60: 'Nd',  # Neodymium
    61: 'Pm',  # Promethium
    62: 'Sm',  # Samarium
    63: 'Eu',  # Europium
    64: 'Gd',  # Gadolinium
    65: 'Tb',  # Terbium
    66: 'Dy',  # Dysprosium
    67: 'Ho',  # Holmium
    68: 'Er',  # Erbium
    69: 'Tm',  # Thulium
    70: 'Yb',  # Ytterbium
    71: 'Lu',  # Lutetium
    72: 'Hf',  # Hafnium
    73: 'Ta',  # Tantalum
    74: 'W',  # Tungsten
    75: 'Re',  # Rhenium
    76: 'Os',  # Osmium
    77: 'Ir',  # Iridium
    78: 'Pt',  # Platinum
    79: 'Au',  # Gold
    80: 'Hg',  # Mercury
    81: 'Tl',  # Thallium
    82: 'Pb',  # Lead
    83: 'Bi',  # Bismuth
    84: 'Po',  # Polonium
    85: 'At',  # Astatine
    86: 'Rn',  # Radon
    87: 'Fr',  # Francium
    88: 'Ra',  # Radium
    89: 'Ac',  # Actinium
    90: 'Th',  # Thorium
    91: 'Pa',  # Protactinium
    92: 'U',  # Uranium
    93: 'Np',  # Neptunium
    94: 'Pu',  # Plutonium
    95: 'Am',  # Americium
    96: 'Cm',  # Curium
    97: 'Bk',  # Berkelium
    98: 'Cf',  # Californium
    99: 'Es',  # Einsteinium
    100: 'Fm',  # Fermium
    101: 'Md',  # Mendelevium
    102: 'No',  # Nobelium
    103: 'Lr',  # Lawrencium
    104: 'Rf',  # Rutherfordium
    105: 'Db',  # Dubnium
    106: 'Sg',  # Seaborgium
    107: 'Bh',  # Bohrium
    108: 'Hs',  # Hassium
    109: 'Mt',  # Meitnerium
    110: 'Ds',  # Darmstadtium
    111: 'Rg',  # Roentgenium
    112: 'Cn',  # Copernicium
    113: 'Nh',  # Nihonium
    114: 'Fl',  # Flerovium
    115: 'Mc',  # Moscovium
    116: 'Lv',  # Livermorium
    117: 'Ts',  # Tennessine
    118: 'Og',  # Oganesson

    # Special atom types
    252: 'Lp',  # Lone Pair
    253: 'R',  # Rgroup Label
    254: '*',  # Dummy Atom
    255: '*',  # Unspecified Atom (Asterisk)
}


def request(identifier, namespace='cid', domain='compound', operation=None, output='JSON', searchtype=None, **kwargs):
    """
    Construct API request from parameters and return the response.

    Full specification at https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
    """
    if not identifier:
        raise ValueError('identifier/cid cannot be None')
    # If identifier is a list, join with commas into string
    if isinstance(identifier, int):
        identifier = str(identifier)
    if not isinstance(identifier, str):
        identifier = ','.join(str(x) for x in identifier)
    # Filter None values from kwargs
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    # Build API URL
    urlid, postdata = None, None
    if namespace == 'sourceid':
        identifier = identifier.replace('/', '.')
    if namespace in ['listkey', 'formula', 'sourceid'] \
            or searchtype == 'xref' \
            or (searchtype and namespace == 'cid') or domain == 'sources':
        urlid = quote(identifier.encode('utf8'))
    else:
        postdata = urlencode([(namespace, identifier)]).encode('utf8')
    comps = filter(None, [API_BASE, domain, searchtype, namespace, urlid, operation, output])
    apiurl = '/'.join(comps)
    if kwargs:
        apiurl += f'?{urlencode(kwargs)}'
    # Make request
    try:
        log.debug(f'Request URL: {apiurl}')
        log.debug(f'Request data: {postdata}')
        context = ssl.create_default_context(cafile=_CA_FILE)
        response = urlopen(apiurl, postdata, context=context)
        return response
    except HTTPError as e:
        raise create_http_error(e) from e


def get(identifier, namespace='cid', domain='compound', operation=None, output='JSON', searchtype=None, **kwargs):
    """Request wrapper that automatically handles async requests."""
    if (searchtype and searchtype != 'xref') or namespace in ['formula']:
        response = request(identifier, namespace, domain, None, 'JSON', searchtype, **kwargs).read()
        status = json.loads(response.decode())
        if 'Waiting' in status and 'ListKey' in status['Waiting']:
            identifier = status['Waiting']['ListKey']
            namespace = 'listkey'
            while 'Waiting' in status and 'ListKey' in status['Waiting']:
                time.sleep(2)
                response = request(identifier, namespace, domain, operation, 'JSON', **kwargs).read()
                status = json.loads(response.decode())
            if not output == 'JSON':
                response = request(identifier, namespace, domain, operation, output, searchtype, **kwargs).read()
    else:
        response = request(identifier, namespace, domain, operation, output, searchtype, **kwargs).read()
    return response


def get_json(identifier, namespace='cid', domain='compound', operation=None, searchtype=None, **kwargs):
    """Request wrapper that automatically parses JSON response and supresses NotFoundError."""
    try:
        return json.loads(get(identifier, namespace, domain, operation, 'JSON', searchtype, **kwargs).decode())
    except NotFoundError as e:
        log.info(e)
        return None

def get_sdf(identifier, namespace='cid', domain='compound',operation=None, searchtype=None, **kwargs):
    """Request wrapper that automatically parses SDF response and supresses NotFoundError."""
    try:
        return get(identifier, namespace, domain, operation, 'SDF', searchtype, **kwargs).decode()
    except NotFoundError as e:
        log.info(e)
        return None

def get_compounds(identifier, namespace='cid', searchtype=None, as_dataframe=False, **kwargs):
    """Retrieve the specified compound records from PubChem.

    :param identifier: The compound identifier to use as a search query.
    :param namespace: (optional) The identifier type, one of cid, name, smiles, sdf, inchi, inchikey or formula.
    :param searchtype: (optional) The advanced search type, one of substructure, superstructure or similarity.
    :param as_dataframe: (optional) Automatically extract the :class:`~pubchempy.Compound` properties into a pandas
                         :class:`~pandas.DataFrame` and return that.
    """
    results = get_json(identifier, namespace, searchtype=searchtype, **kwargs)
    compounds = [Compound(r) for r in results['PC_Compounds']] if results else []
    if as_dataframe:
        return compounds_to_frame(compounds)
    return compounds


def get_substances(identifier, namespace='sid', as_dataframe=False, **kwargs):
    """Retrieve the specified substance records from PubChem.

    :param identifier: The substance identifier to use as a search query.
    :param namespace: (optional) The identifier type, one of sid, name or sourceid/<source name>.
    :param as_dataframe: (optional) Automatically extract the :class:`~pubchempy.Substance` properties into a pandas
                         :class:`~pandas.DataFrame` and return that.
    """
    results = get_json(identifier, namespace, 'substance', **kwargs)
    substances = [Substance(r) for r in results['PC_Substances']] if results else []
    if as_dataframe:
        return substances_to_frame(substances)
    return substances


def get_assays(identifier, namespace='aid', **kwargs):
    """Retrieve the specified assay records from PubChem.

    :param identifier: The assay identifier to use as a search query.
    :param namespace: (optional) The identifier type.
    """
    results = get_json(identifier, namespace, 'assay', 'description', **kwargs)
    return [Assay(r) for r in results['PC_AssayContainer']] if results else []


#: Allows properties to optionally be specified as underscore_separated, consistent with Compound attributes.
PROPERTY_MAP = {
    'molecular_formula': 'MolecularFormula',
    'molecular_weight': 'MolecularWeight',
    'smiles': 'SMILES',
    'connectivity_smiles': 'ConnectivitySMILES',
    'canonical_smiles': 'CanonicalSMILES',
    'isomeric_smiles': 'IsomericSMILES',
    'inchi': 'InChI',
    'inchikey': 'InChIKey',
    'iupac_name': 'IUPACName',
    'xlogp': 'XLogP',
    'exact_mass': 'ExactMass',
    'monoisotopic_mass': 'MonoisotopicMass',
    'tpsa': 'TPSA',
    'complexity': 'Complexity',
    'charge': 'Charge',
    'h_bond_donor_count': 'HBondDonorCount',
    'h_bond_acceptor_count': 'HBondAcceptorCount',
    'rotatable_bond_count': 'RotatableBondCount',
    'heavy_atom_count': 'HeavyAtomCount',
    'isotope_atom_count': 'IsotopeAtomCount',
    'atom_stereo_count': 'AtomStereoCount',
    'defined_atom_stereo_count': 'DefinedAtomStereoCount',
    'undefined_atom_stereo_count': 'UndefinedAtomStereoCount',
    'bond_stereo_count': 'BondStereoCount',
    'defined_bond_stereo_count': 'DefinedBondStereoCount',
    'undefined_bond_stereo_count': 'UndefinedBondStereoCount',
    'covalent_unit_count': 'CovalentUnitCount',
    'volume_3d': 'Volume3D',
    'conformer_rmsd_3d': 'ConformerModelRMSD3D',
    'conformer_model_rmsd_3d': 'ConformerModelRMSD3D',
    'x_steric_quadrupole_3d': 'XStericQuadrupole3D',
    'y_steric_quadrupole_3d': 'YStericQuadrupole3D',
    'z_steric_quadrupole_3d': 'ZStericQuadrupole3D',
    'feature_count_3d': 'FeatureCount3D',
    'feature_acceptor_count_3d': 'FeatureAcceptorCount3D',
    'feature_donor_count_3d': 'FeatureDonorCount3D',
    'feature_anion_count_3d': 'FeatureAnionCount3D',
    'feature_cation_count_3d': 'FeatureCationCount3D',
    'feature_ring_count_3d': 'FeatureRingCount3D',
    'feature_hydrophobe_count_3d': 'FeatureHydrophobeCount3D',
    'effective_rotor_count_3d': 'EffectiveRotorCount3D',
    'conformer_count_3d': 'ConformerCount3D',
}


def get_properties(properties, identifier, namespace='cid', searchtype=None, as_dataframe=False, **kwargs):
    """Retrieve the specified properties from PubChem.

    :param identifier: The compound, substance or assay identifier to use as a search query.
    :param namespace: (optional) The identifier type.
    :param searchtype: (optional) The advanced search type, one of substructure, superstructure or similarity.
    :param as_dataframe: (optional) Automatically extract the properties into a pandas :class:`~pandas.DataFrame`.
    """
    if isinstance(properties, str):
        properties = properties.split(',')
    properties = ','.join([PROPERTY_MAP.get(p, p) for p in properties])
    properties = f'property/{properties}'
    results = get_json(identifier, namespace, 'compound', properties, searchtype=searchtype, **kwargs)
    results = results['PropertyTable']['Properties'] if results else []
    if as_dataframe:
        import pandas as pd
        return pd.DataFrame.from_records(results, index='CID')
    return results


def get_synonyms(identifier, namespace='cid', domain='compound', searchtype=None, **kwargs):
    results = get_json(identifier, namespace, domain, 'synonyms', searchtype=searchtype, **kwargs)
    return results['InformationList']['Information'] if results else []


def get_cids(identifier, namespace='name', domain='compound', searchtype=None, **kwargs):
    results = get_json(identifier, namespace, domain, 'cids', searchtype=searchtype, **kwargs)
    if not results:
        return []
    elif 'IdentifierList' in results:
        return results['IdentifierList']['CID']
    elif 'InformationList' in results:
        return results['InformationList']['Information']


def get_sids(identifier, namespace='cid', domain='compound', searchtype=None, **kwargs):
    results = get_json(identifier, namespace, domain, 'sids', searchtype=searchtype, **kwargs)
    if not results:
        return []
    elif 'IdentifierList' in results:
        return results['IdentifierList']['SID']
    elif 'InformationList' in results:
        return results['InformationList']['Information']


def get_aids(identifier, namespace='cid', domain='compound', searchtype=None, **kwargs):
    results = get_json(identifier, namespace, domain, 'aids', searchtype=searchtype, **kwargs)
    if not results:
        return []
    elif 'IdentifierList' in results:
        return results['IdentifierList']['AID']
    elif 'InformationList' in results:
        return results['InformationList']['Information']


def get_all_sources(domain='substance'):
    """Return a list of all current depositors of substances or assays."""
    results = json.loads(get(domain, None, 'sources').decode())
    return results['InformationList']['SourceName']


def download(outformat, path, identifier, namespace='cid', domain='compound', operation=None, searchtype=None,
             overwrite=False, **kwargs):
    """Format can be  XML, ASNT/B, JSON, SDF, CSV, PNG, TXT."""
    response = get(identifier, namespace, domain, operation, outformat, searchtype, **kwargs)
    if not overwrite and os.path.isfile(path):
        raise OSError(f"{path} already exists. Use 'overwrite=True' to overwrite it.")
    with open(path, 'wb') as f:
        f.write(response)


def memoized_property(fget):
    """Decorator to create memoized properties.

    Used to cache :class:`~pubchempy.Compound` and :class:`~pubchempy.Substance` properties that require an additional
    request.
    """
    attr_name = f'_{fget.__name__}'

    @functools.wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)
    return property(fget_memoized)


def deprecated(message):
    """Decorator to mark as deprecated and emit a warning when used."""
    def deco(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            warnings.warn(
                f'{func.__name__} is deprecated: {message}',
                category=PubChemPyDeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapped
    return deco


class Atom:
    """Class to represent an atom in a :class:`~pubchempy.Compound`."""

    def __init__(self, aid, number, x=None, y=None, z=None, charge=0):
        """Initialize with an atom ID, atomic number, coordinates and optional change.

        :param int aid: Atom ID
        :param int number: Atomic number
        :param float x: X coordinate.
        :param float y: Y coordinate.
        :param float z: (optional) Z coordinate.
        :param int charge: (optional) Formal charge on atom.
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

    def __repr__(self):
        return f'Atom({self.aid!r}, {self.element!r})'

    def __eq__(self, other):
        return (isinstance(other, type(self)) and self.aid == other.aid and self.element == other.element and
                self.x == other.x and self.y == other.y and self.z == other.z and self.charge == other.charge)

    @deprecated('Dictionary style access to Atom attributes is deprecated')
    def __getitem__(self, prop):
        """Allow dict-style access to attributes to ease transition from when atoms were dicts."""
        if prop in {'element', 'x', 'y', 'z', 'charge'}:
            return getattr(self, prop)
        raise KeyError(prop)

    @deprecated('Dictionary style access to Atom attributes is deprecated')
    def __setitem__(self, prop, val):
        """Allow dict-style setting of attributes to ease transition from when atoms were dicts."""
        setattr(self, prop, val)

    @deprecated('Dictionary style access to Atom attributes is deprecated')
    def __contains__(self, prop):
        """Allow dict-style checking of attributes to ease transition from when atoms were dicts."""
        if prop in {'element', 'x', 'y', 'z', 'charge'}:
            return getattr(self, prop) is not None
        return False

    @property
    def element(self):
        """The element symbol for this atom."""
        return ELEMENTS.get(self.number, str(self.number))

    def to_dict(self):
        """Return a dictionary containing Atom data."""
        data = {'aid': self.aid, 'number': self.number, 'element': self.element}
        for coord in {'x', 'y', 'z'}:
            if getattr(self, coord) is not None:
                data[coord] = getattr(self, coord)
        if self.charge != 0:
            data['charge'] = self.charge
        return data

    def set_coordinates(self, x, y, z=None):
        """Set all coordinate dimensions at once."""
        self.x = x
        self.y = y
        self.z = z

    @property
    def coordinate_type(self):
        """Whether this atom has 2D or 3D coordinates."""
        return '2d' if self.z is None else '3d'


class Bond:
    """Class to represent a bond between two atoms in a :class:`~pubchempy.Compound`."""

    def __init__(self, aid1, aid2, order=BondType.SINGLE, style=None):
        """Initialize with begin and end atom IDs, bond order and bond style.

        :param int aid1: Begin atom ID.
        :param int aid2: End atom ID.
        :param int order: Bond order.
        """
        self.aid1 = aid1
        """ID of the begin atom of this bond."""
        self.aid2 = aid2
        """ID of the end atom of this bond."""
        self.order = order
        """Bond order."""
        self.style = style
        """Bond style annotation."""

    def __repr__(self):
        return f'Bond({self.aid1!r}, {self.aid2!r}, {self.order!r})'

    def __eq__(self, other):
        return (isinstance(other, type(self)) and self.aid1 == other.aid1 and self.aid2 == other.aid2 and
                self.order == other.order and self.style == other.style)

    @deprecated('Dictionary style access to Bond attributes is deprecated')
    def __getitem__(self, prop):
        """Allow dict-style access to attributes to ease transition from when bonds were dicts."""
        if prop in {'order', 'style'}:
            return getattr(self, prop)
        raise KeyError(prop)

    @deprecated('Dictionary style access to Bond attributes is deprecated')
    def __setitem__(self, prop, val):
        """Allow dict-style setting of attributes to ease transition from when bonds were dicts."""
        setattr(self, prop, val)

    @deprecated('Dictionary style access to Atom attributes is deprecated')
    def __contains__(self, prop):
        """Allow dict-style checking of attributes to ease transition from when bonds were dicts."""
        if prop in {'order', 'style'}:
            return getattr(self, prop) is not None
        return False

    @deprecated('Dictionary style access to Atom attributes is deprecated')
    def __delitem__(self, prop):
        """Delete the property prop from the wrapped object."""
        if not hasattr(self.__wrapped, prop):
            raise KeyError(prop)
        delattr(self.__wrapped, prop)

    def to_dict(self):
        """Return a dictionary containing Bond data."""
        data = {'aid1': self.aid1, 'aid2': self.aid2, 'order': self.order}
        if self.style is not None:
            data['style'] = self.style
        return data


class Compound:
    """Corresponds to a single record from the PubChem Compound database.

    The PubChem Compound database is constructed from the Substance database using a standardization and deduplication
    process. Each Compound is uniquely identified by a CID.
    """
    def __init__(self, record):
        """Initialize with a record dict from the PubChem PUG REST service.

        For most users, the ``from_cid()`` class method is probably a better way of creating Compounds.

        :param dict record: A compound record returned by the PubChem PUG REST service.
        """
        self._record = None
        self._atoms = {}
        self._bonds = {}
        self.record = record

    @property
    def record(self):
        """The raw compound record returned by the PubChem PUG REST service."""
        return self._record

    @record.setter
    def record(self, record):
        self._record = record
        log.debug(f'Created {self}')
        self._setup_atoms()
        self._setup_bonds()

    def _setup_atoms(self):
        """Derive Atom objects from the record."""
        # Delete existing atoms
        self._atoms = {}
        # Create atoms
        aids = self.record['atoms']['aid']
        elements = self.record['atoms']['element']
        if not len(aids) == len(elements):
            raise ResponseParseError('Error parsing atom elements')
        for aid, element in zip(aids, elements):
            self._atoms[aid] = Atom(aid=aid, number=element)
        # Add coordinates
        if 'coords' in self.record:
            coord_ids = self.record['coords'][0]['aid']
            xs = self.record['coords'][0]['conformers'][0]['x']
            ys = self.record['coords'][0]['conformers'][0]['y']
            zs = self.record['coords'][0]['conformers'][0].get('z', [])
            if not len(coord_ids) == len(xs) == len(ys) == len(self._atoms) or (zs and not len(zs) == len(coord_ids)):
                raise ResponseParseError('Error parsing atom coordinates')
            for aid, x, y, z in zip_longest(coord_ids, xs, ys, zs):
                self._atoms[aid].set_coordinates(x, y, z)
        # Add charges
        if 'charge' in self.record['atoms']:
            for charge in self.record['atoms']['charge']:
                self._atoms[charge['aid']].charge = charge['value']

    def _setup_bonds(self):
        """Derive Bond objects from the record."""
        self._bonds = {}
        if 'bonds' not in self.record:
            return
        # Create bonds
        aid1s = self.record['bonds']['aid1']
        aid2s = self.record['bonds']['aid2']
        orders = self.record['bonds']['order']
        if not len(aid1s) == len(aid2s) == len(orders):
            raise ResponseParseError('Error parsing bonds')
        for aid1, aid2, order in zip(aid1s, aid2s, orders):
            self._bonds[frozenset((aid1, aid2))] = Bond(aid1=aid1, aid2=aid2, order=order)
        # Add styles
        if 'coords' in self.record and 'style' in self.record['coords'][0]['conformers'][0]:
            aid1s = self.record['coords'][0]['conformers'][0]['style']['aid1']
            aid2s = self.record['coords'][0]['conformers'][0]['style']['aid2']
            styles = self.record['coords'][0]['conformers'][0]['style']['annotation']
            for aid1, aid2, style in zip(aid1s, aid2s, styles):
                self._bonds[frozenset((aid1, aid2))].style = style

    @classmethod
    def from_cid(cls, cid, **kwargs):
        """Retrieve the Compound record for the specified CID.

        Usage::

            c = Compound.from_cid(6819)

        :param int cid: The PubChem Compound Identifier (CID).
        """
        record = json.loads(request(cid, **kwargs).read().decode())['PC_Compounds'][0]
        return cls(record)

    def __repr__(self):
        return f'Compound({self.cid if self.cid else ""})'

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.record == other.record

    def to_dict(self, properties=None):
        """Return a dictionary containing Compound data. Optionally specify a list of the desired properties.

        synonyms, aids and sids are not included unless explicitly specified using the properties parameter. This is
        because they each require an extra request.

        ``canonical_smiles`` and ``isomeric_smiles`` are not included by default, as they are deprecated and have
        been replaced by ``connectivity_smiles`` and ``smiles`` respectively.
        """
        if not properties:
            skip = {'aids', 'sids', 'synonyms', 'canonical_smiles', 'isomeric_smiles'}
            properties = [p for p in dir(Compound) if isinstance(getattr(Compound, p), property) and p not in skip]
        return {p: [i.to_dict() for i in getattr(self, p)] if p in {'atoms', 'bonds'} else getattr(self, p) for p in properties}

    def to_series(self, properties=None):
        """Return a pandas :class:`~pandas.Series` containing Compound data. Optionally specify a list of the desired
        properties.

        synonyms, aids and sids are not included unless explicitly specified using the properties parameter. This is
        because they each require an extra request.
        """
        import pandas as pd
        return pd.Series(self.to_dict(properties))

    @property
    def cid(self):
        """The PubChem Compound Identifier (CID).

        .. note::

            When searching using a SMILES or InChI query that is not present in the PubChem Compound database, an
            automatically generated record may be returned that contains properties that have been calculated on the
            fly. These records will not have a CID property.
        """
        if 'id' in self.record and 'id' in self.record['id'] and 'cid' in self.record['id']['id']:
            return self.record['id']['id']['cid']

    @property
    def elements(self):
        """List of element symbols for atoms in this Compound."""
        return [a.element for a in self.atoms]

    @property
    def atoms(self):
        """List of :class:`Atoms <pubchempy.Atom>` in this Compound."""
        return sorted(self._atoms.values(), key=lambda x: x.aid)

    @property
    def bonds(self):
        """List of :class:`Bonds <pubchempy.Bond>` between :class:`Atoms <pubchempy.Atom>` in this Compound."""
        return sorted(self._bonds.values(), key=lambda x: (x.aid1, x.aid2))

    @memoized_property
    def synonyms(self):
        """A ranked list of all the names associated with this Compound.

        Requires an extra request. Result is cached.
        """
        if self.cid:
            results = get_json(self.cid, operation='synonyms')
            return results['InformationList']['Information'][0]['Synonym'] if results else []

    @memoized_property
    def sids(self):
        """Requires an extra request. Result is cached."""
        if self.cid:
            results = get_json(self.cid, operation='sids')
            return results['InformationList']['Information'][0]['SID'] if results else []

    @memoized_property
    def aids(self):
        """Requires an extra request. Result is cached."""
        if self.cid:
            results = get_json(self.cid, operation='aids')
            return results['InformationList']['Information'][0]['AID'] if results else []

    @property
    def coordinate_type(self):
        if CoordinateType.TWO_D in self.record['coords'][0]['type']:
            return '2d'
        elif CoordinateType.THREE_D in self.record['coords'][0]['type']:
            return '3d'

    @property
    def charge(self):
        """Formal charge on this Compound."""
        return self.record['charge'] if 'charge' in self.record else 0

    @property
    def molecular_formula(self):
        """Molecular formula."""
        return _parse_prop({'label': 'Molecular Formula'}, self.record['props'])

    @property
    def molecular_weight(self):
        """Molecular Weight."""
        sval = _parse_prop({'label': 'Molecular Weight'}, self.record['props'])
        return float(sval) if sval else None

    @property
    @deprecated('Use connectivity_smiles instead')
    def canonical_smiles(self):
        """Canonical SMILES, with no stereochemistry information (deprecated).

        .. deprecated:: 1.0.5
           :attr:`canonical_smiles` is deprecated, use :attr:`connectivity_smiles`
           instead.
        """
        return self.connectivity_smiles

    @property
    @deprecated('Use smiles instead')
    def isomeric_smiles(self):
        """Isomeric SMILES.

        .. deprecated:: 1.0.5
           :attr:`isomeric_smiles` is deprecated, use :attr:`smiles` instead.
        """
        return self.smiles

    @property
    def connectivity_smiles(self):
        """Connectivity SMILES.

        A canonical SMILES string that excludes stereochemical and isotopic information.

        Replaces the the deprecated :attr:`canonical_smiles` property.
        """
        return _parse_prop({'label': 'SMILES', 'name': 'Connectivity'}, self.record['props'])

    @property
    def smiles(self):
        """Absolute SMILES (isomeric and canonical).

        A canonical SMILES string that includes stereochemical and isotopic information.

        Replaces the deprecated :attr:`isomeric_smiles` property.
        """
        return _parse_prop({'label': 'SMILES', 'name': 'Absolute'}, self.record['props'])

    @property
    def inchi(self):
        """InChI string."""
        return _parse_prop({'label': 'InChI', 'name': 'Standard'}, self.record['props'])

    @property
    def inchikey(self):
        """InChIKey."""
        return _parse_prop({'label': 'InChIKey', 'name': 'Standard'}, self.record['props'])

    @property
    def iupac_name(self):
        """Preferred IUPAC name."""
        # Note: Allowed, CAS-like Style, Preferred, Systematic, Traditional are available in full record
        return _parse_prop({'label': 'IUPAC Name', 'name': 'Preferred'}, self.record['props'])

    @property
    def xlogp(self):
        """XLogP."""
        return _parse_prop({'label': 'Log P'}, self.record['props'])

    @property
    def exact_mass(self):
        """Exact mass."""
        sval = _parse_prop({'label': 'Mass', 'name': 'Exact'}, self.record['props'])
        return float(sval) if sval else None

    @property
    def monoisotopic_mass(self):
        """Monoisotopic mass."""
        sval = _parse_prop({'label': 'Weight', 'name': 'MonoIsotopic'}, self.record['props'])
        return float(sval) if sval else None

    @property
    def tpsa(self):
        """Topological Polar Surface Area."""
        return _parse_prop({'implementation': 'E_TPSA'}, self.record['props'])

    @property
    def complexity(self):
        """Complexity."""
        return _parse_prop({'implementation': 'E_COMPLEXITY'}, self.record['props'])

    @property
    def h_bond_donor_count(self):
        """Hydrogen bond donor count."""
        return _parse_prop({'implementation': 'E_NHDONORS'}, self.record['props'])

    @property
    def h_bond_acceptor_count(self):
        """Hydrogen bond acceptor count."""
        return _parse_prop({'implementation': 'E_NHACCEPTORS'}, self.record['props'])

    @property
    def rotatable_bond_count(self):
        """Rotatable bond count."""
        return _parse_prop({'implementation': 'E_NROTBONDS'}, self.record['props'])

    @property
    def fingerprint(self):
        """Raw padded and hex-encoded fingerprint, as returned by the PUG REST API."""
        return _parse_prop({'implementation': 'E_SCREEN'}, self.record['props'])

    @property
    def cactvs_fingerprint(self):
        """PubChem CACTVS fingerprint.

        Each bit in the fingerprint represents the presence or absence of one of 881 chemical substructures.

        More information at ftp://ftp.ncbi.nlm.nih.gov/pubchem/specifications/pubchem_fingerprints.txt
        """
        # Skip first 4 bytes (contain length of fingerprint) and last 7 bits (padding) then re-pad to 881 bits
        return f'{int(self.fingerprint[8:], 16):020b}'[:-7].zfill(881)

    @property
    def heavy_atom_count(self):
        """Heavy atom count."""
        if 'count' in self.record and 'heavy_atom' in self.record['count']:
            return self.record['count']['heavy_atom']

    @property
    def isotope_atom_count(self):
        """Isotope atom count."""
        if 'count' in self.record and 'isotope_atom' in self.record['count']:
            return self.record['count']['isotope_atom']

    @property
    def atom_stereo_count(self):
        """Atom stereocenter count."""
        if 'count' in self.record and 'atom_chiral' in self.record['count']:
            return self.record['count']['atom_chiral']

    @property
    def defined_atom_stereo_count(self):
        """Defined atom stereocenter count."""
        if 'count' in self.record and 'atom_chiral_def' in self.record['count']:
            return self.record['count']['atom_chiral_def']

    @property
    def undefined_atom_stereo_count(self):
        """Undefined atom stereocenter count."""
        if 'count' in self.record and 'atom_chiral_undef' in self.record['count']:
            return self.record['count']['atom_chiral_undef']

    @property
    def bond_stereo_count(self):
        """Bond stereocenter count."""
        if 'count' in self.record and 'bond_chiral' in self.record['count']:
            return self.record['count']['bond_chiral']

    @property
    def defined_bond_stereo_count(self):
        """Defined bond stereocenter count."""
        if 'count' in self.record and 'bond_chiral_def' in self.record['count']:
            return self.record['count']['bond_chiral_def']

    @property
    def undefined_bond_stereo_count(self):
        """Undefined bond stereocenter count."""
        if 'count' in self.record and 'bond_chiral_undef' in self.record['count']:
            return self.record['count']['bond_chiral_undef']

    @property
    def covalent_unit_count(self):
        """Covalently-bonded unit count."""
        if 'count' in self.record and 'covalent_unit' in self.record['count']:
            return self.record['count']['covalent_unit']

    @property
    def volume_3d(self):
        conf = self.record['coords'][0]['conformers'][0]
        if 'data' in conf:
            return _parse_prop({'label': 'Shape', 'name': 'Volume'}, conf['data'])

    @property
    def multipoles_3d(self):
        conf = self.record['coords'][0]['conformers'][0]
        if 'data' in conf:
            return _parse_prop({'label': 'Shape', 'name': 'Multipoles'}, conf['data'])

    @property
    def conformer_rmsd_3d(self):
        coords = self.record['coords'][0]
        if 'data' in coords:
            return _parse_prop({'label': 'Conformer', 'name': 'RMSD'}, coords['data'])

    @property
    def effective_rotor_count_3d(self):
        return _parse_prop({'label': 'Count', 'name': 'Effective Rotor'}, self.record['props'])

    @property
    def pharmacophore_features_3d(self):
        return _parse_prop({'label': 'Features', 'name': 'Pharmacophore'}, self.record['props'])

    @property
    def mmff94_partial_charges_3d(self):
        return _parse_prop({'label': 'Charge', 'name': 'MMFF94 Partial'}, self.record['props'])

    @property
    def mmff94_energy_3d(self):
        conf = self.record['coords'][0]['conformers'][0]
        if 'data' in conf:
            return _parse_prop({'label': 'Energy', 'name': 'MMFF94 NoEstat'}, conf['data'])

    @property
    def conformer_id_3d(self):
        conf = self.record['coords'][0]['conformers'][0]
        if 'data' in conf:
            return _parse_prop({'label': 'Conformer', 'name': 'ID'}, conf['data'])

    @property
    def shape_selfoverlap_3d(self):
        conf = self.record['coords'][0]['conformers'][0]
        if 'data' in conf:
            return _parse_prop({'label': 'Shape', 'name': 'Self Overlap'}, conf['data'])

    @property
    def feature_selfoverlap_3d(self):
        conf = self.record['coords'][0]['conformers'][0]
        if 'data' in conf:
            return _parse_prop({'label': 'Feature', 'name': 'Self Overlap'}, conf['data'])

    @property
    def shape_fingerprint_3d(self):
        conf = self.record['coords'][0]['conformers'][0]
        if 'data' in conf:
            return _parse_prop({'label': 'Fingerprint', 'name': 'Shape'}, conf['data'])


def _parse_prop(search, proplist):
    """Extract property value from record using the given urn search filter."""
    props = [i for i in proplist if all(item in i['urn'].items() for item in search.items())]
    if len(props) > 0:
        return props[0]['value'][list(props[0]['value'].keys())[0]]


class Substance:
    """Corresponds to a single record from the PubChem Substance database.

    The PubChem Substance database contains all chemical records deposited in PubChem in their most raw form, before
    any significant processing is applied. As a result, it contains duplicates, mixtures, and some records that don't
    make chemical sense. This means that Substance records contain fewer calculated properties, however they do have
    additional information about the original source that deposited the record.

    The PubChem Compound database is constructed from the Substance database using a standardization and deduplication
    process. Hence each Compound may be derived from a number of different Substances.
    """

    @classmethod
    def from_sid(cls, sid):
        """Retrieve the Substance record for the specified SID.

        :param int sid: The PubChem Substance Identifier (SID).
        """
        record = json.loads(request(sid, 'sid', 'substance').read().decode())['PC_Substances'][0]
        return cls(record)

    def __init__(self, record):
        self.record = record
        """A dictionary containing the full Substance record that all other properties are obtained from."""

    def __repr__(self):
        return f'Substance({self.sid if self.sid else ""})'

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.record == other.record

    def to_dict(self, properties=None):
        """Return a dictionary containing Substance data.

        If the properties parameter is not specified, everything except cids and aids is included. This is because the
        aids and cids properties each require an extra request to retrieve.

        :param properties: (optional) A list of the desired properties.
        """
        if not properties:
            skip = {'deposited_compound', 'standardized_compound', 'cids', 'aids'}
            properties = [p for p in dir(Substance) if isinstance(getattr(Substance, p), property) and p not in skip]
        return {p: getattr(self, p) for p in properties}

    def to_series(self, properties=None):
        """Return a pandas :class:`~pandas.Series` containing Substance data.

        If the properties parameter is not specified, everything except cids and aids is included. This is because the
        aids and cids properties each require an extra request to retrieve.

        :param properties: (optional) A list of the desired properties.
        """
        import pandas as pd
        return pd.Series(self.to_dict(properties))

    @property
    def sid(self):
        """The PubChem Substance Idenfitier (SID)."""
        return self.record['sid']['id']

    @property
    def synonyms(self):
        """A ranked list of all the names associated with this Substance."""
        if 'synonyms' in self.record:
            return self.record['synonyms']

    @property
    def source_name(self):
        """The name of the PubChem depositor that was the source of this Substance."""
        return self.record['source']['db']['name']

    @property
    def source_id(self):
        """Unique ID for this Substance within those from the same PubChem depositor source."""
        return self.record['source']['db']['source_id']['str']

    @property
    def standardized_cid(self):
        """The CID of the Compound that was produced when this Substance was standardized.

        May not exist if this Substance was not standardizable.
        """
        for c in self.record.get('compound', []):
            if c['id']['type'] == CompoundIdType.STANDARDIZED:
                return c['id']['id']['cid']

    @memoized_property
    def standardized_compound(self):
        """Return the :class:`~pubchempy.Compound` that was produced when this Substance was standardized.

        Requires an extra request. Result is cached.
        """
        cid = self.standardized_cid
        if cid:
            return Compound.from_cid(cid)

    @property
    def deposited_compound(self):
        """Return a :class:`~pubchempy.Compound` produced from the unstandardized Substance record as deposited.

        The resulting :class:`~pubchempy.Compound` will not have a ``cid`` and will be missing most properties.
        """
        for c in self.record.get('compound', []):
            if c['id']['type'] == CompoundIdType.DEPOSITED:
                return Compound(c)

    @memoized_property
    def cids(self):
        """A list of all CIDs for Compounds that were produced when this Substance was standardized.

        Requires an extra request. Result is cached."""
        results = get_json(self.sid, 'sid', 'substance', 'cids')
        return results['InformationList']['Information'][0]['CID'] if results else []

    @memoized_property
    def aids(self):
        """A list of all AIDs for Assays associated with this Substance.

        Requires an extra request. Result is cached."""
        results = get_json(self.sid, 'sid', 'substance', 'aids')
        return results['InformationList']['Information'][0]['AID'] if results else []


class Assay:

    @classmethod
    def from_aid(cls, aid):
        """Retrieve the Assay record for the specified AID.

        :param int aid: The PubChem Assay Identifier (AID).
        """
        record = json.loads(request(aid, 'aid', 'assay', 'description').read().decode())['PC_AssayContainer'][0]
        return cls(record)

    def __init__(self, record):
        self.record = record
        """A dictionary containing the full Assay record that all other properties are obtained from."""

    def __repr__(self):
        return f'Assay({self.aid if self.aid else ""})'

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.record == other.record

    def to_dict(self, properties=None):
        """Return a dictionary containing Assay data.

        If the properties parameter is not specified, everything is included.

        :param properties: (optional) A list of the desired properties.
        """
        if not properties:
            properties = [p for p in dir(Assay) if isinstance(getattr(Assay, p), property)]
        return {p: getattr(self, p) for p in properties}

    @property
    def aid(self):
        """The PubChem Substance Idenfitier (SID)."""
        return self.record['assay']['descr']['aid']['id']

    @property
    def name(self):
        """The short assay name, used for display purposes."""
        return self.record['assay']['descr']['name']

    @property
    def description(self):
        """Description."""
        return self.record['assay']['descr']['description']

    @property
    def project_category(self):
        """A category to distinguish projects funded through MLSCN, MLPCN or from literature.

        Possible values include mlscn, mlpcn, mlscn-ap, mlpcn-ap, literature-extracted, literature-author,
        literature-publisher, rnaigi.
        """
        if 'project_category' in self.record['assay']['descr']:
            return ProjectCategory(self.record['assay']['descr']['project_category'])

    @property
    def comments(self):
        """Comments and additional information."""
        return [comment for comment in self.record['assay']['descr']['comment'] if comment]

    @property
    def results(self):
        """A list of dictionaries containing details of the results from this Assay."""
        return self.record['assay']['descr']['results']

    @property
    def target(self):
        """A list of dictionaries containing details of the Assay targets."""
        if 'target' in self.record['assay']['descr']:
            return self.record['assay']['descr']['target']

    @property
    def revision(self):
        """Revision identifier for textual description."""
        return self.record['assay']['descr']['revision']

    @property
    def aid_version(self):
        """Incremented when the original depositor updates the record."""
        return self.record['assay']['descr']['aid']['version']


def compounds_to_frame(compounds, properties=None):
    """Construct a pandas :class:`~pandas.DataFrame` from a list of :class:`~pubchempy.Compound` objects.

    Optionally specify a list of the desired :class:`~pubchempy.Compound` properties.
    """
    import pandas as pd
    if isinstance(compounds, Compound):
        compounds = [compounds]
    properties = set(properties) | {'cid'} if properties else None
    return pd.DataFrame.from_records([c.to_dict(properties) for c in compounds], index='cid')


def substances_to_frame(substances, properties=None):
    """Construct a pandas :class:`~pandas.DataFrame` from a list of :class:`~pubchempy.Substance` objects.

    Optionally specify a list of the desired :class:`~pubchempy.Substance` properties.
    """
    import pandas as pd
    if isinstance(substances, Substance):
        substances = [substances]
    properties = set(properties) | {'sid'} if properties else None
    return pd.DataFrame.from_records([s.to_dict(properties) for s in substances], index='sid')


# def add_columns_to_frame(dataframe, id_col, id_namespace, add_cols):
#     """"""
#     # Existing dataframe with some identifier column
#     # But consider what to do if the identifier column is an index?
#     # What about having the Compound/Substance object as a column?


class PubChemPyDeprecationWarning(Warning):
    """Warning category for deprecated features."""
    pass


class PubChemPyError(Exception):
    """Base class for all PubChemPy exceptions."""
    pass


class ResponseParseError(PubChemPyError):
    """PubChem response is uninterpretable."""
    pass

class PubChemHTTPError(PubChemPyError):
    """Generic error class to handle HTTP error codes."""
    def __init__(self, code: int, msg: str, details: list[str]) -> None:
        super().__init__(msg)
        self.code = code
        self.msg = msg
        self.details = details

    def __str__(self) -> str:
        output = f'PubChem HTTP Error {self.code} {self.msg}'
        if self.details:
            details = ', '.join(self.details)
            output = f'{output} ({details})'
        return output

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.code!r}, {self.msg!r}, {self.details!r})'


def create_http_error(e: HTTPError) -> PubChemHTTPError:
    """Create appropriate PubChem HTTP error subclass based on status code."""
    code = e.code
    msg = e.msg
    details = []
    try:
        fault = json.loads(e.read().decode())['Fault']
        msg = fault.get('Code', msg)
        if 'Message' in fault:
            msg = f'{msg}: {fault["Message"]}'
        details = fault.get('Details', [])
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
    """400: Request is improperly formed (syntax error in the URL, POST body, etc.)."""


class NotFoundError(PubChemHTTPError):
    """404: The input record was not found (e.g. invalid CID)."""


class MethodNotAllowedError(PubChemHTTPError):
    """405: Request not allowed (such as invalid MIME type in the HTTP Accept header)."""

class ServerError(PubChemHTTPError):
    """500: Some problem on the server side (such as a database server down, etc.)."""


class UnimplementedError(PubChemHTTPError):
    """501: The requested operation has not (yet) been implemented by the server."""


class ServerBusyError(PubChemHTTPError):
    """503: Too many requests or server is busy, retry later."""


class TimeoutError(PubChemHTTPError):
    """504: The request timed out, from server overload or too broad a request.

    See :ref:`Avoiding TimeoutError <avoiding_timeouterror>` for more information.
    """


if __name__ == '__main__':
    print(__version__)
