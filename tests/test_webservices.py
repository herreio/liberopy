import os
import logging
import random
import unittest
import liberopy

connections_mab = {
    "BAL": "https://bacharchiv.libero-is.de/libero",
    "HGB": "https://hgb.libero-is.de/libero",
    "LHS": "https://heinsberg.libero-is.de/libero"
}

connections_marc = {
    "BVS": "https://begavalley.libero.com.au/libero",
    "BHL": "https://brokenhill.libero.com.au/libero",
    "GLI": "https://glen-innes.libero.com.au/libero",
    "PPP": "https://catalogue.mnclibrary.org.au/libero",
    "CAS": "https://richmondvalley.libero.com.au/libero",
    "UPS": "https://webopacups.urbe.it/libero",
    "UOM": "https://library.uom.ac.mu/libero"  # v6.3
}

connections_marc_ch = {
    "ZUR": "https://opac.kunsthaus.ch/libero",
    "PDB": "https://biblio.parlament.ch/libero"
}

connections_marc_de = {
    "COT": "https://web-opac.bibliothek-cottbus.de/libero",
    "HBK": "https://opac.hfbk-dresden.de/libero",  # v6.3
    "KON": "https://libero.ub.uni-konstanz.de/libero",
    "SAR": "https://opac.saarbruecken.de/libero"
}

connections = {
    **connections_mab,
    **connections_marc,
    **connections_marc_ch,
    **connections_marc_de
}

try:
    db_chosen = os.environ["LIBEROPY_TEST_DB"]
    if db_chosen not in connections:
        raise KeyError
except KeyError:
    db_choices = list(connections.keys())
    db_chosen = db_choices[random.randint(0, len(db_choices) - 1)]

print(f"The database {db_chosen} was chosen for the tests ----------------------------\n")

try:
    search_query = os.environ["LIBEROPY_TEST_QUERY"]
except KeyError:
    search_query = "har"


class LiberoClientTestCase(unittest.TestCase):

    def setUp(self):
        self.db = db_chosen
        self.client = liberopy.WebServices(
            connections[self.db],
            db=self.db,
            loglevel=logging.WARNING
        )
        self.format = "MAB2" if self.db in connections_mab else "MARC21"


class LiberoClientInitTestCase(LiberoClientTestCase):

    def test_init(self):
        self.assertEqual(self.client.domain, connections[self.db])


