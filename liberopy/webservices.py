# -*- coding: utf-8 -*-

import re
import atexit
import requests
from lxml import etree


class WebServices:

    def __init__(self, domain):
        self.domain = domain
        self.base = "{0}/LiberoWebServices".format(self.domain)
        self.token = None
        self.Authenticate = None
        self.CatalogueSearcher = None
        self.LibraryAPI = None

    def login(self, user, password):
        self.Authenticate = Authenticate(self.base, user, password)
        if self.Authenticate.token:
            self.token = self.Authenticate.token
            self.CatalogueSearcher = CatalogueSearcher(self.base, self.token)
            self.LibraryAPI = LibraryAPI(self.base, self.token)

    def newitems(self):
        if self.token:
            return self.CatalogueSearcher.newitems()
        print("You have to login first!")

    def titledetails(self, rsn):
        if self.token:
            return self.LibraryAPI.titledetails(rsn)
        print("You have to login first!")


class ServiceResponse:

    def __init__(self, xmlstr):
        self.xmlstr = xmlstr
        self.parser = etree.XMLParser(remove_blank_text=True)
        self.root = etree.fromstring(xmlstr.encode("utf-8"), self.parser)

    def tree(self):
        return etree.ElementTree(self.root)

    def store(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.xmlstr)

    def store_pretty(self, path):
        xml_tree = self.tree()
        xml_tree.write(path, xml_declaration=True,
                       encoding="UTF-8", pretty_print=True)


class ServicePackage:

    def __init__(self, base, name):
        self.base = base
        self.name = name
        self.path = "{0}.{1}.cls".format(self.base, self.name)

    @staticmethod
    def get_request(url):
        response = requests.get(url)
        if response.status_code != 200:
            print("HTTP {0}".format(response.status_code))
            return None
        return response

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
        response = self.get_request(url)
        if response:
            return ServiceResponse(response.text)

    def url_titledetails(self, rsn):
        url = self.method_path("GetTitleDetails")
        url = self.add_rsn_to_url(url, rsn)
        return self.add_token_to_url(url, self.token)

    def add_rsn_to_url(self, url, rsn):
        return self.add_param(url, "RSN", rsn)


class CatalogueSearcher(ServicePackage):

    def __init__(self, base, token):
        super().__init__(base, "CatalogueSearcher")
        self.token = token

    def newitems(self):
        url = self.url_newitems()
        response = self.get_request(url)
        if response:
            return ServiceResponse(response.text)

    def url_newitems(self):
        url = self.method_path("Catalogue")
        url = self.add_type_to_url(url, "newitem")
        return self.add_token_to_url(url, self.token)


class Authenticate(ServicePackage):

    def __init__(self, base, user, password):
        super().__init__(base, "Authenticate")
        self.token = self.login(user, password)
        if self.token:
            print("Login successful!")
            print("Set logout at exit.")
            atexit.register(self.logout)
        else:
            print("Login failed!")

    def login(self, user, password):
        url = self.url_login(user, password)
        response = self.get_request(url)
        if response and response.text:
            return self._extract_token(response.text)

    def logout(self):
        url = self.url_logout(self.token)
        response = self.get_request(url)
        if response:
            print("Logout successful!")

    def url_login(self, user, password):
        url = self.method_path("Login")
        url = self.add_param(url, "Username", user)
        return self.add_param(url, "Password", password)

    def url_logout(self, token):
        url = self.method_path("Logout")
        return self.add_token_to_url(url, token)

    def _extract_token(self, response):
        found = re.search("<Token>(.+)</Token>", response)
        return found.groups()[0] if found else ""
