# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.Sources.List import List
from .Query import Query
from .Debug import logger
from .__init__ import _


ROWS = 12


class MovieList(Query):
    def __init__(self, parent):
        self.parent = parent
        Query.__init__(self)
        self.parent["list"] = List()
        self.list = []
        self.index = 0
        self.total_results = 0
        self.page_size = 120
        self.page = 1
        self.pages = 0

    def getList(self, postdata, channel=None):
        logger.info("postdata: %s", postdata)
        self.postdata = postdata
        self.channel = channel
        self.page_size = postdata.get("size", 120)
        offset = postdata.get("offset", 0)
        if offset == 0:
            self.list = []
            self.index = 0
        alist, self.total_results = self.download(postdata, channel)
        self.list += alist
        logger.debug("list: %s", self.list)
        self.parent["list"].setList(self.list)
        self.parent["list"].index = self.index
        self.page = offset // self.page_size + 1
        self.pages = max(1, (self.total_results + self.page_size - 1) // self.page_size)
        self.updateTitle()

    def getCurrentSelection(self):
        if self.parent["list"].getCurrent() is not None:
            return self.parent["list"].getCurrent()
        return None

    def up(self):
        if self.index > 0:
            self.index -= 1
            self.parent["list"].index = self.index
        else:
            logger.warning("Already at the first item in the list.")
        self.updateTitle()

    def down(self):
        self.index += 1
        if self.index < len(self.list):
            self.parent["list"].index = self.index
        else:
            self.postdata["offset"] = len(self.list)
            self.getList(self.postdata, self.channel)
        self.updateTitle()

    def left(self):
        self.index = max(0, self.index - ROWS)
        self.parent["list"].index = self.index
        self.updateTitle()

    def right(self):
        self.index += ROWS
        if self.index < len(self.list):
            self.parent["list"].index = self.index
        else:
            self.postdata["offset"] = len(self.list)
            self.getList(self.postdata, self.channel)
        self.updateTitle()

    def pageUp(self):
        logger.info("page_size: %s, index: %s, list len: %s", self.page_size, self.index, len(self.list))
        self.index = max(0, self.index - self.page_size)
        self.parent["list"].index = self.index
        self.updateTitle()

    def pageDown(self):
        logger.info("page_size: %s, index: %s, list len: %s", self.page_size, self.index, len(self.list))
        self.index += self.page_size
        if self.index < len(self.list):
            self.parent["list"].index = self.index
        else:
            self.postdata["offset"] = len(self.list)
            self.getList(self.postdata, self.channel)
        self.updateTitle()

    def updateTitle(self):
        if self.list:
            self.parent.title = self.parent.title_base + " - " + _("Page") + ": " + f"{self.page}/{self.pages}"
        else:
            self.parent.title = self.parent.title_base + " - " + _("No movies available")
        logger.info("Updated title: %s", self.parent.title)
