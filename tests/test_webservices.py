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
    "KON": "https://libero.ub.uni-konstanz.de/libero",
    "SAR": "https://opac.saarbruecken.de/libero"
}

connections = {
    **connections_mab,
    #**connections_marc,
    #**connections_marc_ch,
    **connections_marc_de
}

db_choices = list(connections.keys())
db_choices_max_i = len(db_choices) - 1
db_chosen = db_choices[random.randint(0, db_choices_max_i)]
print(f"The database {db_chosen} was chosen for the tests ----------------------------\n")

search_query = "har"


class LiberoClientTestCase(unittest.TestCase):

    def setUp(self):
        self.db = db_chosen
        self.q = search_query
        self.client = liberopy.WebServices(
            connections[db_chosen],
            db=db_chosen,
            loglevel=logging.WARNING
        )
        self.format = "MAB2" if db_chosen in connections_mab else "MARC21"


class LiberoClientInitTestCase(LiberoClientTestCase):

    def test_init(self):
        self.assertEqual(self.client.domain, connections[self.db])


class LiberoClientNewitemsTestCase(LiberoClientTestCase):

    def test_newitems_title_item(self):
        self.newitems = self.client.newitems()
        if self.newitems is None:
            pass
        else:
            self.newitems_total = self.newitems.get_total()
            self.assertIsInstance(self.newitems_total, int)
            self.newitems_list = self.newitems.get_list()
            self.assertIsInstance(self.newitems_list, list)
            if len(self.newitems_list) < 1:
                print(f"Search newitems via database {self.db} returned 0 items.")
            else:
                self.newitems_list_record = self.newitems_list[random.randint(0, len(self.newitems_list) - 1)]
                self.assertIsInstance(self.newitems_list_record, dict)
                self.assertIn("rsn", self.newitems_list_record)
                self.newitems_list_record_rsn = self.newitems_list_record["rsn"]
                # retrieval of title metadata
                self.newitems_list_record_title = self.client.title(self.newitems_list_record_rsn)
                if self.newitems_list_record_title is None:
                    pass
                else:
                    self.assertEqual(self.newitems_list_record_rsn, self.newitems_list_record_title.get_rsn())
                    self.newitems_list_record_barcodes = self.newitems_list_record_title.get_items_barcode()
                    self.assertIsInstance(self.newitems_list_record_barcodes, list)
                    if len(self.newitems_list_record_barcodes) < 1:
                        print(f"Title with RSN {self.newitems_list_record_rsn} from database {self.db} has no barcode.")
                    else:
                        self.newitems_list_record_barcode = self.newitems_list_record_barcodes[random.randint(0, len(self.newitems_list_record_barcodes) - 1)]
                        # retrieval of item metadata
                        self.newitems_list_record_item = self.client.item(self.newitems_list_record_barcode)
                        if self.newitems_list_record_item is None:
                            pass
                        else:
                            self.assertEqual(self.newitems_list_record_barcode, self.newitems_list_record_item.get_barcode())
                            self.newitems_list_record_rid = self.newitems_list_record_item.get_rid()
                            if self.newitems_list_record_rid is None:
                                print(f"Item with barcode {self.newitems_list_record_barcode} from database {self.db} has no RID.")
                            else:
                                # retrieval of RSN via RID
                                rsn = self.client.rid2rsn(self.newitems_list_record_rid)
                                self.assertEqual(self.newitems_list_record_rsn, rsn)
                                # retrieval of barcodes via RID
                                bcs = self.client.rid2bc(self.newitems_list_record_rid)
                                self.assertIsInstance(bcs, list)
                                self.assertIn(self.newitems_list_record_barcode, bcs)


class LiberoClientSearchTestCase(LiberoClientTestCase):

    def test_search_title_item(self):
        self.search = self.client.search(self.q)
        if self.search is None:
            pass
        else:
            self.search_total = self.search.get_total()
            self.assertIsInstance(self.search_total, int)
            # retrieval of search count
            self.search_count = self.client.search_count(self.q)
            if self.search_count is None:
                pass
            else:
                self.assertIsInstance(self.search_count, int)
                self.assertEqual(self.search_count, self.search_total)
            self.search_list = self.search.get_list()
            self.assertIsInstance(self.search_list, list)
            if len(self.search_list) < 1:
                print(f"Search for query {self.q} via database {self.db} returned 0 items.")
            else:
                self.search_list_record = self.search_list[random.randint(0, len(self.search_list) - 1)]
                self.assertIsInstance(self.search_list_record, dict)
                self.assertIn("rsn", self.search_list_record)
                self.search_list_record_rsn = self.search_list_record["rsn"]
                # retrieval of title metadata
                self.search_list_record_title = self.client.title(self.search_list_record_rsn)
                if self.search_list_record_title is None:
                    pass
                else:
                    self.assertEqual(self.search_list_record_rsn, self.search_list_record_title.get_rsn())
                    self.search_list_record_barcodes = self.search_list_record_title.get_items_barcode()
                    self.assertIsInstance(self.search_list_record_barcodes, list)
                    if len(self.search_list_record_barcodes) < 1:
                        print(f"Title with RSN {self.search_list_record_rsn} from database {self.db} has no barcode.")
                    else:
                        self.search_list_record_barcode = self.search_list_record_barcodes[random.randint(0, len(self.search_list_record_barcodes) - 1)]
                        # retrieval of item metadata
                        self.search_list_record_item = self.client.item(self.search_list_record_barcode)
                        if self.search_list_record_item is None:
                            pass
                        else:
                            self.assertEqual(self.search_list_record_barcode, self.search_list_record_item.get_barcode())
                            self.search_list_record_rid = self.search_list_record_item.get_rid()
                            if self.search_list_record_rid is None:
                                print(f"Item with barcode {self.search_list_record_barcode} from database {self.db} has no RID.")
                            else:
                                # retrieval of RSN via RID
                                rsn = self.client.rid2rsn(self.search_list_record_rid)
                                self.assertEqual(self.search_list_record_rsn, rsn)
                                # retrieval of barcodes via RID
                                bcs = self.client.rid2bc(self.search_list_record_rid)
                                self.assertIsInstance(bcs, list)
                                self.assertIn(self.search_list_record_barcode, bcs)


if __name__ == '__main__':
    unittest.main()
