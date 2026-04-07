# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)

from enigma import eServiceCenter, eServiceReference
from Components.config import config
from .Debug import logger


def getServiceList(servicetypes):
    logger.info("servicetypes: %s", servicetypes)
    """
    Get list of services from given service type reference string.
    Returns list of tuples: [(service_ref_string, service_name), ...]
    """
    service_list = []
    try:
        ref = eServiceReference(servicetypes)
        serviceHandler = eServiceCenter.getInstance()
        services = serviceHandler.list(ref)
        if services:
            while True:
                service = services.getNext()
                if not service.valid():
                    break
                info = serviceHandler.info(service)
                if info:
                    service_name = info.getName(service)
                    service_ref = service.toString()
                    if service_name and service_ref:
                        service_list.append((service_ref, service_name))
    except Exception as e:
        logger.error("Error getting service list: %s", str(e))
    return service_list


def getTVBouquets():
    logger.info("...")
    """
    Get list of TV bouquets.
    Returns list of tuples: [(bouquet_ref_string, bouquet_name), ...]
    """
    bouquets = []
    try:
        serviceHandler = eServiceCenter.getInstance()
        bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
        bouquet_root = eServiceReference(bouquet_rootstr)

        if config.usage.multibouquet.value:
            bouquet_list = serviceHandler.list(bouquet_root)
            if bouquet_list:
                while True:
                    s = bouquet_list.getNext()
                    if not s.valid():
                        break
                    if s.flags & eServiceReference.isDirectory and not s.flags & eServiceReference.isInvisible:
                        info = serviceHandler.info(s)
                        if info:
                            bouquets.append((s.toString(), info.getName(s)))
        else:
            info = serviceHandler.info(bouquet_root)
            if info:
                bouquets.append((bouquet_root.toString(), info.getName(bouquet_root)))
    except Exception as e:
        logger.error("Error getting TV bouquets: %s", str(e))
    return bouquets
