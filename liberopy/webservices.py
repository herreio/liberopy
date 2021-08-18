# -*- coding: utf-8 -*-

import re
import atexit
import requests
from lxml import etree

from .log import logger


class WebServices:

    def __init__(self, domain):
        self.domain = domain
        self.base = "{0}/LiberoWebServices".format(self.domain)
        self.token = None
        self.logger = logger
        self.Authenticate = None
        self.CatalogueSearcher = None
        self.LibraryAPI = None

    def login(self, user, password):
        if self.token:
            self.logout()
        self.Authenticate = Authenticate(self.base, user, password)
        if self.Authenticate.token:
            self.token = self.Authenticate.token
            self.CatalogueSearcher = CatalogueSearcher(self.base, self.token)
            self.LibraryAPI = LibraryAPI(self.base, self.token)

    def logout(self):
        if self.token:
            self.token = None
            self.Authenticate.logout()
            self.Authenticate = None
            self.CatalogueSearcher = None
            self.LibraryAPI = None
            return
        self.logger.warning("You are not logged in!")

    def newitems(self):
        if self.token:
            return self.CatalogueSearcher.newitems()
        self.logger.error("You have to login first!")

    def itemdetails(self, barcode):
        if self.token:
            return self.LibraryAPI.itemdetails(barcode)
        self.logger.error("You have to login first!")

    def titledetails(self, rsn):
        if self.token:
            return self.LibraryAPI.titledetails(rsn)
        self.logger.error("You have to login first!")


class ServiceResponse:

    def __init__(self, xmlstr):
        self.xmlstr = xmlstr
        self.parser = etree.XMLParser(remove_blank_text=True)
        self.parser_error = None
        try:
            self.root = etree.fromstring(xmlstr.encode("utf-8"), self.parser)
        except etree.XMLSyntaxError as err:
            self.parser_error = str(err)
            self.root = None

    def tree(self):
        if self.parser_error is None:
            return etree.ElementTree(self.root)

    def store(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.xmlstr)

    def store_pretty(self, path):
        xml_tree = self.tree()
        if xml_tree is not None:
            xml_tree.write(path, xml_declaration=True,
                           encoding="UTF-8", pretty_print=True)


class ServicePackage:

    def __init__(self, base, name):
        self.base = base
        self.name = name
        self.path = "{0}.{1}.cls".format(self.base, self.name)
        self.logger = logger

    def get_request(self, url):
        try:
            response = requests.get(url, headers={"User-Agent": "liberopy 2021.8.12"})
        except requests.exceptions.RequestException as e:
            self.logger.error(e.__class__.__name__)
            return None
        if response.status_code != 200:
            self.logger.error("HTTP {0}".format(response.status_code))
            return None
        return response

    def soap_request(self, url):
        response = self.get_request(url)
        if response:
            return ServiceResponse(response.text)

    @staticmethod
    def set_param(url, name, value):
        return "{0}?{1}={2}".format(url, name, value)

    def url_wsdl(self):
        return self.set_param(self.path, "wsdl", "1")

    def wsdl(self):
        response = self.get_request(self.url_wsdl())
        if response:
            return ServiceResponse(response.text)

    def method_path(self, method):
        return self.set_param(self.path, "soap_method", method)

    @staticmethod
    def add_param(url, name, value):
        return "{0}&{1}={2}".format(url, name, value)

    def add_token_to_url(self, url, token):
        return self.add_param(url, "TOKEN", token)

    def add_type_to_url(self, url, type):
        return self.add_param(url, "Type", type)


class LibraryAPI(ServicePackage):

    def __init__(self, base, token):
        super().__init__(base, "LibraryAPI")
        self.token = token

    def titledetails(self, rsn):
        url = self.url_titledetails(rsn)
        self.logger.info("Fetching title with RSN {0}.".format(rsn))
        return self.soap_request(url)

    def itemdetails(self, barcode):
        url = self.url_itemdetails(barcode)
        self.logger.info("Fetching item with barcode {0}.".format(barcode))
        return self.soap_request(url)

    def url_itemdetails(self, barcode):
        url = self.method_path("GetItemDetails")
        url = self.add_barcode_to_url(url, barcode)
        return self.add_token_to_url(url, self.token)

    def url_titledetails(self, rsn):
        url = self.method_path("GetTitleDetails")
        url = self.add_rsn_to_url(url, rsn)
        return self.add_token_to_url(url, self.token)

    def add_rsn_to_url(self, url, rsn):
        return self.add_param(url, "RSN", rsn)

    def add_barcode_to_url(self, url, barcode):
        return self.add_param(url, "ItemBarcode", barcode)


class CatalogueSearcher(ServicePackage):

    def __init__(self, base, token):
        super().__init__(base, "CatalogueSearcher")
        self.token = token

    def newitems(self):
        url = self.url_newitems()
        self.logger.info("Searching titles with newitems in LIBERO.")
        return self.soap_request(url)

    def url_newitems(self):
        url = self.method_path("Catalogue")
        url = self.add_type_to_url(url, "newitem")
        return self.add_token_to_url(url, self.token)


class Authenticate(ServicePackage):

    def __init__(self, base, user, password):
        super().__init__(base, "Authenticate")
        self.token = self.login(user, password)
        if self.token:
            self.logger.info("Login successful!")
            self.logger.info("Set logout at exit.")
            atexit.register(self.logout)
        else:
            self.logger.error("Login failed!")

    def login(self, user, password):
        url = self.url_login(user, password)
        response = self.get_request(url)
        if response and response.text:
            return self.extract_token(response.text)

    def logout(self):
        url = self.url_logout(self.token)
        response = self.get_request(url)
        if response:
            atexit.unregister(self.logout)
            self.logger.info("Logout successful!")

    def url_login(self, user, password):
        url = self.method_path("Login")
        url = self.add_param(url, "Username", user)
        return self.add_param(url, "Password", password)

    def url_logout(self, token):
        url = self.method_path("Logout")
        return self.add_token_to_url(url, token)

    @staticmethod
    def extract_token(response):
        found = re.search("<Token>(.+)</Token>", response)
        return found.groups()[0] if found else ""
