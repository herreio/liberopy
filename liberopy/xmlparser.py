# -*- coding: utf-8 -*-
"""
Parser classes for XML serialized data retrieved via Libero Web Services SOAP API
"""

import base64
import dateutil.parser
from lxml import etree

from . import mabparser


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
        if self.root is not None:   # and self.parser_error is None
            self.xmlstr_pretty = etree.tostring(self.tree(), encoding="UTF-8",
                                                xml_declaration=True,
                                                pretty_print=True).decode()
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
            xml_tree.write(path, encoding="UTF-8", xml_declaration=True,
                           pretty_print=True)

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
            return [e.text.strip() for e in elems
                    if e is not None and e.text is not None]
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


class ResultItem(ServiceResponse):

    def __init__(self, xmlstr, tagname="searchResultItems"):
        super().__init__(xmlstr, tagname=tagname)

    def get_rsn(self):
        return self.text("rsn")

    def get_author(self):
        return self.text("author")

    def get_title(self):
        return self.text("title")

    def get_publication(self):
        return self.text("publication")

    def get_publication_year(self):
        return self.text("publicationYear")

    def get_gmd(self):
        return self.text("gmd")

    def get_holdings(self):
        return self.text("holdings")

    def get_branch(self):
        return self.text("branch")

    def get_collection(self):
        return self.text("collection")

    def get_call_number(self):
        return self.text("callNumber")

    def get_isbn(self):
        return self.text("ISBN")

    def get_issn(self):
        return self.text("ISSN")

    def get_date_added(self):
        return self.text("dateAdded")

    def get_items_barcode(self):
        return self.texts(["barcodeItems", "BarcodeItem", "barcode"])

    def get_items_branch(self):
        return self.texts(["barcodeItems", "BarcodeItem", "branch"])

    def get_items_call_number(self):
        return self.texts(["barcodeItems", "BarcodeItem", "callNumber"])

    def get_items_collection(self):
        return self.texts(["barcodeItems", "BarcodeItem", "collection"])

    def get_items_exception(self):
        return self.texts(["barcodeItems", "BarcodeItem", "exception"])

    def get_items_status(self):
        return self.texts(["barcodeItems", "BarcodeItem", "status"])


class Title(ResultItem):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="GetTitleResponse")

    def get_elem_marc_data_items(self):
        return self.elem("MarcDataItems")

    def get_mab_data_items_xml_parser(self):
        marc_data_items_elems = self.get_elem_marc_data_items()
        if marc_data_items_elems is not None:
            return TitleMab(etree.tostring(marc_data_items_elems).decode())

    def get_mab_data_items_parser(self):
        mab_data_items_xml = self.get_mab_data_items_xml_parser()
        if mab_data_items_xml is not None:
            return mab_data_items_xml.get_parser()


class TitleMab(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="MarcDataItems")

    def to_dict(self):
        mab_data = {
            "_id": None,
            "_type": None,
            "_status": None,
            "_version": None,
            "_leader": None,
            "_fields": {}
        }
        tag_pattern = self.ns("tag")
        sequence_pattern = self.ns("seq")
        subfield_pattern = self.ns("subfield")
        mab_data_b64_pattern = self.ns("tagData")
        mab_elems = self.elems("MarcDataItem")
        for mab_elem in mab_elems:
            tag = mab_elem.find(tag_pattern).text[1:]
            mab_data_b64 = mab_elem.find(mab_data_b64_pattern)
            if mab_data_b64 is not None:
                mab_data_plain = base64.b64decode(mab_data_b64.text).decode("utf-8")
            if tag == "###":
                mab_data["_type"] = mab_data_plain[23]
                mab_data["_status"] = mab_data_plain[5]
                mab_data["_version"] = mab_data_plain[6:10]
                mab_data["_leader"] = mab_data_plain
                continue
            else:
                if tag not in mab_data["_fields"]:
                    mab_data["_fields"][tag] = []
                tag_data = mab_data["_fields"][tag]
                subfield = mab_elem.find(subfield_pattern).text
                sequence = mab_elem.find(sequence_pattern).text
                tag_data.append({
                  "indicator": subfield,
                  "sequence": int(sequence),
                  "value": mab_data_plain
                })
                mab_data["_fields"][tag] = tag_data
            if tag == "001":
                mab_data["_id"] = mab_data_plain
        return mab_data

    def get_parser(self):
        return mabparser.MabTitle(self.to_dict())


