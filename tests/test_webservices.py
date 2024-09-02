import logging
import random
import unittest
import liberopy

connections = {
#"BAL": "https://bacharchiv.libero-is.de/libero",
"BVS": "https://begavalley.libero.com.au/libero",
"BHL": "https://brokenhill.libero.com.au/libero",
"GLI": "https://glen-innes.libero.com.au/libero",
"HGB": "https://hgb.libero-is.de/libero",
#"ZUR": "https://opac.kunsthaus.ch/libero",
"PPP": "https://catalogue.mnclibrary.org.au/libero",
#"PDB": "https://biblio.parlament.ch/libero",
"CAS": "https://richmondvalley.libero.com.au/libero",
"SAR": "https://opac.saarbruecken.de/libero",
"LHS": "https://heinsberg.libero-is.de/libero",
"COT": "https://web-opac.bibliothek-cottbus.de/libero",
"UPS": "https://webopacups.urbe.it/libero",
"KON": "https://libero.ub.uni-konstanz.de/libero"#,
#"UOM": "https://library.uom.ac.mu/libero"
}

db_choices = list(connections.keys())
db_choices_max_i = len(db_choices) - 1
db_chosen = db_choices[random.randint(0, db_choices_max_i)]
print(f"The database {db_chosen} was chosen for this test ----------------------------")

class LiberoClientTestCase(unittest.TestCase):

    def setUp(self):
        self.db = db_chosen
        self.client = liberopy.WebServices(
            connections[db_chosen],
            db=db_chosen,
            loglevel=logging.WARNING
        )

    def test_init(self):
        self.assertEqual(self.client.domain, connections[self.db])

    def test_newitems(self):
        self.newitems = self.client.newitems()
        if self.newitems is None:
            print(f"Newitems via database {self.db} is None.")
        else:
            self.assertIsInstance(self.newitems.get_total(), int)
            self.newitems_list = self.newitems.get_list()
            self.assertIsInstance(self.newitems_list, list)

    def test_search(self):
        self.search = self.client.search("Harry Potter")
        if self.search is None:
            print(f"Search via database {self.db} is None.")
        else:
            self.assertIsInstance(self.search.get_total(), int)
            self.search_list = self.search.get_list()
            self.assertIsInstance(self.search_list, list)
            if len(self.search_list) > 0:
                self.search_list_item = self.search_list[random.randint(0, len(self.search_list) - 1)]
                if self.search_list_item is not None:
                    self.assertIsInstance(self.search_list_item, dict)
                else:
                    print(f"Search list item via database {self.db} is None.")
            else:
                print(f"Search via database {self.db} returned 0 items.")

    def test_search_count(self):
        self.search_count = self.client.search_count("Harry Potter")
        if self.search_count is None:
            print(f"Search count via database {self.db} is None.")
        else:
            self.assertIsInstance(self.search_count, int)


if __name__ == '__main__':
    unittest.main()
