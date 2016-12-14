#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = open('VERSION').read().strip()

setup(
    name="roulier",
    version=version,
    packages=find_packages(),
    install_requires=['lxml', 'Jinja2', 'requests', 'cerberus', 'zplgrf'],
    author="Hparfr <https://github.com/hparfr>",
    author_email="roulier@hpar.fr",
    description="Label parcels without pain",
    include_package_data=True,
    package_data={'roulier': ['*.xml', '*.xsl', '*.zpl']},
    url="https://github.com/akretion/roulier",
    download_url="https://github.com/akretion/roulier/tarball/0.1.0",
    keywords=['carrier', 'logistics', 'delivery'],
)
