# -*- coding: utf-8 -*-
"""Minimal xbmcvfs stub for running wizard code outside Kodi."""
import os


def translatePath(path):
    if path.startswith("special://profile/"):
        return os.path.join("/tmp/kodi-profile", path[len("special://profile/"):])
    if path.startswith("special://home/"):
        return os.path.join("/tmp/kodi-home", path[len("special://home/"):])
    if path.startswith("special://temp/"):
        return os.path.join("/tmp/kodi-temp", path[len("special://temp/"):])
    return path


def exists(path):
    return os.path.exists(path)


def mkdirs(path):
    os.makedirs(path, exist_ok=True)
    return True


def File(path, mode="r"):
    return open(path, mode)
