# -*- coding: utf-8 -*-

import atexit
import logging
import requests

from .xmlparser import ServiceResponse, ItemDetails, TitleDetails,\
    OrderInformation, OrderLineInformation, OrderStatus, NewItems

from . import __version__


class WebServices:

    def __init__(self, domain, loglevel=logging.DEBUG):
        self.domain = domain
        self.base = "{0}/LiberoWebServices".format(self.domain)
        self.token = None
        self.logger = None
        self.Authenticate = None
        self.LibraryAPI = None
        self._logger(loglevel)
        self.CatalogueSearcher = CatalogueSearcher(self.base, loglevel=self.logger.level)

    def _logger(self, level):
        self.logger = logging.getLogger("liberopy.WebServices")
        if not self.logger.handlers:
            stream = logging.StreamHandler()
            stream.setLevel(level)
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
            stream.setFormatter(formatter)
            self.logger.addHandler(stream)
            self.logger.setLevel(level)

    def login(self, user, password, patron=False):
        if self.token is not None:
            self.logout()
        self.Authenticate = Authenticate(self.base, user, password, patron=patron, loglevel=self.logger.level)
        if self.Authenticate.token:
            self.token = self.Authenticate.token
            self.LibraryAPI = LibraryAPI(self.base, self.token, loglevel=self.logger.level)

    def logout(self):
        if self.token is not None:
            self.token = None
            self.Authenticate.logout()
            self.Authenticate = None
            self.LibraryAPI = None
            return
        self.logger.warning("You are not logged in!")

    def rid2rsn(self, rid):
        return self.CatalogueSearcher.rid2rsn(rid)

    def newitems(self):
        return self.CatalogueSearcher.newitems()

    def itemdetails(self, barcode):
        if self.token is not None:
            return self.LibraryAPI.itemdetails(barcode)
        self.logger.error("You have to log in first!")

    def titledetails(self, rsn):
        if self.token is not None:
            return self.LibraryAPI.titledetails(rsn)
        self.logger.error("You have to log in first!")

    def orderstatus(self, on, ln):
        if self.token is not None:
            return self.LibraryAPI.orderstatus(on, ln)
        self.logger.error("You have to log in first!")

    def orderinfo(self, on):
        if self.token is not None:
            return self.LibraryAPI.orderinfo(on)
        self.logger.error("You have to log in first!")

    def orderlineinfo(self, on, ln):
        if self.token is not None:
            return self.LibraryAPI.orderlineinfo(on, ln)
        self.logger.error("You have to log in first!")


