# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config
from Screens.ChoiceBox import ChoiceBox
from .ConfigScreen import ConfigScreen
from .About import about
from .Debug import logger
from .PluginUtils import WHERE_JOBCOCKPIT, getPlugin
from .Version import ID
from .__init__ import _


class Menu():
    def __init__(self):
        self.menu = [
            (_("Download Manager"), self.showDownloadManager),
            (_("Settings"), self.showSettings),
            (_("About"), self.showAbout)
        ]

    def openMenu(self):
        self.session.openWithCallback(
            self.openMenuCallback,
            ChoiceBox,
            title=_("Functions"),
            list=self.menu,
            titlebartext="MediathekCockpit" + " - " + _("Menu")
        )

    def openMenuCallback(self, selection):
        logger.info("...")
        if selection:
            selection[1]()

    def showDownloadManager(self):
        logger.info("...")
        plugin = getPlugin(WHERE_JOBCOCKPIT)
        if plugin:
            logger.debug("plugin.name: %s", plugin.name)
            plugin(self.session, ID)

    def showSettings(self):
        logger.info("...")
        self.session.openWithCallback(
            self.showSettingsCallback, ConfigScreen, config.plugins.mediathekcockpit)

    def showSettingsCallback(self, changed=None):
        logger.info("...")
        if changed:
            self.postdata["size"] = int(
                config.plugins.mediathekcockpit.size.value)
            self.postdata["future"] = config.plugins.mediathekcockpit.future.value
            self.postdata["offset"] = 0

    def showAbout(self):
        logger.info("...")
        about(self.session)
