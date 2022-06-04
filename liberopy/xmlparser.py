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

    def get_mab(self):
        return self.elem("MAB")

    def get_mab_xml(self):
        mab_elems = self.get_mab()
        if mab_elems is not None:
            return TitleDetailsMab(etree.tostring(mab_elems).decode())

    def get_mab_json(self):
        mab_xml = self.get_mab_xml()
        if mab_xml is not None:
            return mab_xml.get_json()


class TitleDetailsMab(ServiceResponse):

    def __init__(self, xmlstr):
        super().__init__(xmlstr, tagname="MAB")
        self.data = self._transform()

    def _transform(self):
        mab_data = {
            "_id": None,
            "_type": None,
            "_status": None,
            "_version": None,
            "_fields": {}
        }
        tag_pattern = self.ns("Tag")
        sequence_pattern = self.ns("Sequence")
        subfield_pattern = self.ns("Subfield")
        mab_data_plain_pattern = self.ns("MABDataPlain")
        mab_elems = self.elems("MAB")
        for mab_elem in mab_elems:
            tag = mab_elem.find(tag_pattern).text
            subfield = mab_elem.find(subfield_pattern).text
            sequence = mab_elem.find(sequence_pattern).text
            mab_data_plain = mab_elem.find(mab_data_plain_pattern)
            if mab_data_plain is not None:
                mab_data_plain = mab_data_plain.text
            if tag not in mab_data["_fields"]:
                mab_data["_fields"][tag] = []
            tag_data = mab_data["_fields"][tag]
            tag_data.append({
              "indicator": subfield,
              "sequence": int(sequence),
              "value": mab_data_plain
            })
            mab_data["_fields"][tag] = tag_data
            if tag == "###":
                mab_data["_type"] = mab_data_plain[23]
                mab_data["_status"] = mab_data_plain[5]
                mab_data["_version"] = mab_data_plain[6:10]
            elif tag == "001":
                mab_data["_id"] = mab_data_plain
        return mab_data

    def get_json(self):
        return MabJson(self.data)


