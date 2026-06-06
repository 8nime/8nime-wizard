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

# All wizard prompts use native Kodi dialogs (xbmcgui.Dialog) — no custom
# WindowXMLDialog skins. The addon ships no skin of its own.

import xbmc
import xbmcgui

import re

from resources.libs.common import logging
from resources.libs.common import tools
from resources.libs.common.config import CONFIG


def highlight_text(msg):
    msg = msg.replace('\n', '[NL]')
    matches = re.compile("-->Python callback/script returned the following error<--(.+?)-->End of Python script error report<--").findall(msg)
    for item in matches:
        string = '-->Python callback/script returned the following error<--{0}-->End of Python script error report<--'.format(item)
        msg = msg.replace(string, '[COLOR red]{0}[/COLOR]'.format(string))
    msg = msg.replace('WARNING', '[COLOR yellow]WARNING[/COLOR]').replace('ERROR', '[COLOR red]ERROR[/COLOR]').replace('[NL]', '\n').replace(': EXCEPTION Thrown (PythonToCppException) :', '[COLOR red]: EXCEPTION Thrown (PythonToCppException) :[/COLOR]')
    msg = msg.replace('\\\\', '\\').replace(CONFIG.HOME, '')
    return msg


def show_text_box(title, msg):
    xbmcgui.Dialog().textviewer(title, msg)


def show_save_data_settings():
    """First-run prompt: what to preserve when a build is installed.

    Native multi-select instead of a custom skinned window. Each entry maps
    straight to the keep*/clear* settings the build installer reads.
    """
    options = [
        ('Keep Trakt Data', 'keeptrakt'),
        ('Keep Login Info', 'keeplogin'),
        ('Keep Sources', 'keepsources'),
        ('Keep Profiles', 'keepprofiles'),
        ('Keep playercorefactory.xml', 'keepplayercore'),
        ('Keep guisettings.xml', 'keepguisettings'),
        ('Keep AdvancedSettings.xml', 'keepadvanced'),
        ('Keep Favourites', 'keepfavourites'),
        ('Keep Super Favourites', 'keepsuper'),
        ('Keep Installed Repositories', 'keeprepos'),
        ('Keep My Whitelist Addons', 'keepwhitelist'),
        ('Clear Cache on Install', 'clearcache'),
        ('Clear Packages on Install', 'clearpackages'),
        ('Clear Thumbnails on Install', 'clearthumbs'),
    ]
    labels = [label for label, _ in options]
    preselect = [i for i, (_, sid) in enumerate(options) if CONFIG.get_setting(sid) == 'true']

    selected = xbmcgui.Dialog().multiselect(
        '{0} - Data to keep when installing a build'.format(CONFIG.ADDONTITLE),
        labels, preselect=preselect)

    if selected is not None:
        for i, (_, sid) in enumerate(options):
            CONFIG.set_setting(sid, 'true' if i in selected else 'false')

    CONFIG.set_setting('first_install', 'false')


def show_build_prompt():
    msg = ("Currently no build is installed from {0}.\n\n"
           "Select 'Build Menu' to install a build, or 'Ignore' to stop seeing "
           "this message.").format(CONFIG.ADDONTITLE)

    open_menu = xbmcgui.Dialog().yesno(CONFIG.ADDONTITLE, msg,
                                       yeslabel='Build Menu', nolabel='Ignore')

    logging.log("[Current Build Check] [User Selected: {0}]".format(
        'Open Build Menu' if open_menu else 'Ignore'), level=xbmc.LOGINFO)
    CONFIG.set_setting('nextbuildcheck', tools.get_date(days=CONFIG.UPDATECHECK, formatted=True))
    CONFIG.set_setting('installed', 'ignored')

    if open_menu:
        url = 'plugin://{0}/?mode=builds'.format(CONFIG.ADDON_ID)
        xbmc.executebuiltin('ActivateWindow(Programs, {0}, return)'.format(url))


def show_update_window(name='Testing Window', current='1.0', new='1.1'):
    msgcurrent = 'Running latest version of installed build: '
    msgupdate = 'Update available for installed build: '
    build_name = '[COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, name)
    current_version = 'Current Version: v[COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, current)
    latest_version = 'Latest Version: v[COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, new)

    final_msg = '{0}{1}\n{2}\n{3}\n'.format(msgcurrent if current >= new else msgupdate,
                                            build_name, current_version, latest_version)

    install = xbmcgui.Dialog().yesno(CONFIG.ADDONTITLE, final_msg,
                                     yeslabel='Install', nolabel='Ignore')
    if install:
        from resources.libs.wizard import Wizard
        Wizard().build(CONFIG.BUILDNAME)


def split_notify(notify):
    response = tools.open_url(notify)

    if response:
        link = response.text

        try:
            link = response.text.decode('utf-8')
        except:
            pass

        link = link.replace('\r', '').replace('\t', '    ').replace('\n', '[CR]')
        if link.find('|||') == -1:
            return False, False

        _id, msg = link.split('|||')
        _id = _id.replace('[CR]', '')
        if msg.startswith('[CR]'):
            msg = msg[4:]

        return _id, msg
    else:
        return False, False


def show_notification(msg, test=False):
    heading = CONFIG.HEADERMESSAGE if CONFIG.HEADERTYPE == 'Text' else CONFIG.ADDONTITLE
    text = msg.replace('[CR]', '\n')

    remind = xbmcgui.Dialog().yesno(heading, text,
                                    yeslabel='Remind Me Later', nolabel='Dismiss')

    if not test:
        # yes (remind) -> keep showing; no (dismiss) -> stop showing this note
        CONFIG.set_setting('notedismiss', 'false' if remind else 'true')
    logging.log('[Notifications] Notification {0} {1}'.format(
        CONFIG.get_setting('noteid'), 'Remind Me Later' if remind else 'Dismissed'))


def show_log_viewer(window_title="Viewing Log File", window_msg=None, log_file=None, ext_buttons=False):
    # ext_buttons (upload / switch log) dropped with the custom window — those
    # actions live under Maintenance -> Logging Tools.
    if window_msg is not None:
        text = window_msg
    else:
        if log_file is None:
            log_file = logging.grab_log(file=True)
        text = tools.read_from_file(log_file)

    xbmcgui.Dialog().textviewer(window_title, highlight_text(text or ''), usemono=True)
