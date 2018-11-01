# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "pfeffernusse"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["connexion"]

setup(
    name=NAME,
    version=VERSION,
    description="Pfeffernusse",
    author_email="jlaura@usgs.gov",
    url="",
    keywords=["OpenAPI", "Pfeffernusse"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['openapi/openapi.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['pfeffernusse=pfeffernusse.__main__:main']},
    long_description="""\
    A SpiceAPI for extracting NAIF Spice Data
    """
)

