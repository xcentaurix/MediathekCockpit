# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Plugins.Plugin import PluginDescriptor
from .ConfigInit import ConfigInit
from .SkinUtils import loadPluginSkin
from .Debug import logger
from .Version import VERSION
from .MediathekCockpit import MediathekCockpit
from .PluginUtils import WHERE_MEDIATHEK_SEARCH
from . import _


def main(session, query="", **__kwargs):
    logger.info("...")
    session.open(MediathekCockpit, query)


def showDownloads(session, event="", service="", **_kwargs):
    logger.info("...")
    if not service:
        service = session.nav.getCurrentService()
    info = service.info()
    if not event:
        event = info.getEvent(0)  # 0 = now, 1 = next
    event_name = event and event.getEventName() or info.getName() or ""
    logger.info("event_name: %s", event_name)
    session.open(MediathekCockpit, event_name)


def autoStart(reason, **kwargs):
    if reason == 0:  # startup
        if "session" in kwargs:
            logger.info("+++ Version: %s starts...", VERSION)
            loadPluginSkin("skin.xml")
    elif reason == 1:  # shutdown
        logger.info("--- shutdown")


def Plugins(**__kwargs):
    ConfigInit()
    return [
        PluginDescriptor(
            where=[
                PluginDescriptor.WHERE_AUTOSTART,
                PluginDescriptor.WHERE_SESSIONSTART
            ],
            fnc=autoStart
        ),
        PluginDescriptor(
            name="MediathekCockpit",
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon="MediathekCockpit.png",
            description=_("Browse Mediathek libraries"),
            fnc=main
        ),
        PluginDescriptor(
            name=_("Mediathek Downloads"),
            description=_("Mediathek Downloads"),
            where=[
                PluginDescriptor.WHERE_EVENTINFO
            ],
            fnc=showDownloads
        ),
        PluginDescriptor(
            name=_("MediathekCockpit"),
            description=_("Mediathek Downloads"),
            where=WHERE_MEDIATHEK_SEARCH,
            fnc=main
        ),
    ]
