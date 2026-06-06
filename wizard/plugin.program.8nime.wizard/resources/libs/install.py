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
import xbmcaddon
import xbmcgui
import xbmcvfs

import glob
import os
import re
import shutil

from resources.libs.common.config import CONFIG

###########################
#      Fresh Install      #
###########################


def wipe():
    from resources.libs import db
    from resources.libs.common import logging
    from resources.libs import skin
    from resources.libs.common import tools
    from resources.libs import update

    exclude_dirs = CONFIG.EXCLUDES
    exclude_dirs.append('My_Builds')
    
    progress_dialog = xbmcgui.DialogProgress()
    
    skin.skin_to_default('Fresh Install')
    
    update.addon_updates('set')
    xbmcPath = os.path.abspath(CONFIG.HOME)
    progress_dialog.create(CONFIG.ADDONTITLE,
                  "[COLOR {0}]Calculating files and folders".format(CONFIG.COLOR2), '', 'Please Wait![/COLOR]')
    total_files = sum([len(files) for r, d, files in os.walk(xbmcPath)])
    del_file = 0
    progress_dialog.update(0, "[COLOR {0}]Gathering Excludes list.[/COLOR]".format(CONFIG.COLOR2))
    if CONFIG.KEEPREPOS == 'true':
        repos = glob.glob(os.path.join(CONFIG.ADDONS, 'repo*/'))
        for item in repos:
            repofolder = os.path.split(item[:-1])[1]
            if not repofolder == exclude_dirs:
                exclude_dirs.append(repofolder)
    if CONFIG.KEEPSUPER == 'true':
        exclude_dirs.append('plugin.program.super.favourites')
    for item in CONFIG.DEPENDENCIES:
        exclude_dirs.append(item)

    progress_dialog.update(0, "[COLOR {0}]Clearing out files and folders:".format(CONFIG.COLOR2))
    latestAddonDB = db.latest_db('Addons')
    for root, dirs, files in os.walk(xbmcPath, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for name in files:
            del_file += 1
            fold = root.replace('/', '\\').split('\\')
            x = len(fold)-1
            if name == 'sources.xml' and fold[-1] == 'userdata' and CONFIG.KEEPSOURCES == 'true':
                logging.log("Keep sources.xml: {0}".format(os.path.join(root, name)))
            elif name == 'favourites.xml' and fold[-1] == 'userdata' and CONFIG.KEEPFAVS == 'true':
                logging.log("Keep favourites.xml: {0}".format(os.path.join(root, name)))
            elif name == 'profiles.xml' and fold[-1] == 'userdata' and CONFIG.KEEPPROFILES == 'true':
                logging.log("Keep profiles.xml: {0}".format(os.path.join(root, name)))
            elif name == 'playercorefactory.xml' and fold[-1] == 'userdata' and CONFIG.KEEPPLAYERCORE == 'true':
                logging.log("Keep playercorefactory.xml: {0}".format(os.path.join(root, name)))
            elif name == 'guisettings.xml' and fold[-1] == 'userdata' and CONFIG.KEEPGUISETTINGS == 'true':
                logging.log("Keep guisettings.xml: {0}".format(os.path.join(root, name)))
            elif name == 'advancedsettings.xml' and fold[-1] == 'userdata' and CONFIG.KEEPADVANCED == 'true':
                logging.log("Keep advancedsettings.xml: {0}".format(os.path.join(root, name)))
            elif name in CONFIG.LOGFILES:
                logging.log("Keep Log File: {0}".format(name))
            elif name.endswith('.db'):
                try:
                    if name == latestAddonDB:
                        logging.log("Ignoring {0} on Kodi {1}".format(name, tools.kodi_version()))
                    else:
                        os.remove(os.path.join(root, name))
                except Exception as e:
                    if not name.startswith('Textures13'):
                        logging.log('Failed to delete, Purging DB')
                        logging.log("-> {0}".format(str(e)))
                        db.purge_db_file(os.path.join(root, name))
            else:
                progress_dialog.update(int(tools.percentage(del_file, total_files)), '',
                              '[COLOR {0}]File: [/COLOR][COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name), '')
                try:
                    os.remove(os.path.join(root, name))
                except Exception as e:
                    logging.log("Error removing {0}".format(os.path.join(root, name)))
                    logging.log("-> / {0}".format(str(e)))
        if progress_dialog.iscanceled():
            progress_dialog.close()
            logging.log_notify(CONFIG.ADDONTITLE,
                               "[COLOR {0}]Fresh Start Cancelled[/COLOR]".format(CONFIG.COLOR2))
            return False
    for root, dirs, files in os.walk(xbmcPath, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for name in dirs:
            progress_dialog.update(100, '',
                          'Cleaning Up Empty Folder: [COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, name), '')
            if name not in ["Database", "userdata", "temp", "addons", "addon_data"]:
                shutil.rmtree(os.path.join(root, name), ignore_errors=True, onerror=None)
        if progress_dialog.iscanceled():
            progress_dialog.close()
            logging.log_notify(CONFIG.ADDONTITLE,
                               "[COLOR {0}]Fresh Start Cancelled[/COLOR]".format(CONFIG.COLOR2))
            return False
            
    progress_dialog.close()
    CONFIG.clear_setting('build')


def fresh_start(install=None, over=False):
    from resources.libs.common import logging
    from resources.libs.common import tools

    dialog = xbmcgui.Dialog()

    if over:
        yes_pressed = 1

    elif install == 'restore':
        yes_pressed = dialog.yesno(CONFIG.ADDONTITLE,
                                       "[COLOR {0}]Do you wish to restore your".format(CONFIG.COLOR2),
                                       "Kodi configuration to default settings",
                                       "Before installing the local backup?[/COLOR]",
                                       nolabel='[B][COLOR red]No, Cancel[/COLOR][/B]',
                                       yeslabel='[B][COLOR springgreen]Continue[/COLOR][/B]')
    elif install:
        yes_pressed = dialog.yesno(CONFIG.ADDONTITLE, "[COLOR {0}]Do you wish to restore your".format(CONFIG.COLOR2),
                                       "Kodi configuration to default settings",
                                       "Before installing [COLOR {0}]{1}[/COLOR]?".format(CONFIG.COLOR1, install),
                                       nolabel='[B][COLOR red]No, Cancel[/COLOR][/B]',
                                       yeslabel='[B][COLOR springgreen]Continue[/COLOR][/B]')
    else:
        yes_pressed = dialog.yesno(CONFIG.ADDONTITLE,
                                       "[COLOR {0}]Do you wish to restore your".format(CONFIG.COLOR2),
                                       "Kodi configuration to default settings?[/COLOR]",
                                       nolabel='[B][COLOR red]No, Cancel[/COLOR][/B]',
                                       yeslabel='[B][COLOR springgreen]Continue[/COLOR][/B]')
    if yes_pressed:
        wipe()
        
        if over:
            return True
        elif install == 'restore':
            return True
        elif install:
            from resources.libs.wizard import Wizard

            Wizard().build('normal', install, over=True)
        else:
            dialog.ok(CONFIG.ADDONTITLE, "[COLOR {0}]To save changes you now need to force close Kodi, Press OK to force close Kodi[/COLOR]".format(CONFIG.COLOR2))
            from resources.libs import update
            update.addon_updates('reset')
            tools.kill_kodi(over=True)
    else:
        if not install == 'restore':
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]Fresh Install: Cancelled![/COLOR]'.format(CONFIG.COLOR2))
            xbmc.executebuiltin('Container.Refresh()')
