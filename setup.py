#!/usr/bin/env python

from setuptools import setup, find_packages
setup ( \
    name = 'python-ovrsdk',
    version = '0.3.2.1',
    description = 'Python wrapper for Oculus VR SDK.',
    long_description = open('README.rst', 'r').read(),
    author = 'Rye Terrell',
    author_email = 'wwwtyro@gmail.com',
    url = 'https://github.com/wwwtyro/python-ovrsdk',
    packages = ['ovrsdk', 'ovrsdk.windows'],
    package_data = {'': ['libovr.dll']}
)