class ResultItems(ServiceResponse):

    def __init__(self, xmlstr, tagname):
        super().__init__(xmlstr, tagname=tagname)

    def get_total(self):
        num = self.text("Total")
        if num is not None:
            return int(num)

    def _get_list(self):
        items = []
        for item in self.elems("searchResultItems"):
            item_parsed = {}
            for field in item:
                tag = field.tag.replace("{http://libero.com.au}", "")
                item_parsed[tag] = field.text
            items.append(item_parsed)
        return items

    def get_list(self):
        return self._get_list()

    def items(self):
        for item in self.elems("searchResultItems"):
            yield ResultItem(etree.tostring(item).decode())


class Search(ResultItems):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, "SearchResponse")


class Catalogue(ResultItems):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, "CatalogueResponse")

    def get_term(self):
        return self.text("Term")


class TitleDetails(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="GetTitleDetailsResponse")

    @staticmethod
    def clean_title(title):
        title_clean = "[o.T.]"
        if isinstance(title, str):
            title_clean = title.replace("¬", "")
        return title_clean

    @staticmethod
    def clean_issn(issn):
        issn_clean = None
        if isinstance(issn, str):
            issn_clean = issn.replace("ISSN ", "")
        return issn_clean

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

    def get_mabtype(self):
        return self.text("MABType")

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

    def get_acronym(self):
        return self.text("Acronym")

    def get_expiry_date(self):
        return self.text("ExpiryDate")

    def get_successor(self):
        return self.text("ContinuedByTitle")

    def get_display_title(self):
        return self.text("DisplayTitle")

    def get_display_title_clean(self):
        return self.clean_title(self.get_display_title())

    def get_created_date(self):
        return self.text("CreatedDate")

    def get_oai_date(self):
        return self.text("OAIDate")

    def get_raw_created_date(self):
        return self.text("RawCreatedDate")

    def get_raw_created_datetime(self):
        return self.text("RawCreatedDateTime")

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
        return self.clean_issn(self.text("ISSN"))

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

    def get_cataloguing_level(self):
        return self.text("CataloguingLevel")

    def get_filing_indicator(self):
        return self.text("FilingIndicator")

    def get_opac_display_flag(self):
        return True if self.text("OPACDisplayFlag") == "true" else False

    def get_elem_mab(self):
        return self.elem("MAB")

    def get_mab_xml_parser(self):
        mab_elems = self.get_elem_mab()
        if mab_elems is not None:
            return TitleDetailsMab(etree.tostring(mab_elems).decode())

    def get_mab_parser(self):
        mab_xml = self.get_mab_xml_parser()
        if mab_xml is not None:
            return mab_xml.get_parser()


