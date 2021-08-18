# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger("liberopy")
stream = logging.StreamHandler()
stream.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
stream.setFormatter(formatter)
logger.addHandler(stream)
logger.setLevel(logging.DEBUG)
