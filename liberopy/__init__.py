# -*- coding: utf-8 -*-
"""
``liberopy`` provides a Libero Web Services SOAP API client.
"""

__author__ = "Donatus Herre <donatus.herre@slub-dresden.de>"
__version__ = "2024.9.7"
__license__ = "GPLv3"

from . import xmlparser
from .webservices import WebServices

__all__ = ["xmlparser", "WebServices"]
