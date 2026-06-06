################################################################################
#      Copyright (C) 2019 drinfernoo                                           #
#                                                                              #
#  This Program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 2, or (at your option)         #
#  any later version.                                                          #
#                                                                              #
#  This Program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with XBMC; see the file COPYING.  If not, write to                    #
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.       #
#  http://www.gnu.org/copyleft/gpl.html                                        #
################################################################################

import xbmc
import xbmcgui
import xbmcplugin

import sys

try:  # Python 3
    from urllib.parse import quote_plus
except ImportError:  # Python 2
    from urllib import quote_plus

from resources.libs.common.config import CONFIG


def set_view():
    auto_view = CONFIG.get_setting('auto-view')

    if auto_view == 'true':
        view_type = CONFIG.get_setting('viewType')

        xbmc.executebuiltin("Container.SetViewMode({0})".format(view_type))


def add_file(display, params=None, menu=None, description=CONFIG.ADDONTITLE, overwrite=True,
             themeit=None, isFolder=False):

    # isFolder = False
    _add_menu_item(display, params, menu, description, overwrite, themeit, isFolder)


def add_dir(display, params=None, menu=None, description=CONFIG.ADDONTITLE, overwrite=True,
            themeit=None, isFolder=True):

    # isFolder = True
    _add_menu_item(display, params, menu, description, overwrite, themeit, isFolder)


def _add_menu_item(display, params, menu, description, overwrite, themeit, isFolder):
    # the plugin id, i.e. "plugin://plugin.program.openwizard/"
    u = sys.argv[0]

    if params is not None:
        u += "?{0}={1}".format('mode', quote_plus(params.get('mode', "")))
        
        for param in params:
            if param == 'mode':
                continue
                
            # build URI to send to router
            u += "&{0}={1}".format(param, quote_plus(params.get(param, "")))

    # format item label using themes from uservar
    if themeit is not None:
        display = themeit.format(display)

    # build list item — no icon/thumb art and no fanart background (stripped UI)
    liz = xbmcgui.ListItem(display)
    liz.setInfo(type="Video", infoLabels={"Title": display, "Plot": description})

    # build context menu
    # if menu is not None:
        # liz.addContextMenuItems(menu, replaceItems=overwrite)

    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolder)
    return ok
