# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0 (see LICENSE file for details)


from twisted.internet import reactor


def callLater(delay, function, *args, **kwargs):
    return reactor.callLater(delay, function, *args, **kwargs)