class ServicePackage:

    def __init__(self, base, name, loglevel=logging.DEBUG):
        self.base = base
        self.name = name
        self.path = "{0}.{1}.cls".format(self.base, self.name)
        self.logger = None
        self._logger(loglevel)

    def _logger(self, level):
        self.logger = logging.getLogger("liberopy.webservices.{0}".format(self.name))
        if not self.logger.handlers:
            stream = logging.StreamHandler()
            stream.setLevel(level)
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
            stream.setFormatter(formatter)
            self.logger.addHandler(stream)
            self.logger.setLevel(level)

    def get_request(self, url):
        try:
            response = requests.get(url, headers={"User-Agent": "liberopy {0}".format(__version__)})
        except requests.exceptions.RequestException as e:
            self.logger.error(e.__class__.__name__)
            return None
        if response.status_code != 200:
            self.logger.error("HTTP {0}".format(response.status_code))
            return None
        return response

    def soap_request(self, url, post=ServiceResponse):
        response = self.get_request(url)
        if response is not None:
            return post(response.text)

    @staticmethod
    def set_param(url, name, value):
        return "{0}?{1}={2}".format(url, name, value)

    def url_wsdl(self):
        return self.set_param(self.path, "wsdl", "1")

    def wsdl(self):
        url = self.url_wsdl()
        return self.soap_request(url)

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

    def __init__(self, base, token, loglevel=logging.DEBUG):
        super().__init__(base, "LibraryAPI", loglevel=loglevel)
        self.token = token

    def titledetails(self, rsn):
        url = self.url_titledetails(rsn)
        self.logger.info("Fetch title with RSN {0}.".format(rsn))
        return self.soap_request(url, post=TitleDetails)

    def itemdetails(self, barcode):
        url = self.url_itemdetails(barcode)
        self.logger.info("Fetch item with barcode {0}.".format(barcode))
        return self.soap_request(url, post=ItemDetails)

    def orderstatus(self, on, ln):
        url = self.url_orderstatus(on, ln)
        self.logger.info("Fetch status of order line {0}/{1}.".format(on, ln))
        return self.soap_request(url, post=OrderStatus)

    def orderinfo(self, on):
        url = self.url_orderinfo(on)
        self.logger.info("Fetch order {0}.".format(on))
        return self.soap_request(url, post=OrderInformation)

    def orderlineinfo(self, on, ln):
        url = self.url_orderlineinfo(on, ln)
        self.logger.info("Fetch order line {0}/{1}.".format(on, ln))
        return self.soap_request(url, post=OrderLineInformation)

    def url_itemdetails(self, barcode):
        url = self.method_path("GetItemDetails")
        url = self.add_barcode_to_url(url, barcode)
        return self.add_token_to_url(url, self.token)

    def url_titledetails(self, rsn):
        url = self.method_path("GetTitleDetails")
        url = self.add_rsn_to_url(url, rsn)
        return self.add_token_to_url(url, self.token)

    def url_orderstatus(self, on, ln):
        url = self.method_path("OrderStatus")
        url = self.add_ordernum_to_url(url, on)
        url = self.add_orderline_to_url(url, ln)
        return self.add_token_to_url(url, self.token)

    def url_orderinfo(self, on):
        url = self.method_path("OrderInformation")
        url = self.add_ordernum_to_url(url, on)
        return self.add_token_to_url(url, self.token)

    def url_orderlineinfo(self, on, ln):
        url = self.method_path("OrderLineInformation")
        url = self.add_ordernum_to_url(url, on)
        url = self.add_linenum_to_url(url, ln)
        return self.add_token_to_url(url, self.token)

    def add_rsn_to_url(self, url, rsn):
        return self.add_param(url, "RSN", rsn)

    def add_barcode_to_url(self, url, barcode):
        return self.add_param(url, "ItemBarcode", barcode)

    def add_ordernum_to_url(self, url, on):
        return self.add_param(url, "OrderNumber", on)

    def add_linenum_to_url(self, url, ln):
        return self.add_param(url, "LineNumber", ln)

    def add_orderline_to_url(self, url, ln):
        return self.add_param(url, "OrderLine", ln)


class CatalogueSearcher(ServicePackage):

    def __init__(self, base, loglevel=logging.DEBUG):
        super().__init__(base, "CatalogueSearcher", loglevel=loglevel)

    def newitems(self):
        url = self.url_newitems()
        self.logger.info("Search titles with new items in LIBERO.")
        return self.soap_request(url, post=NewItems)

    def rid2rsn(self, rid):
        url = self.url_rid2rsn(rid)
        self.logger.info("Fetch RSN for title with RID {0}.".format(rid))
        response = self.soap_request(url)
        if response is not None:
            return response.text("GetRsnByRIDResult")

    def url_rid2rsn(self, rid):
        url = self.method_path("GetRsnByRID")
        return self.add_rid_to_url(url, rid)

    def url_newitems(self):
        url = self.method_path("Catalogue")
        return self.add_type_to_url(url, "newitem")

    def add_rid_to_url(self, url, rid):
        return self.add_param(url, "RID", rid)


class Authenticate(ServicePackage):

    def __init__(self, base, user, password, patron=False, loglevel=logging.DEBUG):
        super().__init__(base, "Authenticate", loglevel=loglevel)
        if patron:
            self.token = self.patron_login(user, password)
        else:
            self.token = self.login(user, password)
        if self.token is not None:
            self.logger.info("Login successful!")
            self.logger.info("Set logout at exit.")
            atexit.register(self.logout)
        else:
            self.logger.error("Login failed!")

    def login(self, user, password):
        url = self.url_login(user, password)
        response = self.soap_request(url)
        if response is not None and response.text("Status") == "1":
            return response.text("Token")

    def patron_login(self, user, password):
        url = self.url_patron_login(user, password)
        response = self.soap_request(url)
        if response is not None and response.text("Status") == "1":
            return response.text("Token")

    def logout(self):
        if self.token:
            url = self.url_logout(self.token)
            response = self.soap_request(url)
            if response is not None and response.text("Status") == "1":
                atexit.unregister(self.logout)
                self.logger.info("Logout successful!")

    def url_login(self, user, password):
        url = self.method_path("Login")
        url = self.add_param(url, "Username", user)
        return self.add_param(url, "Password", password)

    def url_patron_login(self, user, password):
        url = self.method_path("PatronLogin")
        url = self.add_param(url, "Username", user)
        return self.add_param(url, "Password", password)

    def url_logout(self, token):
        url = self.method_path("Logout")
        return self.add_token_to_url(url, token)