class TitleDetailsMab(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="MAB")

    def to_dict(self):
        mab_data = {
            "_id": None,
            "_type": None,
            "_status": None,
            "_version": None,
            "_leader": None,
            "_fields": {}
        }
        tag_pattern = self.ns("Tag")
        sequence_pattern = self.ns("Sequence")
        subfield_pattern = self.ns("Subfield")
        mab_data_plain_pattern = self.ns("MABDataPlain")
        mab_elems = self.elems("MAB")
        for mab_elem in mab_elems:
            tag = mab_elem.find(tag_pattern).text
            mab_data_plain = mab_elem.find(mab_data_plain_pattern)
            if mab_data_plain is not None:
                mab_data_plain = mab_data_plain.text
            if tag == "###":
                mab_data["_type"] = mab_data_plain[23]
                mab_data["_status"] = mab_data_plain[5]
                mab_data["_version"] = mab_data_plain[6:10]
                mab_data["_leader"] = mab_data_plain
            else:
                if tag not in mab_data["_fields"]:
                    mab_data["_fields"][tag] = []
                tag_data = mab_data["_fields"][tag]
                subfield = mab_elem.find(subfield_pattern).text
                sequence = mab_elem.find(sequence_pattern).text
                tag_data.append({
                  "indicator": subfield,
                  "sequence": int(sequence),
                  "value": mab_data_plain
                })
                mab_data["_fields"][tag] = tag_data
            if tag == "001":
                mab_data["_id"] = mab_data_plain
        return mab_data

    def get_parser(self):
        return mabparser.MabTitle(self.to_dict())


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

    def get_expected_delivery_date(self):
        return self.text("ExpectedDeliveryDate")

    def get_date_ordered(self):
        return self.text("DateOrdered")

    def get_date_paid(self):
        return self.text("DatePaid")

    def get_date_printed(self):
        return self.text("DatePrinted")

    def get_print_status(self):
        return self.text("PrintStatus")

    def get_expected_payment_date(self):
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


class Item(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="GetItemByBarcodeResponse")

    def get_rsn(self):
        return self.text("RSN")

    def get_rid(self):
        return self.text("RID")

    def get_barcode(self):
        return self.text("barcode")

    def get_branch(self):
        return self.text("branchAt")

    def get_date_purchased(self):
        return self.text("purchaseDate")

    def get_branch_purchased(self):
        return self.text("purchasedBy")

    def get_supplier_code(self):
        return self.text("supplierCode")

    def get_branch_owner(self):
        return self.text("ownerBranch")

    def get_exception_code(self):
        return self.text("exceptionCode")

    def get_collection_code(self):
        return self.text("collectionCode")

    def get_call_number(self):
        return self.text("callNumber")

    def get_acquisition_type(self):
        return self.text("acquisitionType")

    def get_statistics(self):
        return self.text("statistic1")

    def get_inventory_number(self):
        return self.text("inventoryNumber")

    def get_gmd_code(self):
        return self.text("gmd")

    def get_stack_location_code(self):
        return self.text("stackLocation")

    def get_call_numbers(self):
        return self.texts(["callNumberList", "callNumberListItem"])

    def get_item_notes(self):
        return self.text("itemNotes")

    def get_review_date(self):
        return self.text("reviewDate")

    def get_volume_title_ref(self):
        return self.text("volumeTitleRef")

    def get_serials_issue_sort_code(self):
        return self.text("serialsIssueSortCode")


class MabBlock(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="GetMABBlockResponse")


class MarcBlock(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="GetMARCBlockResponse")


class MemberInformation(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="GetMemberInformationResponse")

    def get_field(self, name):
        return self.text(["Fields[@field=\"{0}\"]".format(name), "value"])

    def get_code(self):
        return self.get_field("Code")

    def get_key(self):
        return self.get_field("Key")

    def get_email(self):
        return self.get_field("Email")

    def get_given_name(self):
        return self.get_field("GivenName")

    def get_surname(self):
        return self.get_field("Surname")


class MemberDetails(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="GetMemberDetailsResponse")

    def get_borrower_id(self):
        return self.text("BorrowerID")

    def get_borrower_code(self):
        return self.text("BorrowerCode")

    def get_email_address(self):
        return self.text("EmailAddress")

    def get_short_name(self):
        return self.text("ShortName")

    def get_given_name(self):
        return self.text("GivenNames")

    def get_surname(self):
        return self.text("Surname")


class Branches(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="BranchResponse")

    def get_codes(self):
        return self.texts(["Branches", "Code"])

    def get_descriptions(self):
        return self.texts(["Branches", "Description"])

    def get_opac_selections(self):
        return self.texts(["Branches", "OPACSelection"])
