# -*- coding: utf-8 -*-
"""
test_requests
~~~~~~~~~~~~~

Test basic requests.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from pubchempy import *


def test_requests():
    """Test a variety of basic raw requests and ensure they don't return an error code."""
    assert request('c1ccccc1', 'smiles').getcode() == 200
    assert request('DTP/NCI', 'sourceid', 'substance', '747285', 'SDF').getcode() == 200
    assert request('coumarin', 'name', output='PNG', image_size='50x50').getcode() == 200


def test_content_type():
    """Test content type header matches desired output format."""
    assert request(241, output='JSON').headers['Content-Type'] == 'application/json'
    assert request(241, output='XML').headers['Content-Type'] == 'application/xml'
    assert request(241, output='SDF').headers['Content-Type'] == 'chemical/x-mdl-sdfile'
    assert request(241, output='ASNT').headers['Content-Type'] == 'text/plain'
    assert request(241, output='PNG').headers['Content-Type'] == 'image/png'


def test_listkey_requests():
    """Test asynchronous listkey requests."""
    r1 = get_json('CC', 'smiles', operation='cids', searchtype='superstructure')
    assert 'IdentifierList' in r1 and 'CID' in r1['IdentifierList']
    r2 = get_json('C10H21N', 'formula', listkey_count=3)
    assert 'PC_Compounds' in r2 and len(r2['PC_Compounds']) == 3


def test_xref_request():
    """Test requests with xref inputs."""
    response = request('US6187568B1', 'PatentID', 'substance',  operation='sids', searchtype='xref')
    assert response.code == 200
    response2 = get_json('US6187568B1', 'PatentID', 'substance', operation='sids', searchtype='xref')
    assert 'IdentifierList' in response2
    assert 'SID' in response2['IdentifierList']
    sids = get_sids('US6187568B1', 'PatentID', 'substance', searchtype='xref')
    assert all(isinstance(sid, int) for sid in sids)
