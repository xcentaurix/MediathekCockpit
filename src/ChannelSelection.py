# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import json
from Screens.ChoiceBox import ChoiceBox
from .WebRequests import WebRequests
from .Debug import logger
from .__init__ import _


class ChannelSelection():
    def __init__(self):
        return

    def openChannelSelection(self):
        logger.info("...")
        url = "https://mediathekviewweb.de/api/channels"
        channel_list = json.loads(
            WebRequests().getContent(url)).get("channels", [])
        choices = [(_("All channels"),)]
        for channel in channel_list:
            choices.append((str(channel),))
        self.session.openWithCallback(
            self.openChannelSelectionCallback,
            ChoiceBox,
            title=_("Channel selection"),
            list=choices,
            titlebartext="MediathekCockpit" + " - " + _("Channel selection"),
            keys=[]
        )

    def openChannelSelectionCallback(self, selection):
        logger.info("selection: %s", selection)
        if selection:
            channel = selection[0]
            if channel == _("All channels"):
                if "queries" in self.postdata:
                    del self.postdata["queries"]
                channel = None
            else:
                self.postdata["queries"] = [
                    {"fields": ["channel"], "query": channel}]
            self.postdata["offset"] = 0
            self.downloadMovieList(channel)
