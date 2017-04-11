# -*- coding: utf-8 -*-
"""
PubChemPy

Python interface for the PubChem PUG REST service.
https://github.com/mcs07/PubChemPy
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

import functools
import json
import logging
import os
import sys
import time
import warnings
import binascii

try:
    from urllib.error import HTTPError
    from urllib.parse import quote, urlencode
    from urllib.request import urlopen
except ImportError:
    from urllib import urlencode
    from urllib2 import quote, urlopen, HTTPError

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


__author__ = 'Matt Swain'
__email__ = 'm.swain@me.com'
__version__ = '1.0.4'
__license__ = 'MIT'

API_BASE = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'

log = logging.getLogger('pubchempy')
log.addHandler(logging.NullHandler())


if sys.version_info[0] == 3:
    text_types = str, bytes
else:
    text_types = basestring,


class CompoundIdType(object):
    """"""
    #: Original Deposited Compound
    DEPOSITED = 0
    #: Standardized Form of the Deposited Compound
    STANDARDIZED = 1
    #: Component of the Standardized Form
    COMPONENT = 2
    #: Neutralized Form of the Standardized Form
    NEUTRALIZED = 3
    #: Deposited Mixture Component
    MIXTURE = 4
    #: Alternate Tautomer Form of the Standardized Form
    TAUTOMER = 5
    #: Ionized pKa Form of the Standardized Form
    IONIZED = 6
    #: Unspecified or Unknown Compound Type
    UNKNOWN = 255


class BondType(object):
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3
    QUADRUPLE = 4
    DATIVE = 5
    COMPLEX = 6
    IONIC = 7
    UNKNOWN = 255


class CoordinateType(object):
    TWO_D = 1
    THREE_D = 2
    SUBMITTED = 3
    EXPERIMENTAL = 4
    COMPUTED = 5
    STANDARDIZED = 6
    AUGMENTED = 7
    ALIGNED = 8
    COMPACT = 9
    UNITS_ANGSTROMS = 10
    UNITS_NANOMETERS = 11
    UNITS_PIXEL = 12
    UNITS_POINTS = 13
    UNITS_STDBONDS = 14
    UNITS_UNKNOWN = 255


class ProjectCategory(object):
    MLSCN = 1
    MPLCN = 2
    MLSCN_AP = 3
    MPLCN_AP = 4
    JOURNAL_ARTICLE = 5
    ASSAY_VENDOR = 6
    LITERATURE_EXTRACTED = 7
    LITERATURE_AUTHOR = 8
    LITERATURE_PUBLISHER = 9
    RNAIGI = 10
    OTHER = 255


ELEMENTS = {
    1: 'H',
    2: 'He',
    3: 'Li',
    4: 'Be',
    5: 'B',
    6: 'C',
    7: 'N',
    8: 'O',
    9: 'F',
    10: 'Ne',
    11: 'Na',
    12: 'Mg',
    13: 'Al',
    14: 'Si',
    15: 'P',
    16: 'S',
    17: 'Cl',
    18: 'Ar',
    19: 'K',
    20: 'Ca',
    21: 'Sc',
    22: 'Ti',
    23: 'V',
    24: 'Cr',
    25: 'Mn',
    26: 'Fe',
    27: 'Co',
    28: 'Ni',
    29: 'Cu',
    30: 'Zn',
    31: 'Ga',
    32: 'Ge',
    33: 'As',
    34: 'Se',
    35: 'Br',
    36: 'Kr',
    37: 'Rb',
    38: 'Sr',
    39: 'Y',
    40: 'Zr',
    41: 'Nb',
    42: 'Mo',
    43: 'Tc',
    44: 'Ru',
    45: 'Rh',
    46: 'Pd',
    47: 'Ag',
    48: 'Cd',
    49: 'In',
    50: 'Sn',
    51: 'Sb',
    52: 'Te',
    53: 'I',
    54: 'Xe',
    55: 'Cs',
    56: 'Ba',
    57: 'La',
    58: 'Ce',
    59: 'Pr',
    60: 'Nd',
    61: 'Pm',
    62: 'Sm',
    63: 'Eu',
    64: 'Gd',
    65: 'Tb',
    66: 'Dy',
    67: 'Ho',
    68: 'Er',
    69: 'Tm',
    70: 'Yb',
    71: 'Lu',
    72: 'Hf',
    73: 'Ta',
    74: 'W',
    75: 'Re',
    76: 'Os',
    77: 'Ir',
    78: 'Pt',
    79: 'Au',
    80: 'Hg',
    81: 'Tl',
    82: 'Pb',
    83: 'Bi',
    84: 'Po',
    85: 'At',
    86: 'Rn',
    87: 'Fr',
    88: 'Ra',
    89: 'Ac',
    90: 'Th',
    91: 'Pa',
    92: 'U',
    93: 'Np',
    94: 'Pu',
    95: 'Am',
    96: 'Cm',
    97: 'Bk',
    98: 'Cf',
    99: 'Es',
    100: 'Fm',
    101: 'Md',
    102: 'No',
    103: 'Lr',
    104: 'Rf',
    105: 'Db',
    106: 'Sg',
    107: 'Bh',
    108: 'Hs',
    109: 'Mt',
    110: 'Ds',
    111: 'Rg',
    112: 'Cp',
    113: 'ut',
    114: 'uq',
    115: 'up',
    116: 'uh',
    117: 'us',
    118: 'uo',
}


def request(identifier, namespace='cid', domain='compound', operation=None, output='JSON', searchtype=None, **kwargs):
    """
    Construct API request from parameters and return the response.

    Full specification at http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html
    """
    if not identifier:
        raise ValueError('identifier/cid cannot be None')
    # If identifier is a list, join with commas into string
    if isinstance(identifier, int):
        identifier = str(identifier)
    if not isinstance(identifier, text_types):
        identifier = ','.join(str(x) for x in identifier)
    # Filter None values from kwargs
    kwargs = dict((k, v) for k, v in kwargs.items() if v is not None)
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
        apiurl += '?%s' % urlencode(kwargs)
    # Make request
    try:
        log.debug('Request URL: %s', apiurl)
        log.debug('Request data: %s', postdata)
        response = urlopen(apiurl, postdata)
        return response
    except HTTPError as e:
        raise PubChemHTTPError(e)


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


# Allows properties to optionally be specified as underscore_separated, consistent with Compound attributes
PROPERTY_MAP = {
    'molecular_formula': 'MolecularFormula',
    'molecular_weight': 'MolecularWeight',
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
    if isinstance(properties, text_types):
        properties = properties.split(',')
    properties = ','.join([PROPERTY_MAP.get(p, p) for p in properties])
    properties = 'property/%s' % properties
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
        raise IOError("%s already exists. Use 'overwrite=True' to overwrite it." % path)
    with open(path, 'wb') as f:
        f.write(response)


def memoized_property(fget):
    """Decorator to create memoized properties.

    Used to cache :class:`~pubchempy.Compound` and :class:`~pubchempy.Substance` properties that require an additional
    request.
    """
    attr_name = '_{0}'.format(fget.__name__)

    @functools.wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)
    return property(fget_memoized)


def deprecated(message=None):
    """Decorator to mark functions as deprecated. A warning will be emitted when the function is used."""
    def deco(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            warnings.warn(
                message or 'Call to deprecated function {}'.format(func.__name__),
                category=PubChemPyDeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapped
    return deco


class Atom(object):
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
        return 'Atom(%s, %s)' % (self.aid, self.element)

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
        return ELEMENTS.get(self.number, None)

    def to_dict(self):
        """Return a dictionary containing Atom data."""
        data = {'aid': self.aid, 'number': self.number, 'element': self.element}
        for coord in {'x', 'y', 'z'}:
            if getattr(self, coord) is not None:
                data[coord] = getattr(self, coord)
        if self.charge is not 0:
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


class Bond(object):
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
        return 'Bond(%s, %s, %s)' % (self.aid1, self.aid2, self.order)

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


class Compound(object):
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
        log.debug('Created %s' % self)
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
        return 'Compound(%s)' % self.cid if self.cid else 'Compound()'

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.record == other.record

    def to_dict(self, properties=None):
        """Return a dictionary containing Compound data. Optionally specify a list of the desired properties.

        synonyms, aids and sids are not included unless explicitly specified using the properties parameter. This is
        because they each require an extra request.
        """
        if not properties:
            skip = {'aids', 'sids', 'synonyms'}
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
        return _parse_prop({'label': 'Molecular Weight'}, self.record['props'])

    @property
    def canonical_smiles(self):
        """Canonical SMILES, with no stereochemistry information."""
        return _parse_prop({'label': 'SMILES', 'name': 'Canonical'}, self.record['props'])

    @property
    def isomeric_smiles(self):
        """Isomeric SMILES."""
        return _parse_prop({'label': 'SMILES', 'name': 'Isomeric'}, self.record['props'])

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
        return _parse_prop({'label': 'Mass', 'name': 'Exact'}, self.record['props'])

    @property
    def monoisotopic_mass(self):
        """Monoisotopic mass."""
        return _parse_prop({'label': 'Weight', 'name': 'MonoIsotopic'}, self.record['props'])

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
        return '{0:020b}'.format(int(self.fingerprint[8:], 16))[:-7].zfill(881)

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


class Substance(object):
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
        return 'Substance(%s)' % self.sid if self.sid else 'Substance()'

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
        for c in self.record['compound']:
            if c['id']['type'] == CompoundIdType.STANDARDIZED:
                return c['id']['id']['cid']

    @memoized_property
    def standardized_compound(self):
        """Return the :class:`~pubchempy.Compound` that was produced when this Substance was standardized.

        Requires an extra request. Result is cached.
        """
        for c in self.record['compound']:
            if c['id']['type'] == CompoundIdType.STANDARDIZED:
                return Compound.from_cid(c['id']['id']['cid'])

    @property
    def deposited_compound(self):
        """Return a :class:`~pubchempy.Compound` produced from the unstandardized Substance record as deposited.

        The resulting :class:`~pubchempy.Compound` will not have a ``cid`` and will be missing most properties.
        """
        for c in self.record['compound']:
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


class Assay(object):

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
        return 'Assay(%s)' % self.aid if self.aid else 'Assay()'

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
        """Description"""
        return self.record['assay']['descr']['description']

    @property
    def project_category(self):
        """A category to distinguish projects funded through MLSCN, MLPCN or from literature.

        Possible values include mlscn, mlpcn, mlscn-ap, mlpcn-ap, literature-extracted, literature-author,
        literature-publisher, rnaigi.
        """
        if 'project_category' in self.record['assay']['descr']:
            return self.record['assay']['descr']['project_category']

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
    properties = set(properties) | set(['cid']) if properties else None
    return pd.DataFrame.from_records([c.to_dict(properties) for c in compounds], index='cid')


def substances_to_frame(substances, properties=None):
    """Construct a pandas :class:`~pandas.DataFrame` from a list of :class:`~pubchempy.Substance` objects.

    Optionally specify a list of the desired :class:`~pubchempy.Substance` properties.
    """
    import pandas as pd
    if isinstance(substances, Substance):
        substances = [substances]
    properties = set(properties) | set(['sid']) if properties else None
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
    """Generic error class to handle all HTTP error codes."""
    def __init__(self, e):
        self.code = e.code
        self.msg = e.reason
        try:
            self.msg += ': %s' % json.loads(e.read().decode())['Fault']['Details'][0]
        except (ValueError, IndexError, KeyError):
            pass
        if self.code == 400:
            raise BadRequestError(self.msg)
        elif self.code == 404:
            raise NotFoundError(self.msg)
        elif self.code == 405:
            raise MethodNotAllowedError(self.msg)
        elif self.code == 504:
            raise TimeoutError(self.msg)
        elif self.code == 501:
            raise UnimplementedError(self.msg)
        elif self.code == 500:
            raise ServerError(self.msg)

    def __str__(self):
        return repr(self.msg)


class BadRequestError(PubChemHTTPError):
    """Request is improperly formed (syntax error in the URL, POST body, etc.)."""
    def __init__(self, msg='Request is improperly formed'):
        self.msg = msg


class NotFoundError(PubChemHTTPError):
    """The input record was not found (e.g. invalid CID)."""
    def __init__(self, msg='The input record was not found'):
        self.msg = msg


class MethodNotAllowedError(PubChemHTTPError):
    """Request not allowed (such as invalid MIME type in the HTTP Accept header)."""
    def __init__(self, msg='Request not allowed'):
        self.msg = msg


class TimeoutError(PubChemHTTPError):
    """The request timed out, from server overload or too broad a request.

    See :ref:`Avoiding TimeoutError <avoiding_timeouterror>` for more information.
    """
    def __init__(self, msg='The request timed out'):
        self.msg = msg


class UnimplementedError(PubChemHTTPError):
    """The requested operation has not (yet) been implemented by the server."""
    def __init__(self, msg='The requested operation has not been implemented'):
        self.msg = msg


class ServerError(PubChemHTTPError):
    """Some problem on the server side (such as a database server down, etc.)."""
    def __init__(self, msg='Some problem on the server side'):
        self.msg = msg


if __name__ == '__main__':
    print(__version__)
