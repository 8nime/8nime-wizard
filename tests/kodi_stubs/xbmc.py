# -*- coding: utf-8 -*-
"""Minimal xbmc stub for running wizard code outside Kodi."""

LOGDEBUG = 0
LOGINFO = 1
LOGWARNING = 2
LOGERROR = 3
LOGFATAL = 4


def log(msg, level=LOGINFO):
    pass


def sleep(ms):
    import time
    time.sleep(ms / 1000.0)


def translatePath(path):
    return path


def getCondVisibility(condition):
    return False


def executebuiltin(cmd):
    pass


def getInfoLabel(label):
    if label == "System.BuildVersion":
        return "19.4 Git:20210226-0000000000"
    if label.startswith("System.Memory"):
        return "4096MB"
    return ""


class Keyboard:
    def __init__(self, default="", heading="", hidden=False):
        self._default = default

    def doModal(self):
        pass

    def isConfirmed(self):
        return False

    def getText(self):
        return self._default
