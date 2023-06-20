# -*- coding: utf-8 -*-
"""
Client classes for the Libero Web Opac
"""

import logging
import requests
import datetime

from . import __version__, htmlparser


class WebOpac:

    def __init__(self, domain, db="ACM", loglevel=logging.DEBUG):
        self.domain = domain
        self.path = "{0}/WebOpac.cls".format(self.domain)
        self.db = db
        self.token = None
        self.logger = None
        self.DefaultPage = None
        self.NewItemsGroup = None
        self._logger(loglevel)
        self.DefaultPage = DefaultPage(self.path, self.db, loglevel=self.logger.level)
        self.NewItems = NewItems(self.path, self.db, loglevel=self.logger.level)
        self.NewItemsGroup = NewItemsGroup(self.path, self.db, loglevel=self.logger.level)
        self.NewItemsGroupDetails = NewItemsGroupDetails(self.path, self.db, loglevel=self.logger.level)

    def _logger(self, level):
        self.logger = logging.getLogger("liberopy.WebOpac")
        if not self.logger.handlers:
            stream = logging.StreamHandler()
            stream.setLevel(level)
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
            stream.setFormatter(formatter)
            self.logger.addHandler(stream)
            self.logger.setLevel(level)

    def default_page(self):
        return self.DefaultPage.fetch()

    def new_items(self):
        return self.NewItems.fetch()

    def new_items_group(self):
        return self.NewItemsGroup.fetch()

    def new_items_group_details(self):
        return self.NewItemsGroupDetails.fetch()


class OpacAction:

    def __init__(self, path, name, db, loglevel=logging.DEBUG):
        self.path = path
        self.name = name
        self.db = db
        self.logger = None
        self._logger(loglevel)

    def _logger(self, level):
        self.logger = logging.getLogger("liberopy.webopac.OpacAction.{0}".format(self.name))
        if not self.logger.handlers:
            stream = logging.StreamHandler()
            stream.setLevel(level)
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
            stream.setFormatter(formatter)
            self.logger.addHandler(stream)
            self.logger.setLevel(level)

    def get_request(self, url):
        try:
            response = requests.get(url, headers={"User-Agent": "liberopy {0}".format(__version__)})
        except requests.exceptions.RequestException as e:
            self.logger.error(e.__class__.__name__)
            return None
        if response.status_code != 200:
            self.logger.error("HTTP request to {0} failed!".format(url))
            self.logger.error("HTTP {0}".format(response.status_code))
            return None
        return response

    def html_request(self, url, post=htmlparser.OpacResponse):
        response = self.get_request(url)
        if response and response.text:
            return post(response.text)

    @staticmethod
    def set_param(url, name, value):
        return "{0}?{1}={2}".format(url, name, value)

    @staticmethod
    def add_param(url, name, value):
        return "{0}&{1}={2}".format(url, name, value)

    def action_path(self, action):
        return self.set_param(self.path, "ACTION", action)

    def add_data_to_url(self, url, data):
        return self.add_param(url, "DATA", data)

    def url(self):
        url = self.action_path(self.name)
        return self.add_data_to_url(url, self.db)

    def fetch(self):
        url = self.url()
        return self.html_request(url)


class DefaultPage(OpacAction):

    def __init__(self, path, db, loglevel=logging.DEBUG):
        super().__init__(path, "DEFAULTPAGE", db, loglevel=loglevel)


class NewItems(OpacAction):

    def __init__(self, path, db, loglevel=logging.DEBUG):
        super().__init__(path, "NEWITEMS", db, loglevel=loglevel)

    def fetch(self):
        url = self.url()
        return self.html_request(url, post=htmlparser.NewItemsResponse)


class NewItemsGroup(OpacAction):

    def __init__(self, path, db, loglevel=logging.DEBUG):
        super().__init__(path, "NEWITEMSGROUP", db, loglevel=loglevel)

    def fetch(self):
        url = self.url()
        return self.html_request(url, post=htmlparser.NewItemsGroupResponse)


class NewItemsGroupDetails(OpacAction):

    def __init__(self, path, db, loglevel=logging.DEBUG):
        super().__init__(path, "NEWITEMSGROUPDETAILS", db, loglevel=loglevel)

    def fetch(self, group="001", month=str(datetime.date.today().month)):
        url = self.url()
        url = self.add_group_to_url(url, group)
        url = self.add_month_to_url(url, month)
        return self.html_request(url, post=htmlparser.NewItemsGroupDetailsResponse)

    def add_month_to_url(self, url, month):
        return self.add_param(url, "MONTH", month)

    def add_group_to_url(self, url, group):
        return self.add_param(url, "GROUP", group)