class LiberoClientCatalogTestMixin(LiberoClientTestCase):

    def setUp(self):
        super().setUp()
        self.response = None
        self.results = None
        self.total = None
        self.record = None
        self.record_rsn = None
        self.record_title = None
        self.record_title_mab = None
        self.record_title_mab_id = None
        self.record_title_marc = None
        self.record_title_marc_id = None
        self.record_barcodes = None
        self.record_barcode = None
        self.record_item = None
        self.record_rid = None
        self.record_rsn_via_rid = None
        self.record_barcodes_via_rid = None
        self.record_marc = None
        self.record_marcp = None
        self.record_mab = None
        self.record_mabp = None

    def helperTitle(self, rsn):
        self.record_title = self.client.title(rsn)
        if self.record_title is None:
            pass
        else:
            self.assertEqual(rsn, self.record_title.get_rsn())
            self.helperTitleData(self.record_title)
            self.record_barcodes = self.record_title.get_items_barcode()
            self.assertIsInstance(self.record_barcodes, list)
            if len(self.record_barcodes) < 1:
                print(f"Title with RSN {rsn} from database {self.db} has no barcode.")
            else:
                self.record_barcode = self.record_barcodes[random.randint(0, len(self.record_barcodes) - 1)]

    def helperTitleData(self, tit):
        if self.format == "MARC21":
            self.helperTitleMarc(tit)
        elif self.format == "MAB2":
            self.helperTitleMab(tit)
        else:
            print(f"Format {self.format} is unknown. Please check.")

    def helperTitleMab(self, tit):
        self.record_title_mab = tit.get_mab_data_items_parser()
        self.record_title_mab_id = self.record_title_mab.get_id()
        self.assertIsInstance(self.record_title_mab_id, str)

    def helperTitleMarc(self, tit):
        self.record_title_marc = tit.get_marc_data_items_parser()
        self.record_title_marc_id = self.record_title_marc.get_id()
        self.assertIsInstance(self.record_title_marc_id, str)

    def helperItem(self, bc):
        self.record_item = self.client.item(bc)
        if self.record_item is None:
            pass
        else:
            self.assertEqual(bc, self.record_item.get_barcode())
            self.record_rid = self.record_item.get_rid()
            if self.record_rid is None:
                print(f"Item with barcode {bc} from database {self.db} has no RID.")

    def helperRid2Rsn(self, rid):
        self.record_rsn_via_rid = self.client.rid2rsn(rid)
        if self.record_rsn_via_rid is None:
            pass
        else:
            self.assertIsInstance(self.record_rsn_via_rid, str)
            self.assertEqual(self.record_rsn, self.record_rsn_via_rid)

    def helperRid2Bc(self, rid):
        self.record_barcodes_via_rid = self.client.rid2bc(rid)
        if self.record_barcodes_via_rid is None:
            pass
        else:
            self.assertIsInstance(self.record_barcodes_via_rid, list)
            self.assertIn(self.record_barcode, self.record_barcodes_via_rid)

    def helperBlock(self, rid):
        if self.format == "MARC21":
            self.helperMarcBlock(rid)
        elif self.format == "MAB2":
            self.helperMabBlock(rid)
        else:
            print(f"Format {self.format} is unknown. Please check.")

    def helperMarcBlock(self, rid):
        self.record_marc = self.client.marcblock(rid)
        if self.record_marc is None:
            pass
        else:
            self.assertIsInstance(self.record_marc, str)
            self.record_marcp = self.client.marcplain(rid)
            if self.record_marcp is None:
                pass
            else:
                self.assertIsInstance(self.record_marcp, str)
                self.record_marco = self.client.marcobject(rid)
                if self.record_marco is None:
                    pass
                else:
                    self.assertEqual(rid, self.record_marco.get("001").value())

    def helperMabBlock(self, rid):
        self.record_mab = self.client.mabblock(rid)
        if self.record_mab is None:
            pass
        else:
            self.assertIsInstance(self.record_mab, str)
            self.record_mabp = self.client.mabplain(rid)
            if self.record_mabp is None:
                pass
            else:
                self.assertIsInstance(self.record_mabp, str)

    def helperRecord(self, rsn):
        self.helperTitle(rsn)
        if self.record_barcode is not None:
            self.helperItem(self.record_barcode)
            if self.record_rid is not None:
                self.helperRid2Rsn(self.record_rid)
                self.helperRid2Bc(self.record_rid)
                self.helperBlock(self.record_rid)

    def helperResults(self):
        if isinstance(self.results, list):
            if len(self.results) < 1:
                print(f"Query via database {self.db} returned 0 records.")
            else:
                self.record = self.results[random.randint(0, len(self.results) - 1)]
                self.assertIsInstance(self.record, dict)
                self.assertIn("rsn", self.record)
                self.record_rsn = self.record["rsn"]
                if isinstance(self.record_rsn, str):
                    self.helperRecord(self.record_rsn)


class LiberoClientNewitemsTestCase(LiberoClientCatalogTestMixin):

    def setUp(self):
        super().setUp()

    def helperNewitems(self):
        self.response = self.client.newitems()
        if self.response is None:
            pass
        else:
            self.total = self.response.get_total()
            self.assertIsInstance(self.total, int)
            self.results = self.response.get_list()
            self.assertIsInstance(self.results, list)
            self.helperResults()

    def test_via_newitems(self):
        self.helperNewitems()


class LiberoClientSearchTestCase(LiberoClientCatalogTestMixin):

    def setUp(self):
        super().setUp()
        self.q = search_query
        self.count = None

    def helperSearch(self):
        self.response = self.client.search(self.q)
        if self.response is None:
            pass
        else:
            self.total = self.response.get_total()
            self.assertIsInstance(self.total, int)
            self.results = self.response.get_list()
            self.assertIsInstance(self.results, list)
            self.helperResults()

    def helperSearchCount(self):
        self.count = self.client.search_count(self.q)
        if self.count is None:
            pass
        else:
            self.assertIsInstance(self.count, int)
            self.assertEqual(self.count, self.total)

    def test_via_search(self):
        self.helperSearch()
        self.helperSearchCount()


if __name__ == '__main__':
    unittest.main()
