# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from .Debug import logger
from .__init__ import _
from .Constants import LIST_EVENT_NAME, LIST_SHORT_DESCRIPTION, LIST_DESCRIPTION, LIST_DATE, LIST_DURATION, LIST_CHANNEL, LIST_TIME


class EventView(Screen):

    def __init__(self, session, curr):
        logger.info("...")
        Screen.__init__(self, session)
        self.skinName = "EventView"
        self.setTitle(curr[LIST_EVENT_NAME])
        self["actions"] = ActionMap(
            ["MTC_Actions", "OkCancelActions", "ChannelSelectEPGActions"],
            {
                "red": self.close,
                "ok": self.close,
                "cancel": self.close,
                "showEPGList": self.close
            }
        )
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button()
        self["key_yellow"] = Button()
        self["key_blue"] = Button()
        epg_description = curr[LIST_EVENT_NAME]
        if curr[LIST_SHORT_DESCRIPTION]:
            epg_description += "\n\n" + curr[LIST_SHORT_DESCRIPTION]
        epg_description += "\n\n" + curr[LIST_DESCRIPTION]
        self["epg_description"] = ScrollLabel(epg_description)
        self["datetime"] = Label(curr[LIST_DATE] + " " + curr[LIST_TIME])
        self["duration"] = Label(
            str(curr[LIST_DURATION] / 60) + " " + _("min"))
        self["channel"] = Label(curr[LIST_CHANNEL])
