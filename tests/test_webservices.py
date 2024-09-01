import logging
import random
import unittest
import liberopy

connections = {
"BAL": "https://bacharchiv.libero-is.de/libero",
"HGB": "https://hgb.libero-is.de/libero",
"ZUR": "https://opac.kunsthaus.ch/libero",
"PDB": "https://biblio.parlament.ch/libero",
"CAS": "https://richmondvalley.libero.com.au/libero",
"SAR": "https://opac.saarbruecken.de/libero",
"LHS": "https://heinsberg.libero-is.de/libero",
"COT": "https://web-opac.bibliothek-cottbus.de/libero",
"UPS": "https://webopacups.urbe.it/libero",
"KON": "https://libero.ub.uni-konstanz.de/libero",
"UOM": "https://library.uom.ac.mu/libero"
}

db_choices = list(connections.keys())
db_choices_max_i = len(db_choices) - 1


class LiberoClientTestCase(unittest.TestCase):

    def setUp(self):
        self.db = db_choices[random.randint(0, db_choices_max_i)]
        self.client = liberopy.WebServices(
            connections[self.db],
            db=self.db,
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

    def test_search(self):
        self.search = self.client.search("Harry Potter")
        if self.search is None:
           print(f"Search via database {self.db} is None.")
        else:
           self.assertIsInstance(self.search.get_total(), int)

    def test_search_count(self):
        self.search_count = self.client.search_count("Harry Potter")
        if self.search_count is None:
           print(f"Search count via database {self.db} is None.")
        else:
           self.assertIsInstance(self.search_count, int)


if __name__ == '__main__':
    unittest.main()
