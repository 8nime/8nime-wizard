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

try:  # Python 3
    from urllib.parse import quote_plus
    from urllib.request import urlretrieve
except ImportError:  # Python 2
    from urllib import quote_plus
    from urllib import urlretrieve

from resources.libs.common import directory
from resources.libs.common.config import CONFIG


###########################
#      Menu Items         #
###########################

def system_info():
    from resources.libs.common import logging
    from resources.libs.common import tools

    infoLabel = ['System.FriendlyName', 'System.BuildVersion', 'System.CpuUsage', 'System.ScreenMode',
                 'Network.IPAddress', 'Network.MacAddress', 'System.Uptime', 'System.TotalUptime', 'System.FreeSpace',
                 'System.UsedSpace', 'System.TotalSpace', 'System.Memory(free)', 'System.Memory(used)',
                 'System.Memory(total)']
    data = []
    x = 0
    for info in infoLabel:
        temp = tools.get_info_label(info)
        y = 0
        while temp == "Busy" and y < 10:
            temp = tools.get_info_label(info)
            y += 1
            logging.log("{0} sleep {1}".format(info, str(y)))
            xbmc.sleep(200)
        data.append(temp)
        x += 1
    storage_free = data[8] if 'Una' in data[8] else tools.convert_size(int(float(data[8][:-8])) * 1024 * 1024)
    storage_used = data[9] if 'Una' in data[9] else tools.convert_size(int(float(data[9][:-8])) * 1024 * 1024)
    storage_total = data[10] if 'Una' in data[10] else tools.convert_size(int(float(data[10][:-8])) * 1024 * 1024)
    ram_free = tools.convert_size(int(float(data[11][:-2])) * 1024 * 1024)
    ram_used = tools.convert_size(int(float(data[12][:-2])) * 1024 * 1024)
    ram_total = tools.convert_size(int(float(data[13][:-2])) * 1024 * 1024)

    picture = []
    music = []
    video = []
    programs = []
    repos = []
    scripts = []
    skins = []

    fold = glob.glob(os.path.join(CONFIG.ADDONS, '*/'))
    for folder in sorted(fold, key = lambda x: x):
        foldername = os.path.split(folder[:-1])[1]
        if foldername == 'packages': continue
        xml = os.path.join(folder, 'addon.xml')
        if os.path.exists(xml):
            prov = re.compile("<provides>(.+?)</provides>").findall(tools.read_from_file(xml))
            if len(prov) == 0:
                if foldername.startswith('skin'):
                    skins.append(foldername)
                elif foldername.startswith('repo'):
                    repos.append(foldername)
                else:
                    scripts.append(foldername)
            elif not (prov[0]).find('executable') == -1:
                programs.append(foldername)
            elif not (prov[0]).find('video') == -1:
                video.append(foldername)
            elif not (prov[0]).find('audio') == -1:
                music.append(foldername)
            elif not (prov[0]).find('image') == -1:
                picture.append(foldername)

    directory.add_file('[B]Media Center Info:[/B]', themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Name:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[0]), themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]Version:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[1]), themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]Platform:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, tools.platform().title()), themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]CPU Usage:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[2]), themeit=CONFIG.THEME3)
    directory.add_file('[COLOR {0}]Screen Mode:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[3]), themeit=CONFIG.THEME3)

    directory.add_file('[B]Uptime:[/B]', themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Current Uptime:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[6]), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Total Uptime:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, data[7]), themeit=CONFIG.THEME2)

    directory.add_file('[B]Local Storage:[/B]', themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Used Storage:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, storage_used), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Free Storage:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, storage_free), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Total Storage:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, storage_total), themeit=CONFIG.THEME2)

    directory.add_file('[B]Ram Usage:[/B]', themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Used Memory:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ram_free), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Free Memory:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ram_used), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Total Memory:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, ram_total), themeit=CONFIG.THEME2)

    totalcount = len(picture) + len(music) + len(video) + len(programs) + len(scripts) + len(skins) + len(repos)
    directory.add_file('[B]Addons([COLOR {0}]{1}[/COLOR]):[/B]'.format(CONFIG.COLOR1, totalcount), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Video Addons:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(video))), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Program Addons:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(programs))), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Music Addons:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(music))), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Picture Addons:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(picture))), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Repositories:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(repos))), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Skins:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(skins))), themeit=CONFIG.THEME2)
    directory.add_file('[COLOR {0}]Scripts/Modules:[/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR1, CONFIG.COLOR2, str(len(scripts))), themeit=CONFIG.THEME2)


def enable_addons():
    from resources.libs.common import tools
    
    from xml.etree import ElementTree

    directory.add_file("[I][B][COLOR red]!!Notice: Disabling Some Addons Can Cause Issues!![/COLOR][/B][/I]")
    fold = glob.glob(os.path.join(CONFIG.ADDONS, '*/'))
    addonnames = []
    addonids = []
    for folder in sorted(fold, key=lambda x: x):
        foldername = os.path.split(folder[:-1])[1]
        if foldername in CONFIG.EXCLUDES:
            continue
        elif foldername in CONFIG.DEFAULTPLUGINS:
            continue
        elif foldername == 'packages':
            continue
        xml = os.path.join(folder, 'addon.xml')
        if os.path.exists(xml):
            root = ElementTree.parse(xml).getroot()
            addonid = root.get('id')
            addonname = root.get('name')
           
            try:
                addonnames.append(tools.get_addon_info(addonid, 'name'))
                addonids.append(addonid)
            except:                
                pass
                
            if xbmc.getCondVisibility('System.HasAddon({0})'.format(addonid)):
                state = "[COLOR springgreen][Enabled][/COLOR]"
                goto = "false"
            else:
                state = "[COLOR red][Disabled][/COLOR]"
                goto = "true"
                
            directory.add_file("{0} {1}".format(state, addonname), {'mode': 'toggleaddon', 'name': addonid, 'url': goto})
    if len(addonnames) == 0:
        directory.add_file("No Addons Found to Enable or Disable.")


def remove_addon_data_menu():
    if os.path.exists(CONFIG.ADDON_DATA):
        directory.add_file('[COLOR red][B][REMOVE][/B][/COLOR] All Addon_Data', {'mode': 'removedata', 'name': 'all'}, themeit=CONFIG.THEME2)
        directory.add_file('[COLOR red][B][REMOVE][/B][/COLOR] All Addon_Data for Uninstalled Addons', {'mode': 'removedata', 'name': 'uninstalled'}, themeit=CONFIG.THEME2)
        directory.add_file('[COLOR red][B][REMOVE][/B][/COLOR] All Empty Folders in Addon_Data', {'mode': 'removedata', 'name': 'empty'}, themeit=CONFIG.THEME2)
        directory.add_file('[COLOR red][B][REMOVE][/B][/COLOR] {0} Addon_Data'.format(CONFIG.ADDONTITLE), {'mode': 'resetaddon'}, themeit=CONFIG.THEME2)
        fold = glob.glob(os.path.join(CONFIG.ADDON_DATA, '*/'))
        for folder in sorted(fold, key = lambda x: x):
            foldername = folder.replace(CONFIG.ADDON_DATA, '').replace('\\', '').replace('/', '')
            folderdisplay = foldername
            replace = {'audio.': '[COLOR orange][AUDIO] [/COLOR]', 'metadata.': '[COLOR cyan][METADATA] [/COLOR]',
                       'module.': '[COLOR orange][MODULE] [/COLOR]', 'plugin.': '[COLOR blue][PLUGIN] [/COLOR]',
                       'program.': '[COLOR orange][PROGRAM] [/COLOR]', 'repository.': '[COLOR gold][REPO] [/COLOR]',
                       'script.': '[COLOR springgreen][SCRIPT] [/COLOR]',
                       'service.': '[COLOR springgreen][SERVICE] [/COLOR]', 'skin.': '[COLOR dodgerblue][SKIN] [/COLOR]',
                       'video.': '[COLOR orange][VIDEO] [/COLOR]', 'weather.': '[COLOR yellow][WEATHER] [/COLOR]'}
            for rep in replace:
                folderdisplay = folderdisplay.replace(rep, replace[rep])
            if foldername in CONFIG.EXCLUDES:
                folderdisplay = '[COLOR springgreen][B][PROTECTED][/B][/COLOR] {0}'.format(folderdisplay)
            else:
                folderdisplay = '[COLOR red][B][REMOVE][/B][/COLOR] {0}'.format(folderdisplay)
            directory.add_file(' {0}'.format(folderdisplay), {'mode': 'removedata', 'name': foldername}, themeit=CONFIG.THEME2)
    else:
        directory.add_file('No Addon data folder found.', themeit=CONFIG.THEME3)


def change_freq():
    from resources.libs.common import logging

    dialog = xbmcgui.Dialog()

    change = dialog.select("[COLOR {0}]How often would you list to Auto Clean on Startup?[/COLOR]".format(CONFIG.COLOR2), CONFIG.CLEANFREQ)
    if not change == -1:
        CONFIG.set_setting('autocleanfreq', str(change))
        logging.log_notify('[COLOR {0}]Auto Clean Up[/COLOR]'.format(CONFIG.COLOR1),
                           '[COLOR {0}]Frequency Now {1}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.CLEANFREQ[change]))


