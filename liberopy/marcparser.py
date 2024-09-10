# -*- coding: utf-8 -*-
"""
Parser class for MARC formatted data retrieved via Libero Web Services SOAP API
"""

import datetime


class MarcTitle:
    """
    MARC (machine-readable cataloging) is a standard set of digital formats
    for the machine-readable description of items catalogued by libraries,
    such as books, DVDs, and digital resources. ...

    Working with the Library of Congress, American computer scientist
    Henriette Avram developed MARC between 1965 and 1968, making it possible
    to create records that could be read by computers and shared between
    libraries. By 1971, MARC formats had become the US national standard
    for dissemination of bibliographic data. Two years later, they became
    the international standard. ...

    https://en.wikipedia.org/wiki/MARC_standards
    """

    def __init__(self, data):
        self.data = data

    def get_id(self):
        if isinstance(self.data, dict) and "_id" in self.data:
            return self.data["_id"]

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

    def get_value(self, fname, fsub=None, find1=None, find2=None):
        field = self.get_field(fname)
        if isinstance(field, list):
            for subfield in field:
                if "value" in subfield:
                    if fname.startswith("00"):
                        return subfield["value"]
                    if "indicator1" in subfield and \
                            "indicator2" in subfield and \
                            "subfield" in subfield:
                        ind1 = subfield["indicator1"]
                        ind2 = subfield["indicator2"]
                        sub = subfield["subfield"]
                        if (find1 is None or find1 == ind1) and \
                                (find2 is None or find2 == ind2) and \
                                (fsub is None or fsub == sub):
                            return subfield["value"]

    def get_values(self, fname, reduce=True):
        field = self.get_field(fname)
        if isinstance(field, list):
            values = []
            for subfield in field:
                if "sequence" in subfield and \
                        "indicator1" in subfield and \
                        "indicator2" in subfield and \
                        "subfield" in subfield and \
                        "value" in subfield:
                    values.append(
                        {"seq": subfield["sequence"],
                         "ind1": subfield["indicator1"],
                         "ind2": subfield["indicator2"],
                         "sub": subfield["subfield"],
                         "val": subfield["value"]})
            if len(values) > 0:
                if reduce and len(values) == 1:
                    values = values[0]
                return values

    def get_cn(self):
        """
        00X       Control Fields-General Information

        001       Control Number (NR)

        No indicators and subfield codes.
        """
        return self.get_value("001")

    def get_date_entered(self):
        """
        00X       Control Fields-General Information

        008       Fixed-Length Data Elements-General Information
        /00-05    Date entered on file

        Field has no indicators or subfield codes; the data elements are positionally defined...
        """
        field = self.get_value("008")
        if isinstance(field, str):
            return field[:6]

    def get_date_entered_date(self):
        """
        00X       Control Fields-General Information

        008       Fixed-Length Data Elements-General Information
        /00-05    Date entered on file

        Field has no indicators or subfield codes; the data elements are positionally defined...
        """
        date_entered = self.get_date_entered()
        if isinstance(date_entered, str):
            try:
                return datetime.datetime.strptime(date_entered, "%y%m%d").date()
            except ValueError:
                pass

    def get_date_entered_iso(self):
        """
        00X       Control Fields-General Information

        008       Fixed-Length Data Elements-General Information
        /00-05    Date entered on file

        Field has no indicators or subfield codes; the data elements are positionally defined...
        """
        date_entered = self.get_date_entered_date()
        if date_entered is not None:
            return date_entered.isoformat()

    def get_latest_trans(self):
        """
        00X       Control Fields-General Information

        005       Date and Time of Latest Transaction

        This field has no indicators or subfield codes.
        """
        field = self.get_value("005")
        if isinstance(field, str):
            return field

    def get_latest_trans_datetime(self):
        """
        00X       Control Fields-General Information

        005       Date and Time of Latest Transaction

        This field has no indicators or subfield codes.
        """
        latest_trans = self.get_latest_trans()
        if isinstance(latest_trans, str):
            try:
                return datetime.datetime.strptime(latest_trans, "%Y%m%d%H%M%S.0")
            except ValueError:
                pass

    def get_latest_trans_iso(self):
        """
        00X       Control Fields-General Information

        005       Date and Time of Latest Transaction

        This field has no indicators or subfield codes.
        """
        latest_trans = self.get_latest_trans_datetime()
        if latest_trans is not None:
            return latest_trans.isoformat()
