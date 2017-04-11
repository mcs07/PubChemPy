#!/usr/bin/env python

import os
from setuptools import setup


if os.path.exists('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = '''PubChemPy is a wrapper around the PubChem PUG REST API that provides a way to interact
with PubChem in Python. It allows chemical searches (including by name, substructure and similarity), chemical
standardization, conversion between chemical file formats, depiction and retrieval of chemical properties.
'''

setup(
    name='PubChemPy',
    version='1.0.4',
    author='Matt Swain',
    author_email='m.swain@me.com',
    license='MIT',
    url='https://github.com/mcs07/PubChemPy',
    py_modules=['pubchempy'],
    description='A simple Python wrapper around the PubChem PUG REST API.',
    long_description=long_description,
    keywords='pubchem python rest api chemistry cheminformatics',
    extras_require={'pandas': ['pandas']},
    test_suite='pubchempy_test',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Database :: Front-Ends',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
