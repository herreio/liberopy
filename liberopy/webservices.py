# -*- coding: utf-8 -*-

import re
import atexit
import requests
import dateutil.parser
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
        self.xmlstr_pretty = None
        self.parser = etree.XMLParser(remove_blank_text=True)
        self.parser_error = None
        try:
            self.root = etree.fromstring(xmlstr.encode("utf-8"), self.parser)
        except etree.XMLSyntaxError as err:
            self.parser_error = str(err)
            self.root = None
        if self.parser_error is None:
            self.xmlstr_pretty = etree.tostring(self.tree(), pretty_print=True).decode()

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

    def get_elem(self, tagname):
        xml_tree = self.tree()
        if xml_tree is not None:
            elem = xml_tree.find("//{0}".format(tagname))
            if elem is not None:
                return elem

    def get_text(self, tagname):
        elem = self.get_elem(tagname)
        if elem is not None:
            return elem.text.strip()

    def get_elems(self, tagname):
        xml_tree = self.tree()
        if xml_tree is not None:
            return xml_tree.findall("//{0}".format(tagname))
        return []

    def get_texts(self, tagname):
        elems = self.get_elems(tagname)
        if elems is not None:
            return [e.text.strip() for e in elems if elems]
        return []

    @staticmethod
    def ns(tagname):
        return "{{http://libero.com.au}}{0}".format(tagname)

    def ns_path(self, tagnames):
        return "/".join(self.ns(tagname) for tagname in tagnames)

    def ns_prep(self, tagname):
        if type(tagname) == str:
            return self.ns(tagname)
        elif type(tagname) == list:
            return self.ns_path(tagname)

    def elem(self, tag):
        return self.get_elem(self.ns_prep(tag))

    def elems(self, tag):
        return self.get_elems(self.ns_prep(tag))

    def text(self, tag):
        return self.get_text(self.ns_prep(tag))

    def texts(self, tag):
        return self.get_texts(self.ns_prep(tag))


class TitleDetails(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr)

    @staticmethod
    def clean_title(title):
        title_clean = "[o.T.]"
        if title is not None:
            title_clean = title.replace("¬", "")
        return title_clean

    def get_rid(self):
        return self.text("RID")

    def get_rsn(self):
        return self.text("RSN")

    def get_title(self):
        return self.text("Title")

    def get_title_clean(self):
        return self.clean_title(self.get_title())

    def get_mabtitle(self):
        return self.text("MABTitle")

    def get_main_author(self):
        return self.text("MainAuthor")

    def get_author_key(self):
        return self.text("AuthorKey")

    def get_author_display(self):
        return self.texts(["Author", "Authors", "AuthorDisplayForm"])

    def get_gmd_code(self):
        return self.text(["GMD", "Code"])

    def get_gmd_desc(self):
        return self.text(["GMD", "Description"])

    def get_subtitle(self):
        return self.text("SubTitle")

    def get_subtitle_clean(self):
        return self.clean_title(self.get_subtitle())

    def get_display_title(self):
        return self.text("DisplayTitle")

    def get_display_title_clean(self):
        return self.clean_title(self.get_display_title())

    def get_created_date(self):
        return self.text("CreatedDate")

    def get_raw_created_date(self):
        return self.text("RawCreatedDate")

    def get_last_saved_date(self):
        return self.text("LastSavedDate")

    def get_edit_date(self):
        return self.text("EditDate")

    def get_edit_user(self):
        return self.text("EditByUser")

    def get_collation(self):
        return self.text("Collation")

    def get_imprint(self):
        return self.text("Publication")

    def get_publication_year(self):
        return self.text("PublicationYear")

    def get_lang_code(self):
        return self.text(["Language", "Code"])

    def get_lang_desc(self):
        return self.text(["Language", "Description"])

    def get_stock_items(self):
        return self.texts(["StockItems", "StockItems", "Barcode"])

    def get_isbn(self):
        return self.texts(["AlternateISBNs", "AlternateISBNs", "AlternateISBN"])


