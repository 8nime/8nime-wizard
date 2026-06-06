# -*- coding: utf-8 -*-
"""
Insert Kodi stub modules into sys.modules before any addon code is imported.
This file is loaded automatically by pytest before test collection starts.
"""
import sys
import os

# Make the wizard plugin root importable so `uservar`, `resources.libs.*` work.
WIZARD_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "wizard",
    "plugin.program.8nime.wizard",
)
if WIZARD_ROOT not in sys.path:
    sys.path.insert(0, WIZARD_ROOT)

# Register each stub module under its Kodi name before any addon import runs.
from tests.kodi_stubs import xbmc as _xbmc
from tests.kodi_stubs import xbmcaddon as _xbmcaddon
from tests.kodi_stubs import xbmcgui as _xbmcgui
from tests.kodi_stubs import xbmcplugin as _xbmcplugin
from tests.kodi_stubs import xbmcvfs as _xbmcvfs

sys.modules.setdefault("xbmc", _xbmc)
sys.modules.setdefault("xbmcaddon", _xbmcaddon)
sys.modules.setdefault("xbmcgui", _xbmcgui)
sys.modules.setdefault("xbmcplugin", _xbmcplugin)
sys.modules.setdefault("xbmcvfs", _xbmcvfs)
