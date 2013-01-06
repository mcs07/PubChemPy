# -*- coding: utf-8 -*-
"""
PubChemPy

Python interface for the PubChem PUG REST service.
https://github.com/mcs07/PubChemPy
"""

import json
import os
import time
import urllib
import urllib2



API_BASE = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'


def request(identifier, namespace='cid', domain='compound', operation=None, output='JSON', searchtype=None, **kwargs):
    """
    Construct API request from parameters and return the response.

    Full specification at http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html
    """

    # If identifier is a list, join with commas into string
    if isinstance(identifier, int):
        identifier = str(identifier)
    if not isinstance(identifier, basestring):
        identifier = ','.join(str(x) for x in identifier)

    # Filter None values from kwargs
    kwargs = dict((k,v) for k,v in kwargs.iteritems() if v is not None)

    # Build API URL
    urlid, postdata = None, None
    if namespace in ['listkey', 'formula'] or (searchtype and namespace == 'cid') or domain == 'sources':
        urlid = urllib2.quote(identifier.replace('/','.'))
    else:
        postdata = '%s=%s' % (namespace, urllib2.quote(identifier.replace('/','.')))
    comps = filter(None, [API_BASE, domain, searchtype, namespace, urlid, operation, output])
    apiurl = '/'.join(comps)
    if kwargs:
        apiurl+= '?%s' % urllib.urlencode(kwargs)

    # Make request
    try:
        print apiurl
        response = urllib2.urlopen(apiurl, postdata).read()
        return response
    except urllib2.HTTPError as e:
        raise PubChemHTTPError(e)


def get(identifier, namespace='cid', domain='compound', operation=None, output='JSON', searchtype=None, **kwargs):
    """ Request wrapper that automatically handles async requests. """
    if searchtype or namespace in ['formula']:
        response = request(identifier, namespace, domain, None, 'JSON', searchtype, **kwargs)
        status = json.loads(response)
        if 'Waiting' in status and 'ListKey' in status['Waiting']:
            identifier = status['Waiting']['ListKey']
            namespace = 'listkey'
            while 'Waiting' in status and 'ListKey' in status['Waiting']:
                time.sleep(2)
                response = request(identifier, namespace, domain, operation, 'JSON', **kwargs)
                status = json.loads(response)
            if not output == 'JSON':
                response = request(identifier, namespace, domain, operation, output, searchtype, **kwargs)
    else:
        response = request(identifier, namespace, domain, operation, output, searchtype, **kwargs)
    return response





def get_compounds(identifier, namespace='cid', searchtype=None, **kwargs):
    """ Retrieve the specified compound records from PubChem. """
    results = json.loads(get(identifier, namespace, searchtype=searchtype, **kwargs))
    compounds = [Compound(r) for r in results['PC_Compounds']]
    return compounds

def get_substances(identifier, namespace='sid', **kwargs):
    """ Retrieve the specified substance records from PubChem. """
    results = json.loads(get(identifier, namespace, 'substance', **kwargs))
    substances = [Substance(r) for r in results['PC_Substances']]
    return substances

def get_assays(identifier, namespace='aid', sids=None, **kwargs):
    """ Retrieve the specified assay records from PubChem. """
    results = json.loads(get(identifier, namespace, 'assay', sids, **kwargs))
    assays = [Assay(r) for r in results['PC_AssayContainer']]
    return assays

def get_properties(properties, identifier, namespace='cid', domain='compound', searchtype=None, **kwargs):
    if not isinstance(properties, basestring):
        properties = ','.join(properties)
    properties = 'property/%s' % properties
    results = json.loads(get(identifier, namespace, domain, properties, searchtype=searchtype, **kwargs))
    results = results['PropertyTable']['Properties']
    return results

def get_synonyms(identifier, namespace='cid', domain='compound', searchtype=None, **kwargs):
    results = json.loads(get(identifier, namespace, domain, 'synonyms', searchtype=searchtype, **kwargs))
    synonyms = results['InformationList']['Information']
    return synonyms

def get_cids(identifier, namespace='name', domain='compound', searchtype=None, **kwargs):
    results = json.loads(get(identifier, namespace, domain, 'cids', searchtype=searchtype, **kwargs))
    if 'IdentifierList' in results:
        results = results['IdentifierList']['CID']
    elif 'InformationList' in results:
        results = results['InformationList']['Information']
    return results

def get_sids(identifier, namespace='cid', domain='compound', searchtype=None, **kwargs):
    results = json.loads(get(identifier, namespace, domain, 'sids', searchtype=searchtype, **kwargs))
    print results
    if 'IdentifierList' in results:
        results = results['IdentifierList']['SID']
    elif 'InformationList' in results:
        results = results['InformationList']['Information']
    return results

def get_aids(identifier, namespace='cid', domain='compound', searchtype=None, **kwargs):
    results = json.loads(get(identifier, namespace, domain, 'aids', searchtype=searchtype, **kwargs))
    if 'IdentifierList' in results:
        results = results['IdentifierList']['AID']
    elif 'InformationList' in results:
        results = results['InformationList']['Information']
    return results

# TODO: Assay Description, Summary, Dose-reponse
# TODO: Classification, Dates, XRefs operations

def get_all_sources(domain='substance'):
    """ Return a list of all current depositors of substances or assays. """
    results = json.loads(get(domain, None, 'sources'))
    sources = results['InformationList']['SourceName']
    return sources

