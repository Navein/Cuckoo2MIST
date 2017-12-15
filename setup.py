#! /usr/bin/env python

from setuptools import setup

setup(
    name = 'cuckoo2mist',
    version = '0.4',
    packages = ['cuckoo2mist'],
    package_dir = {'cuckoo2mist': 'cuckoo2mist'},
    package_data = {'cuckoo2mist': ['conf/*.xml']},
    entry_points = {
        "console_scripts": ['cuckoo2mist = cuckoo2mist.cuckoo2mist:main']
    },
    install_requires = ['mmh3==2.5.1'],
    # Metadata
    author = 'Philipp Trinius, Navein Chanderan, Chang Si Ju',
)
