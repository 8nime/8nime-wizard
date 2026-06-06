# -*- coding: utf-8 -*-
"""Minimal xbmcaddon stub for running wizard code outside Kodi."""


class Addon:
    def __init__(self, addon_id=None, id=None):
        self._id = addon_id or id or "plugin.program.8nime.wizard"
        self._settings = {}
        self._info = {
            "id": self._id,
            "path": "/tmp/fake-wizard-path",
            "name": "8nime Wizard",
            "version": "1.0.0",
            "icon": "/tmp/fake-wizard-path/icon.png",
            "fanart": "/tmp/fake-wizard-path/fanart.jpg",
        }

    def getSetting(self, key):
        return self._settings.get(key, "")

    def getSettingBool(self, key):
        return str(self._settings.get(key, "false")).lower() == "true"

    def setSetting(self, key, value):
        self._settings[key] = str(value)

    def getAddonInfo(self, key):
        return self._info.get(key, "")

    def openSettings(self):
        pass