def download(format, path, identifier, namespace='cid', domain='compound', operation=None, searchtype=None, overwrite=False, **kwargs):
    """ Format can be  XML, ASNT/B, JSON, SDF, CSV, PNG, TXT.  """
    response = get(identifier, namespace, domain, operation, format, searchtype, **kwargs)
    if not overwrite and os.path.isfile(path):
        raise IOError("%s already exists. Use 'overwrite=True' to overwrite it." % filename)
    with open(path, 'w') as file:
        file.write(response)

class Compound(object):
    def __init__(self, record):
        self.record = record

    @classmethod
    def from_cid(cls, cid):
        record = json.loads(request(cid))['PC_Compounds'][0]
        return cls(record)

    @property
    def cid(self):
        # Note: smiles or inchi inputs can return compounds without a cid
        if 'id' in self.record and 'id' in self.record['id'] and 'cid' in self.record['id']['id']:
            return self.record['id']['id']['cid']
        else:
            return None

    def __repr__(self):
        return 'Compound(%s)' % self.cid if self.cid else 'Compound()'


    # TODO: Parse record to extract cid, properties
    # property methods for different operations - record, properties, synonyms, sids, aids, assaysummary, classification
    # Parse properties from record where possible
    # Extra request for other properties + synonyms etc.
    # Many methods have options too - e.g. cids, aids, sids
    # method to print/save a certain format to file

class Substance(object):
    def __init__(self, record):
        self.record = record

    @classmethod
    def from_sid(cls, sid):
        record = json.loads(request(sid, 'sid', 'substance'))['PC_Substances'][0]
        return cls(record)

    @property
    def sid(self):
        return self.record['id']['id']['sid']

class Assay(object):
    def __init__(self, record):
        self.record = record

    @classmethod
    def from_aid(cls, aid):
        record = json.loads(request(aid, 'aid', 'assay'))['PC_AssayContainer'][0]
        return cls(record)

    @property
    def aid(self):
        return self.record['id']['id']['aid']


class PubChemHTTPError(Exception):
    """ Generic error class to handle all HTTP error codes """
    def __init__(self, e):
        self.code = e.code
        self.msg = e.reason
        try:
            self.msg += ': %s' % json.load(e)['Fault']['Details'][0]
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
    """ Request is improperly formed (syntax error in the URL, POST body, etc.) """
    def __init__(self, msg='Request is improperly formed'):
        self.msg = msg

class NotFoundError(PubChemHTTPError):
    """ The input record was not found (e.g. invalid CID) """
    def __init__(self, msg='The input record was not found'):
        self.msg = msg

class MethodNotAllowedError(PubChemHTTPError):
    """ Request not allowed (such as invalid MIME type in the HTTP Accept header) """
    def __init__(self, msg='Request not allowed'):
        self.msg = msg

class TimeoutError(PubChemHTTPError):
    """ The request timed out, from server overload or too broad a request """
    def __init__(self, msg='The request timed out'):
        self.msg = msg

class UnimplementedError(PubChemHTTPError):
    """ The requested operation has not (yet) been implemented by the server """
    def __init__(self, msg='The requested operation has not been implemented'):
        self.msg = msg

class ServerError(PubChemHTTPError):
    """ Some problem on the server side (such as a database server down, etc.) """
    def __init__(self, msg='Some problem on the server side'):
        self.msg = msg

if __name__ == '__main__':
    #r = request('coumarin', 'name', record_type='3d')
    #r = request('coumarin', 'name', output='PNG', image_size='50x50')
    #r = request('coumarin', 'name')

    #r = get('C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1', 'smiles', operation='cids', searchtype='substructure')
    #r = request('C10H21N', 'formula')

    #r = request('1', 'cid', searchtype='substructure')
    #r = request('1554905728985065490', 'listkey', operation='cids')



    #r = get('C10H21N', 'formula', operation='property/MolecularFormula', output='CSV')
    #r = get('1', 'cid', searchtype='substructure', operation='cids')

    #r = request('C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1', 'smiles', operation='cids')
    #r = request('tris-(1,10-phenanthroline)ruthenium', 'name', operation='synonyms', output='JSON')
    #r = request('Aspirin', 'name', operation='assaysummary', output='CSV')
    #r = request('Aspirin', 'name', output='JSON')
    #r = request('C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1', 'smiles', operation='property/MolecularFormula')

    #r = get_substances('Aspirin', 'name')
    #r = get_compounds(9548754, searchtype='superstructure')

    #r = get('2223', 'sid', domain='substance', operation='synonyms', searchtype="superstructure")

    #r = get_all_sources('assay')

    #r = get_compounds('C1=CC2=C(C3=C(C=CC=N3)C=C2)N=C1', 'smiles', searchtype='substructure', listkey_count=3)

    #r = get_synonyms(1)

    #r = get_assays(1000)
    #r = get_assays(1, sid='67107,67121,67122')


    #r = get_substances('Coumarin', 'name', listkey_count=3)

    #r = get_compounds('CC', 'smiles', searchtype='superstructure', listkey_count=5)
    #r = get('C10H21N', 'formula', listkey_count=3, listkey_start=6)

    #r = get_cids('Aspirin', 'name', 'substance')
    #r = get_cids('Aspirin', 'name', 'compound')
    #r = get_sids('Aspirin', 'name', 'substance')
    #r = get_aids('Aspirin', 'name', 'substance')
    #r = get_aids('Aspirin', 'name', 'compound')

    r = get_properties('IsomericSMILES', 'tris-(1,10-phenanthroline)ruthenium', 'name')

    print r

    #c = Compound.from_cid(9548754)
    #print c



    # TODO: Some namespaces (e.g. sourceid/<source name>) require '/' replaced with with '.' - leave to user?
