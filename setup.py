# -*- coding: utf-8 -*-

import setuptools

setuptools.setup(
    name="liberopy",
    version="2021.8.28",
    author="Donatus Herre",
    author_email="donatus.herre@slub-dresden.de",
    description="LIBERO Web Services API Client",
    license=open("LICENSE").read(),
    url="https://github.com/herreio/liberopy",
    packages=["liberopy"],
    install_requires=["requests", "lxml", "python-dateutil"],
)
