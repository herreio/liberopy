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

    def get_value(self, fname, find=None):
        field = self.get_field(fname)
        if isinstance(field, list):
            for subfield in field:
                if "indicator" in subfield and \
                        "value" in subfield:
                    if find is None:
                        return {"ind": subfield["indicator"],
                                "val": subfield["value"]}
                    ind = subfield["indicator"]
                    if ind == find:
                        return subfield["value"]

    def get_values(self, fname, reduce=True):
        field = self.get_field(fname)
        if isinstance(field, list):
            values = []
            for subfield in field:
                if "indicator" in subfield and \
                        "value" in subfield:
                    values.append(
                        {"ind": subfield["indicator"],
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
        field = self.get_value("001")
        if isinstance(field, dict) and "val" in field:
            return field["val"]
