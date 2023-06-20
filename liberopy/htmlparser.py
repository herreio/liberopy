# -*- coding: utf-8 -*-
"""
Parser classes for HTML pages retrieved via Libero WebOpac
"""

import json
import lxml.html


class OpacResponse:

    def __init__(self, htmlstr, tagname=None):
        self.root = None
        self.htmlstr = htmlstr
        if isinstance(self.htmlstr, str):
            self.root = lxml.html.fromstring(self.htmlstr)

    def tree(self):
        if self.root is not None:
            return self.root.getroottree()


class NewItemsResponse(OpacResponse):

    def __init__(self, htmlstr, tagname=None):
        super().__init__(htmlstr, tagname=tagname)

    def results(self):
        tree = self.tree()
        if tree is not None:
            script = tree.xpath('//script[starts-with(.,"document.omnioSearchResults")]')
            if isinstance(script, list) and len(script) > 0:
                elem = script[0]
                plain = elem.text.replace("document.omnioSearchResults = ","").rstrip(";")
                return json.loads(plain)

    def results_number(self):
        results = self.results()
        if isinstance(results, dict) and "number" in results:
            return results["number"]

    def results_records(self):
        results = self.results()
        if isinstance(results, dict) and "results" in results:
            return results["results"]

    def results_paging(self):
        results = self.results()
        if isinstance(results, dict) and "paging" in results:
            return results["paging"]

    def results_paging_total(self):
        paging = self.results_paging()
        if isinstance(paging, dict) and "total" in paging:
            return paging["total"]

    def results_code_lists(self):
        results = self.results()
        if isinstance(results, dict) and "codeLists" in results:
            return results["codeLists"]

    def results_code_lists_gmds(self):
        code_lists = self.results_code_lists()
        if isinstance(code_lists, dict) and "gmds" in code_lists:
            return code_lists["gmds"]


class NewItemsGroupResponse(OpacResponse):

    def __init__(self, htmlstr, tagname=None):
        super().__init__(htmlstr, tagname=tagname)

    def get_links(self):
        if self.root is not None:
            return self.root.find_class("NIGLink")

    def parse_links(self):
        links = self.get_links()
        group_data = {}
        for link in links:
            if link.attrib:
                if "title" in link.attrib:
                    group_data[link.attrib["title"]] = None
                    if "href" in link.attrib:
                        group_data[link.attrib["title"]] = link.attrib["href"]
        return group_data


class NewItemsGroupDetailsResponse(OpacResponse):

    def __init__(self, htmlstr, tagname=None):
        super().__init__(htmlstr, tagname=tagname)

    def get_groups(self):
        if self.root is not None:
            return self.root.find_class("GroupCont")

    def parse_groups(self):
        groups = self.get_groups()
        group_data = {}
        for group in groups:
            if group.find_class("xRelLink"):
                link = group.find_class("xRelLink")
                if len(link) == 1:
                    group_title = link[0].text.rstrip(" (Titel)")
                    if "name" in link[0].attrib:
                        group_num = link[0].attrib["name"]
                        group_data[group_num] = {"id": group_num, "name": group_title, "hits": []}
                        if group.find_class("TitleLink"):
                            title_links = group.find_class("TitleLink")
                            for link in title_links:
                                if "title" in link.attrib:
                                    if "href" in link.attrib:
                                        group_data[group_num]["hits"].append(
                                            {
                                                "title": link.attrib["title"],
                                                "href": link.attrib["href"]}
                                            )
        return group_data
