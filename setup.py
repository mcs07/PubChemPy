#!/usr/bin/env python

import os
from distutils.core import setup

import pubchempy


if os.path.exists('README.txt'):
    long_description = open('README.txt').read()
else:
    long_description = open('README.md').read()

setup(
    name='PubChemPy',
    version=pubchempy.__version__,
    author=pubchempy.__author__,
    author_email=pubchempy.__email__,
    license=pubchempy.__license__,
    url='https://github.com/mcs07/PubChemPy',
    py_modules=['pubchempy'],
    description='A simple Python wrapper around the PubChem PUG REST API.',
    long_description=long_description,
    keywords='pubchem python rest api pug',
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
        'Programming Language :: Python :: 2.7',
    ],
)
