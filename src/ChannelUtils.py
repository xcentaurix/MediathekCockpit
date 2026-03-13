# coding=utf-8
# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


import json
from Screens.ChannelSelection import service_types_tv
from .Debug import logger
from .FileUtils import readFile, writeFile
from .ChannelListUtils import getServiceList


def getServiceReference(name):
    logger.info("name: %s", name)
    data = readFile(
        "/usr/lib/enigma2/python/Plugins/Extensions/MediathekCockpit/channels/mtc_service_refs.json")
    service_refs = json.loads(data)
    channel = service_refs.get(name, {})
    service_ref = channel.get("service", "")
    logger.debug("service_ref: %s", service_ref)
    return service_ref


def getServiceDict(bouquet=""):
    if not bouquet:
        bouquet = service_types_tv
    # bouquet = "Alle Sender (Enigma)"
    service_types = bouquet + " " + "ORDER BY name"
    service_list = getServiceList(service_types)
    logger.debug("service_list: %s", service_list)
    if service_list:
        service_dict = {}
        for service, name in service_list:
            if "::" not in service:
                service_dict[name] = service
    # service_dict = convertUnicode2Str(service_dict)
    data = json.dumps(service_dict, indent=6)
    writeFile("/etc/enigma2/mtc_service_dict.json", data)
    return service_dict
