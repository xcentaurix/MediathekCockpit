# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config
from Screens.VirtualKeyBoard import VirtualKeyBoard
from .Query import getSeriesEpisode
from .Debug import logger
from .__init__ import _


class Search():
    def __init__(self):
        self.postdata = {
            "sortOrder": "desc",
            "sortBy": "timestamp",
            "offset": 0,
            "size": config.plugins.mediathekcockpit.size.value,
            "future": config.plugins.mediathekcockpit.future.value
        }

    def openKeyboard(self, query):
        logger.info("query: %s", query)
        series_episode = getSeriesEpisode(query)
        if series_episode:
            query = query.replace(series_episode, "").strip()
        self.session.openWithCallback(self.openKeyboardCallback, VirtualKeyBoard, title=_(
            "Enter search text"), text=query)

    def openKeyboardCallback(self, result):
        logger.info("result: %s", result)
        if result is None:
            result = ""
        fields = ["topic", "title"]
        self.postdata["offset"] = 0
        self.postdata["future"] = config.plugins.mediathekcockpit.future.value
        self.postdata["queries"] = [{"fields": fields, "query": result}]
        self.downloadMovieList()
