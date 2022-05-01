# -*- coding: utf-8 -*-

import dateutil.parser
from lxml import etree


class ServiceResponse:

    def __init__(self, xmlstr, tagname=None):
        self.xmlstr = xmlstr
        self.xmlstr_pretty = None
        self.parser = etree.XMLParser(remove_blank_text=True)
        self.parser_error = None
        try:
            self.root = etree.fromstring(xmlstr.encode("utf-8"), self.parser)
        except etree.XMLSyntaxError as err:
            self.parser_error = str(err)
            self.parser = etree.XMLParser(remove_blank_text=True, recover=True)
            try:
                self.root = etree.fromstring(xmlstr.encode("utf-8"), self.parser)
            except etree.XMLSyntaxError:
                self.root = None
        if self.root is not None:
            self.xmlstr_pretty = etree.tostring(self.tree(), pretty_print=True).decode()
        self.tagname = tagname

    def tree(self):
        if self.root is not None:
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
        if elem is not None and elem.text is not None:
            return elem.text.strip()

    def get_elems(self, tagname):
        xml_tree = self.tree()
        if xml_tree is not None:
            return xml_tree.findall("//{0}".format(tagname))
        return []

    def get_texts(self, tagname):
        elems = self.get_elems(tagname)
        if elems is not None:
            return [e.text.strip() for e in elems if e is not None and e.text is not None]
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

    def message(self):
        return self.text([self.tagname, "Message"])

    def found(self):
        if self.root is not None:
            if self.tagname is not None:
                payload = self.elem(self.tagname)
                if payload is not None:
                    if len(payload.getchildren()) > 0:
                        message = self.message()
                        if message == 'An invalid security token was provided':
                            return None
                        return True
                    return False


class TitleDetails(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="GetTitleDetailsResponse")

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

    def get_rsn_main(self):
        return self.text("MainRSN")

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

    def get_corporate_author_display(self):
        return self.texts(["CorporateAuthor", "CorporateAuthors", "CorporateAuthorDisplayForm"])

    def get_gmd_code(self):
        return self.text(["GMD", "Code"])

    def get_gmd_desc(self):
        return self.text(["GMD", "Description"])

    def get_url(self):
        return self.text(["GetTitleDetailsResult", "URL"])

    def get_urls(self):
        return self.texts(["URLs", "URL", "URL"])

    def get_url_main(self):
        return self.text("MainURL")

    def get_subtitle(self):
        return self.text("SubTitle")

    def get_subtitle_clean(self):
        return self.clean_title(self.get_subtitle())

    def get_series(self):
        return self.text("Series")

    def get_series_clean(self):
        return self.clean_title(self.get_series())

    def get_series_key_display(self):
        return self.texts(["SeriesKey", "SeriesKeys", "SeriesKeyDisplayForm"])

    def get_series_key_display_clean(self):
        return [self.clean_title(t) for t in self.get_series_key_display()]

    def get_serial_rsns(self):
        return self.texts(["SerialYear", "SerialYears", "RSN"])

    def get_serial_years(self):
        return self.texts(["SerialYear", "SerialYears", "YYYY"])

    def get_frequency(self):
        return self.text("Frequency")

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

    def get_number_of_orders(self):
        return self.text("NumberOfOrders")

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

    def get_issn(self):
        return self.text("ISSN")

    def get_alternate_issn(self):
        return self.texts(["AlternateISSNs", "AlternateISSNs", "AlternateISSN"])

    def get_isbn(self):
        return self.text("ISBN")

    def get_alternate_isbn(self):
        return self.texts(["AlternateISBNs", "AlternateISBNs", "AlternateISBN"])

    def get_class_main(self):
        return self.text("ClassMain")

    def get_classifications(self):
        return self.texts(["Classification", "Classifications", "Classification"])


class ItemDetails(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="GetItemDetailsResponse")

    def get_rsn(self):
        return self.text("RSNText")

    def get_barcode(self):
        return self.text("Barcode")

    def get_callnumber(self):
        return self.text(["GetItemDetailsResult", "CallNumber"])

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
        if datetime is not None:
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

    def get_cost_trans_order_num(self):
        return self._get_cost_trans_latest_field("OrderNum")

    def get_cost_trans_invoice_num(self):
        return self._get_cost_trans_latest_field("InvoiceNum")

    def get_cost_trans_budget_year(self):
        return self._get_cost_trans_latest_field("BudgetYear")

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
        if datetime is not None:
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

    def get_supplier_code(self):
        return self.text("SupplierCode")

    def get_order_code(self):
        return self.text("OrderCode")

    def get_order_number(self):
        return self.text("OrderNumber")

    def get_order_line(self):
        return self.text("OrderLine")

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


class OrderStatus(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="OrderStatusResponse")

    def get_status(self):
        return self.text("Status")

    def get_message(self):
        return self.text("Message")


class OrderInformation(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="OrderInformationResponse")

    def get_id(self):
        return self.text("ID")

    def get_order_code(self):
        return self.text("OrderCode")

    def is_open(self):
        return self.text("OpenOrder")

    def found(self):
        result = self.elem("OrderInformationResult")
        if result is not None:
            if len(result.getchildren()) > 0:
                return True
            return False


class OrderLineInformation(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="OrderLineInformationResponse")

    def get_title(self):
        return self.text("Title")

    def get_invoice_number(self):
        return self.text("InvoiceNumber")

    def get_invoice_date(self):
        return self.text("InvoiceDate")

    def get_delivery_date(self):
        return self.text("ExpectedDeliveryDate")

    def get_date_ordered(self):
        return self.text("DateOrdered")

    def get_date_paid(self):
        return self.text("DatePaid")

    def get_date_printed(self):
        return self.text("DatePrinted")

    def get_print_status(self):
        return self.text("PrintStatus")

    def get_payment_date(self):
        return self.text("ExpectedPaymentDate")

    def get_order_status(self):
        return self.text("OrderStatus")

    def get_order_type(self):
        return self.text("OrderType")

    def get_order_code(self):
        return self.text("OrderCode")

    def get_order_line(self):
        return self.text("OrderLine")

    def get_barcode(self):
        return self.text("Barcode")

    def get_acquisition(self):
        return self.text("Acquisition")

    def get_budget_year(self):
        return self.text("BudgetYear")

    def get_supplier_id(self):
        return self.text("SupplierID")

    def get_supplier_code(self):
        return self.text("SupplierCode")

    def get_claim_code(self):
        return self.text("ClaimCode")

    def get_owner_branch(self):
        return self.text("OwnerBranch")

    def get_dispatch_code(self):
        return self.text("DispatchCode")
