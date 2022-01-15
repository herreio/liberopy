# -*- coding: utf-8 -*-

import setuptools

setuptools.setup(
    name="liberopy",
    version="2022.1.18",
    author="Donatus Herre",
    author_email="donatus.herre@slub-dresden.de",
    description="LIBERO Web Services SOAP API Client",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license=open("LICENSE").read(),
    url="https://github.com/herreio/liberopy",
    packages=["liberopy"],
    install_requires=["requests", "lxml", "python-dateutil"],
)