class ItemDetails(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr)

    def get_rsn(self):
        return self.text("RSNText")

    def get_barcode(self):
        return self.text("Barcode")

    def get_callnumber(self):
        return self.text("CallNumber")

    def get_inventory_number(self):
        return self.text("InventoryNumber")

    def get_collection(self):
        return self.text("Collection")

    def get_lending_status(self):
        return self.text("LendingStatus")

    def get_status_description(self):
        return self.text("StatusDescription")

    def get_gmd_code(self):
        return self.text("GMD")

    def get_item_exception(self):
        return self.text("ItemException")

    def get_exception_flag(self):
        return self.text("ExceptionFlag")

    def get_times_issued(self):
        return self.text("TimesIssued")

    def get_total_issues(self):
        return self.text("TotalIssues")

    def get_title(self):
        return self.text("Title")

    def get_author(self):
        return self.text("Author")

    def get_date_purchased(self):
        return self.text("DatePurchased")

    def get_date_reviewed(self):
        return self.text("ReviewDate")

    def get_creation_user(self):
        return self.text("CreationUser")

    def get_creation_datetime(self):
        datetime = self.text("CreationDateTime")
        if datetime:
            return dateutil.parser.isoparse(datetime)

    def get_last_stocktake(self):
        return self.text("LastStocktake")

    def get_last_borrowed_date(self):
        return self.text("LastBorrowedDate")

    def get_newitem_actdate(self):
        return self.text("NewItemActDate")

    def get_newitem_exclude(self):
        return True if self.text(["AcquisitionType", "ExcludeFromNewItemList"]) == "true" else False

    def get_cost_trans_number_latest(self):
        return self.text("LastCostTransactionNumber")

    def _get_cost_trans(self, number):
        cost_trans_elems = self.elems(["CostTrans", "CostTransactions"])
        for cost_trans in cost_trans_elems:
            cost_trans_num = cost_trans.find(self.ns_prep("TransNumber"))
            if cost_trans_num is not None:
                if cost_trans_num.text == str(number):
                    return cost_trans

    def _get_cost_trans_latest(self):
        cost_trans_num = self.get_cost_trans_number_latest()
        if cost_trans_num is not None:
            return self._get_cost_trans(cost_trans_num)

    def _get_cost_trans_latest_field(self, field):
        cost_trans_elem = self._get_cost_trans_latest()
        if cost_trans_elem is not None:
            cost_trans_field_elem = cost_trans_elem.find(self.ns_prep(field))
            if cost_trans_field_elem is not None:
                return cost_trans_field_elem.text

    def get_cost_trans_date(self):
        return self._get_cost_trans_latest_field("TransDate")

    def get_cost_trans_type_code(self):
        return self._get_cost_trans_latest_field(["Type", "Code"])

    def get_cost_trans_type_desc(self):
        return self._get_cost_trans_latest_field(["Type", "Description"])

    def get_cost_trans_budget_year(self):
        return self._get_cost_trans_latest_field(["BudgetYear"])

    def _get_callnumbers(self):
        return self.elems(["ItemCallNumber", "CallNumbers"])

    def _get_callnumbers_field(self, field):
        target_values = []
        callnumber_elems = self._get_callnumbers()
        for callnumber_elem in callnumber_elems:
            target_elem = callnumber_elem.find(self.ns_prep(field))
            if target_elem is not None:
                target_values.append(target_elem.text)
        return target_values

    def get_callnumbers(self):
        return self._get_callnumbers_field("CallNumber")

    def get_callnumbers_maindates(self):
        callnumber_datetimes = []
        for callnumber_maindate_str in self._get_callnumbers_field("DateSetAsMainCallNumber"):
            if callnumber_maindate_str is not None:
                callnumber_datetimes.append(dateutil.parser.isoparse(callnumber_maindate_str))
        return callnumber_datetimes

    def _get_callnumber(self):
        callnumber = self.get_callnumber()
        callnumber_elems = self._get_callnumbers()
        for callnumber_elem in callnumber_elems:
            elem_num = callnumber_elem.find(self.ns_prep("CallNumber"))
            if elem_num is not None and elem_num.text == callnumber:
                return callnumber_elem

    def _get_callnumber_field(self, field):
        callnumber_elem = self._get_callnumber()
        target_elem = callnumber_elem.find(self.ns_prep(field))
        if target_elem is not None:
            return target_elem.text

    def get_callnumber_maindate(self):
        callnumber_datetime_str = self._get_callnumber_field("DateSetAsMainCallNumber")
        if callnumber_datetime_str is not None:
            return dateutil.parser.isoparse(callnumber_datetime_str)

    def get_exception_date(self):
        return self.text("ExceptionDate")

    def get_exception_datetime(self):
        datetime = self.text("ExceptionDateTime")
        if datetime:
            return dateutil.parser.isoparse(datetime)

    def get_acqtype_code(self):
        return self.text(["AcquisitionType", "Code"])

    def get_acqtype_desc(self):
        return self.text(["AcquisitionType", "Description"])

    def get_acqbranch_code(self):
        return self.text(["BranchPurchasedBy", "Code"])

    def get_acqbranch_desc(self):
        return self.text(["BranchPurchasedBy", "Description"])

    def get_ownerbranch_code(self):
        return self.text(["OwnerBranch", "Code"])

    def get_ownerbranch_desc(self):
        return self.text(["OwnerBranch", "Description"])

    def get_stacklocation_code(self):
        return self.text(["StackLocation", "Code"])

    def get_stacklocation_desc(self):
        return self.text(["StackLocation", "Description"])

    def get_statistics_code(self):
        return self.text(["Statistic1", "Code"])

    def get_statistics_desc(self):
        return self.text(["Statistic1", "Description"])

    def get_webopac_display(self):
        return True if self.text("WebOPACDisplay") == "true" else False


class ServicePackage:

    def __init__(self, base, name):
        self.base = base
        self.name = name
        self.path = "{0}.{1}.cls".format(self.base, self.name)
        self.logger = logger

    def get_request(self, url):
        try:
            response = requests.get(url, headers={"User-Agent": "liberopy 2021.10.27"})
        except requests.exceptions.RequestException as e:
            self.logger.error(e.__class__.__name__)
            return None
        if response.status_code != 200:
            self.logger.error("HTTP {0}".format(response.status_code))
            return None
        return response

    def soap_request(self, url, post=ServiceResponse):
        response = self.get_request(url)
        if response:
            return post(response.text)

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
        return self.soap_request(url, post=TitleDetails)

    def itemdetails(self, barcode):
        url = self.url_itemdetails(barcode)
        self.logger.info("Fetching item with barcode {0}.".format(barcode))
        return self.soap_request(url, post=ItemDetails)

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