class MabJson:
    """
    Die Entwicklung und Pflege von MAB (seit 1995 MAB2) ist 2006
    abgeschlossen worden, das Format wurde »eingefroren«.

    Vgl. https://format.gbv.de/mab
    """

    def __init__(self, data):
        self.data = data

    def get_id(self):
        if isinstance(self.data, dict) and "_id" in self.data:
            return self.data["_id"]

    def get_type(self):
        if isinstance(self.data, dict) and "_type" in self.data:
            return self.data["_type"]

    def get_status(self):
        if isinstance(self.data, dict) and "_status" in self.data:
            return self.data["_status"]

    def get_version(self):
        if isinstance(self.data, dict) and "_version" in self.data:
            return self.data["_version"]

    def get_fields(self):
        if isinstance(self.data, dict) and "_fields" in self.data:
            return self.data["_fields"]

    def get_field_tags(self):
        fields = self.get_fields()
        if isinstance(fields, dict):
            return list(fields.keys())

    def get_field(self, name):
        fields = self.get_fields()
        if isinstance(fields, dict) and name in fields:
            return fields[name]

    def get_value(self, fname, find=None):
        field = self.get_field(fname)
        if isinstance(field, list):
            for subfield in field:
                if "indicator" in subfield:
                    ind = subfield["indicator"]
                    if "value" in subfield:
                        if find is None:
                            return {"ind": ind, "val": subfield["value"]}
                        if ind == find:
                            return subfield["value"]

    def get_values(self, fname, reduce=True):
        field = self.get_field(fname)
        if isinstance(field, list):
            values = []
            for subfield in field:
                sf = {}
                if "indicator" in subfield:
                    sf["ind"] = subfield["indicator"]
                if "value" in subfield:
                    sf["val"] = subfield["value"]
                values.append(sf)
            if len(values) > 0:
                if reduce and len(values) == 1:
                    values = values[0]
                return values

    def get_ppn(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        001       IDENTIFIKATIONSNUMMER DES DATENSATZES

          Indikator:
          Blank = nicht definiert
        """
        return self.get_value("001")

    def get_date_entered(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        002       DATUM DER ERSTERFASSUNG / FREMDDATENUEBERNAHME

          Indikator:
          a = Datum der Ersterfassung
          b = Datum der Fremddatenuebernahme
        """
        return self.get_value("002")

    def get_latest_trans(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        003       DATUM DER LETZTEN KORREKTUR

          Indikator:
          Blank = nicht definiert
        """
        return self.get_value("003")

    def get_interational_ids(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        025       UEBERREGIONALE IDENTIFIKATIONSNUMMER

          Indikator:
          blank = nicht spezifiziert
          a     = DDB
          b     = BNB
          c     = Casalini libri
          e     = ekz
          f     = BNF
          g     = ZKA
          l     = LoC
          o     = OCLC
          z     = ZDB
        """
        return self.get_values("025")

    def get_dnb_id(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        025       UEBERREGIONALE IDENTIFIKATIONSNUMMER

          Indikator:
          a     = DNB
        """
        return self.get_value("025", "a")

    def get_loc_id(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        025       UEBERREGIONALE IDENTIFIKATIONSNUMMER

          Indikator:
          l     = LoC
        """
        return self.get_value("025", "l")

    def get_oclc_id(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        025       UEBERREGIONALE IDENTIFIKATIONSNUMMER

          Indikator:
          o     = OCLC
        """
        return self.get_value("025", "o")

    def get_zdb_id(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        025       UEBERREGIONALE IDENTIFIKATIONSNUMMER

          Indikator:
          z     = ZDB
        """
        return self.get_value("025", "z")

    def get_regional_ids(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        026       REGIONALE IDENTIFIKATIONSNUMMER

          Indikator:
          blank = nicht spezifiziert
          a     = Bibliotheksverbund Berlin-Brandenburg
          b     = Norddeutscher Bibliotheksverbund (bis 1996)
          c     = Bibliotheksverbund Niedersachsen/Sachsen-Anhalt
                  (bis 1996)
          d     = Nordrhein-Westfaelischer Bibliotheksverbund
          e     = Hessisches Bibliotheksinformationssystem
          f     = Suedwestdeutscher Bibliotheksverbund
          g     = Bibliotheksverbund Bayern
          h     = Gemeinsamer Bibliotheksverbund der Laender Bremen,
                  Hamburg, Mecklenburg-Vorpommern, Niedersachsen,
                  Sachsen-Anhalt, Schleswig-Holstein, Thueringen
                  (ab 1996)
        """
        return self.get_values("026")

    def get_swb_id(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        026       REGIONALE IDENTIFIKATIONSNUMMER

          Indikator:
          f     = Suedwestdeutscher Bibliotheksverbund
        """
        return self.get_value("026", sfname="f")

    def get_kxp_id(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        026       REGIONALE IDENTIFIKATIONSNUMMER

          Indikator:
          k     = K10plus
        """
        return self.get_value("026", sfname="k")

    def get_local_ids(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        027       LOKALE IDENTIFIKATIONSNUMMER

          Indikator:
          blank = nicht spezifiziert
          a     = gepruefte Identifikationsnummer
          b     = ungepruefte Identifikationsnummer
        """
        return self.get_values("027")

    def get_other_ids(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        029       SONSTIGE IDENTIFIKATIONSNUMMER DES VORLIEGENDEN
                  DATENSATZES

          Indikator:
          blank = nicht spezifiziert
        """
        return self.get_values("029")

    def get_date_published(self):
        """
        400-437   SEGMENT VEROEFFENTLICHUNGSVERMERK, UMFANG, BEIGABEN

        425       ERSCHEINUNGSJAHR(E)

          Indikator:
          blank = Erscheinungsjahr(e) in Vorlageform
          a     = Erscheinungsjahr(e) in Ansetzungsform
          b     = Erscheinungsjahr des ersten Bandes in Ansetzungsform
          c     = Erscheinungsjahr des letzten Bandes in Ansetzungsform
          p     = Publikationsdatum bei Tontraegern (P-Datum)
        """
        return self.get_values("425")

    def get_parent_rid(self):
        """
        451-496   SEGMENT GESAMTTITELANGABEN

        453       IDENTIFIKATIONSNUMMER DES 1. GESAMTTITELS

          Indikator:
          blank = nicht definiert
          m     = mehrbaendiges begrenztes Werk
          r     = Schriftenreihe oder anderes fortlaufendes
                  Sammelwerk
        """
        return self.get_values("453")

    def get_parent_title(self):
        """
        451-496   SEGMENT GESAMTTITELANGABEN

        454       1. GESAMTTITEL IN ANSETZUNGSFORM

          Indikator:
          blank = nicht spezifiziert
          a     = Verfasserwerk
          b     = Urheberwerk
          c     = Sachtitelwerk
        """
        return self.get_values("454")

    def get_predecessor(self):
        """
        501-539   SEGMENT FUSSNOTEN

        531       HINWEISE AUF FRUEHERE AUSGABEN UND BAENDE

          Indikator:
          blank = verbale Beschreibung
          x     = reziproke Beziehung
          y     = nicht reziproke Beziehung
          z     = nicht differenzierte Beziehung
        """
        return self.get_values("531")

    def get_parallel(self):
        """
        501-539   SEGMENT FUSSNOTEN

        532       HINWEISE AUF FRUEHERE UND SPAETERE SOWIE ZEITWEISE
                  GUELTIGE TITEL

          Indikator:
          blank = verbale Beschreibung
          x     = reziproke Beziehung
          y     = nicht reziproke Beziehung
          z     = nicht differenzierte Beziehung
        """
        return self.get_values("532")

    def get_successor(self):
        """
        501-539   SEGMENT FUSSNOTEN

        533       HINWEISE AUF SPAETERE AUSGABEN UND BAENDE

          Indikator:
          blank = verbale Beschreibung
          x     = reziproke Beziehung
          y     = nicht reziproke Beziehung
          z     = nicht differenzierte Beziehung
        """
        return self.get_values("533")

    def get_isbn(self):
        """
        540-589   SEGMENT STANDARDNUMMERN

        540       INTERNATIONALE STANDARDBUCHNUMMER (ISBN)

          Indikator:
          blank = ISBN formal nicht geprueft
          a     = ISBN formal richtig
          b     = ISBN formal falsch
          z     = keine ISBN, aber Einbandart und/oder Preis
        """
        return self.get_values("540")

    def get_ismn(self):
        """
        540-589   SEGMENT STANDARDNUMMERN

        541       INTERNATIONALE STANDARDNUMMER FUER MUSIKALIEN (ISMN)

          Indikator:
          blank = ISMN formal nicht geprueft
          a     = ISMN formal richtig
          b     = ISMN formal falsch
          z     = keine ISMN, aber Einbandart und/oder Preis
        """
        return self.get_values("541")

    def get_issn(self):
        """
        540-589   SEGMENT STANDARDNUMMERN

        542       INTERNATIONALE STANDARDNUMMER FUER FORTLAUFENDE
                  SAMMELWERKE (ISSN)

          Indikator:
          blank = ISSN formal nicht geprueft
          a     = ISSN formal richtig
          b     = ISSN formal falsch
          z     = keine ISSN, aber Einbandart und/oder Preis
        """
        return self.get_values("542")

    def get_numbers(self):
        """
        540-589   SEGMENT STANDARDNUMMERN

        551       VERLAGS-, PRODUKTIONS- UND BESTELLNUMMER VON MUSIKALIEN
                  UND TONTRAEGERN

          Indikator:
          blank = nicht spezifiziert
          a     = Verlags- und Firmenbestellnummer
          b     = Druckplattennummer bei Musikalien
          c     = Plattennummer
          d     = Setnummer
          e     = Produktionsnummer
          f     = Kompaktkassettennummer
        """
        return self.get_values("551")

    def get_article(self):
        """
        540-589   SEGMENT STANDARDNUMMERN

        553       ARTIKELNUMMER

          Indikator:
          blank = nicht spezifiziert
          a     = Internationale Artikelnummer (EAN)
          b     = Universal Product Code (UPC)
        """
        return self.get_values("553")

    def get_ean(self):
        """
        540-589   SEGMENT STANDARDNUMMERN

        553       ARTIKELNUMMER

          Indikator:
          a     = Internationale Artikelnummer (EAN)
        """
        return self.get_value("553", "a")

    def get_upc(self):
        """
        540-589   SEGMENT STANDARDNUMMERN

        553       ARTIKELNUMMER

          Indikator:
          b     = Universal Product Code (UPC)
        """
        return self.get_value("553", "b")

    def get_statistics_code(self):
        """
        9XX RSWK-Schlagwortketten

        997       DBS-FACHGRUPPE MIT UNTERGRUPPE
        """
        return [t["val"] for t in self.get_values("997")]


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
