# -*- coding: utf-8 -*-
"""Minimal xbmcgui stub for running wizard code outside Kodi."""


class Dialog:
    def ok(self, heading, *lines):
        pass

    def yesno(self, heading, *lines, **kwargs):
        return False

    def select(self, heading, options, **kwargs):
        return -1

    def browse(self, dialog_type, heading, shares, mask="", use_thumbs=False,
                treat_file_as_folder=False, default_path=""):
        return default_path

    def notification(self, heading, message, icon="", time=5000, sound=True):
        pass

    def textviewer(self, heading, text):
        pass

    def input(self, heading, default="", type=0, option=0, auto_close=0):
        return default


class DialogProgress:
    def create(self, heading, *lines):
        pass

    def update(self, percent, *lines):
        pass

    def close(self):
        pass

    def iscanceled(self):
        return False


class DialogProgressBG:
    def create(self, heading, message=""):
        pass

    def update(self, percent=0, heading="", message=""):
        pass

    def close(self):
        pass

    def isFinished(self):
        return True


class WindowXMLDialog:
    def __init__(self, *args, **kwargs):
        pass

    def doModal(self):
        pass

    def close(self):
        pass

    def setProperty(self, key, value):
        pass

    def getProperty(self, key):
        return ""

    def getControl(self, control_id):
        return _FakeControl()


class _FakeControl:
    def setLabel(self, label):
        pass

    def setImage(self, image):
        pass

    def setVisible(self, visible):
        pass
