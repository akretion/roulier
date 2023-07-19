#!/usr/bin/env python

from setuptools import setup, find_packages

version = open("VERSION").read().strip()
download_url = "https://github.com/akretion/roulier/archive/%s.zip" % version
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="roulier",
    version=version,
    packages=find_packages(),
    install_requires=[
        "lxml",
        "Jinja2",
        "requests",
        "cerberus",
        "zplgrf",
        "unidecode",
        "pycountry",
    ],
    extras_requires={
        "dev": ["ptpython", "pytest"],
    },
    author="Hparfr <https://github.com/hparfr>",
    author_email="roulier@hpar.fr",
    description="Label parcels without pain",
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={"roulier": ["*.xml", "*.xsl", "*.zpl"]},
    url="https://github.com/akretion/roulier",
    download_url=download_url,
    keywords=["carrier", "logistics", "delivery"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3.6",
    ],
)
