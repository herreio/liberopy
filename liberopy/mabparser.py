# -*- coding: utf-8 -*-
"""
Parser class for MAB formatted data retrieved via Libero Web Services SOAP API
"""

import datetime


class MabTitle:
    """
    The Maschinelles Austauschformat für Bibliotheken or MAB (literally
    translating as "machine data exchange format for libraries") is a
    bibliographic data exchange format.

    MAB was commonly used as an exchange format for metadata especially in
    German-speaking countries. ... The origins of MAB trace back to 1973 ...
    A comprehensive revision of MAB led to the new format version MAB2 in 1995
    ... In June 2013, the delivery of data in MAB format was finally abandoned.

    https://en.wikipedia.org/wiki/Maschinelles_Austauschformat_f%C3%BCr_Bibliotheken
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

    def get_leader(self):
        if isinstance(self.data, dict) and "_leader" in self.data:
            return self.data["_leader"]

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

    def get_date_entered_type(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        002       DATUM DER ERSTERFASSUNG / FREMDDATENUEBERNAHME

          Indikator:
          a = Datum der Ersterfassung
          b = Datum der Fremddatenuebernahme
        """
        find = self.get_date_entered()["ind"]
        if find == "a":
            return "Datum der Ersterfassung"
        elif find == "b":
            return "Datum der Fremddatenuebernahme"

    def get_date_entered_date(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        002       DATUM DER ERSTERFASSUNG / FREMDDATENUEBERNAHME
        """
        date_entered = self.get_date_entered()["val"]
        if date_entered is not None and len(date_entered.strip()) == 8:
            try:
                return datetime.datetime.strptime(date_entered, "%Y%m%d").date()
            except ValueError:
                pass

    def get_date_entered_iso(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        002       DATUM DER ERSTERFASSUNG / FREMDDATENUEBERNAHME
        """
        date_entered = self.get_date_entered_date()
        if date_entered is not None:
            return date_entered.isoformat()

    def get_latest_trans(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        003       DATUM DER LETZTEN KORREKTUR

          Indikator:
          Blank = nicht definiert
        """
        return self.get_value("003")

    def get_latest_trans_datetime(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        003       DATUM DER LETZTEN KORREKTUR
        """
        latest_trans = self.get_latest_trans()["val"]
        if latest_trans is not None:
            try:
                return datetime.datetime.strptime(latest_trans, "%Y%m%d%H%M%S")
            except ValueError:
                pass

    def get_latest_trans_iso(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        003       DATUM DER LETZTEN KORREKTUR
        """
        latest_trans = self.get_latest_trans_datetime()
        if latest_trans is not None:
            return latest_trans.isoformat()

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
        return self.get_value("026", "f")

    def get_kxp_id(self):
        """
        001-029   SEGMENT IDENTIFIKATIONSNUMMERN, DATUMS- UND VERSIONS-
                  ANGABEN

        026       REGIONALE IDENTIFIKATIONSNUMMER

          Indikator:
          k     = K10plus
        """
        return self.get_value("026", "k")

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
        return [t["val"] for t in self.get_values("997", reduce=False)]
