# -*- coding: utf-8 -*-

__author__ = "Donatus Herre <donatus.herre@slub-dresden.de>"
__version__ = "2021.8.13"
__license__ = "GPLv3"

import logging
from .webservices import WebServices

logger = logging.getLogger("liberopy")
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
stream.setFormatter(formatter)
logger.addHandler(stream)
logger.setLevel(logging.DEBUG)
