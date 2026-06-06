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

import os
import re

try:  # Python 3
    from urllib.parse import quote_plus
except ImportError:  # Python 3
    from urllib import quote_plus

from resources.libs.common import logging
from resources.libs.common import tools
from resources.libs.common.config import CONFIG


ACTION_PREVIOUS_MENU = 10  # ESC action
ACTION_NAV_BACK = 92  # Backspace action
ACTION_MOVE_LEFT = 1  # Left arrow key
ACTION_MOVE_RIGHT = 2  # Right arrow key
ACTION_MOVE_UP = 3  # Up arrow key
ACTION_MOVE_DOWN = 4  # Down arrow key
ACTION_MOUSE_WHEEL_UP = 104	 # Mouse wheel up
ACTION_MOUSE_WHEEL_DOWN = 105  # Mouse wheel down
ACTION_MOVE_MOUSE = 107  # Down arrow key
ACTION_SELECT_ITEM = 7  # Number Pad Enter
ACTION_BACKSPACE = 110  # ?
ACTION_MOUSE_LEFT_CLICK = 100
ACTION_MOUSE_LONG_CLICK = 108

BACK_ACTIONS = [ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, ACTION_BACKSPACE]


def highlight_text(msg):
    msg = msg.replace('\n', '[NL]')
    matches = re.compile("-->Python callback/script returned the following error<--(.+?)-->End of Python script error report<--").findall(msg)
    for item in matches:
        string = '-->Python callback/script returned the following error<--{0}-->End of Python script error report<--'.format(item)
        msg = msg.replace(string, '[COLOR red]{0}[/COLOR]'.format(string))
    msg = msg.replace('WARNING', '[COLOR yellow]WARNING[/COLOR]').replace('ERROR', '[COLOR red]ERROR[/COLOR]').replace('[NL]', '\n').replace(': EXCEPTION Thrown (PythonToCppException) :', '[COLOR red]: EXCEPTION Thrown (PythonToCppException) :[/COLOR]')
    msg = msg.replace('\\\\', '\\').replace(CONFIG.HOME, '')
    return msg


def get_artwork(file):
    if file == 'button':
        return os.path.join(CONFIG.SKIN, 'Button', 'button-focus_lightblue.png'),\
               os.path.join(CONFIG.SKIN, 'Button', 'button-focus_grey.png')
    elif file == 'radio' :
        return os.path.join(CONFIG.SKIN, 'RadioButton', 'MenuItemFO.png'),\
               os.path.join(CONFIG.SKIN, 'RadioButton', 'MenuItemNF.png'),\
               os.path.join(CONFIG.SKIN, 'RadioButton', 'radiobutton-focus.png'),\
               os.path.join(CONFIG.SKIN, 'RadioButton', 'radiobutton-nofocus.png')
    elif file == 'slider':
        return os.path.join(CONFIG.SKIN, 'Slider', 'osd_slider_nib.png'),\
               os.path.join(CONFIG.SKIN, 'Slider', 'osd_slider_nibNF.png'),\
               os.path.join(CONFIG.SKIN, 'Slider', 'slider1.png'),\
               os.path.join(CONFIG.SKIN, 'Slider', 'slider1.png')


def while_window(window, active=False, count=0, counter=15):
    windowopen = xbmc.getCondVisibility('Window.IsActive({0})'.format(window))
    logging.log("{0} is {1}".format(window, windowopen))
    while not windowopen and count < counter:
        logging.log("{0} is {1}({2})".format(window, windowopen, count))
        windowopen = xbmc.getCondVisibility('Window.IsActive({0})'.format(window))
        count += 1
        xbmc.sleep(500)

    while windowopen:
        active = True
        logging.log("{0} is {1}".format(window, windowopen))
        windowopen = xbmc.getCondVisibility('Window.IsActive({0})'.format(window))
        xbmc.sleep(250)
        
    return active


def show_text_box(title, msg):
    class TextBox(xbmcgui.WindowXMLDialog):
        def onInit(self):
            self.title = 101
            self.msg = 102
            self.scrollbar = 103
            self.closebutton = 201
            
            self.setProperty('texture.color1', CONFIG.COLOR1)
            self.setProperty('texture.color2', CONFIG.COLOR2)
            self.setProperty('message.title', title)
            self.setProperty('message.msg', msg)

        def onClick(self, controlid):
            if controlid == self.closebutton:
                self.close()

        def onAction(self, action):
            if action.getId() in BACK_ACTIONS:
                self.close()

    tb = TextBox("text_box.xml", CONFIG.ADDON_PATH, 'Default', title=title, msg=msg)
    tb.doModal()
    del tb


def show_save_data_settings():
    class FirstRun(xbmcgui.WindowXMLDialog):

        def __init__(self, *args, **kwargs):
            self.whitelistcurrent = kwargs['current']

        def onInit(self):
            self.title = 101
            self.okbutton = 201
            self.trakt = 301
            self.debrid = 302
            self.login = 303
            self.sources = 304
            self.profiles = 305
            self.playercore = 314
            self.guisettings = 315
            self.advanced = 306
            self.favourites = 307
            self.superfav = 308
            self.repo = 309
            self.whitelist = 310
            self.cache = 311
            self.packages = 312
            self.thumbs = 313
            self.show_dialog()
            self.controllist = [self.trakt, self.login,
                                    self.sources, self.profiles, self.playercore, self.guisettings, self.advanced,
                                    self.favourites, self.superfav, self.repo,
                                    self.whitelist, self.cache, self.packages,
                                    self.thumbs]
            self.controlsettings = ['keeptrakt', 'keeplogin',
                                    'keepsources', 'keepprofiles', 'keepplayercore', 'keepguisettings', 'keepadvanced',
                                    'keepfavourites', 'keeprepos', 'keepsuper',
                                    'keepwhitelist', 'clearcache', 'clearpackages',
                                    'clearthumbs']
            for item in self.controllist:
                if CONFIG.get_setting(self.controlsettings[self.controllist.index(item)]) == 'true':
                    self.getControl(item).setSelected(True)

        def show_dialog(self):
            self.getControl(self.title).setLabel(CONFIG.ADDONTITLE)
            self.setFocus(self.getControl(self.okbutton))

        def onClick(self, controlid):
            if controlid == self.okbutton:

                for item in self.controllist:
                    at = self.controllist.index(item)
                    if self.getControl(item).isSelected():
                        CONFIG.set_setting(self.controlsettings[at], 'true')
                    else:
                        CONFIG.set_setting(self.controlsettings[at], 'false')

                self.close()

        def onAction(self, action):
            if action.getId() in BACK_ACTIONS:
                self.close()

    fr = FirstRun("FirstRunSaveData.xml", CONFIG.ADDON_PATH, 'Default', current=CONFIG.KEEPWHITELIST)
    fr.doModal()
    CONFIG.set_setting('first_install', 'false')
    del fr


def show_build_prompt():
    class BuildPrompt(xbmcgui.WindowXMLDialog):

        def __init__(self, *args, **kwargs):
            self.title = CONFIG.THEME3.format(CONFIG.ADDONTITLE)
            self.msg = "Currently no build installed from {0}.\n\nSelect 'Build Menu' to install a Community Build from us or 'Ignore' to never see this message again.\n\nThank you for choosing {1}.".format(CONFIG.ADDONTITLE, CONFIG.ADDONTITLE)
            self.msg = CONFIG.THEME2.format(self.msg)

        def onInit(self):
            self.image = 101
            self.titlebox = 102
            self.textbox = 103
            self.buildmenu = 201
            self.ignore = 202
            self.show_dialog()

        def show_dialog(self):
            self.getControl(self.image).setImage(CONFIG.ADDON_ICON)
            self.getControl(self.image).setColorDiffuse('9FFFFFFF')
            self.getControl(self.textbox).setText(self.msg)
            self.getControl(self.titlebox).setLabel(self.title)
            self.setFocusId(self.buildmenu)

        def do_build_menu(self):
            logging.log("[Current Build Check] [User Selected: Open Build Menu] [Next Check: {0}]".format(CONFIG.BUILDCHECK),
                        level=xbmc.LOGINFO)
            CONFIG.set_setting('nextbuildcheck', tools.get_date(days=CONFIG.UPDATECHECK, formatted=True))
            CONFIG.set_setting('installed', 'ignored')
            
            url = 'plugin://{0}/?mode=builds'.format(CONFIG.ADDON_ID)
            
            self.close()
            
            xbmc.executebuiltin('ActivateWindow(Programs, {0}, return)'.format(url))

        def do_ignore(self):
            logging.log("[Current Build Check] [User Selected: Ignore Build Menu] [Next Check: {0}]".format(CONFIG.BUILDCHECK),
                        level=xbmc.LOGINFO)
            CONFIG.set_setting('nextbuildcheck', tools.get_date(days=CONFIG.UPDATECHECK, formatted=True))
            CONFIG.set_setting('installed', 'ignored')
            
            self.close()

        def onAction(self, action):
            if action.getId() in BACK_ACTIONS:
                self.do_ignore()

        def onClick(self, controlid):
            if controlid == self.buildmenu:
                self.do_build_menu()
            elif controlid == self.ignore:
                self.do_ignore()

    fr = BuildPrompt("FirstRunBuild.xml", CONFIG.ADDON_PATH, 'Default')
    fr.doModal()
    del fr


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
    class Notification(xbmcgui.WindowXMLDialog):

        def __init__(self, *args, **kwargs):
            self.test = kwargs['test']
            self.msg = kwargs['msg']

        def onInit(self):
            self.image = 101
            self.titlebox = 102
            self.titleimage = 103
            self.textbox = 104
            self.scroller = 105
            self.dismiss = 201
            self.remindme = 202
            self.show_dialog()

        def show_dialog(self):
            self.testimage = os.path.join(CONFIG.ART, 'text.png')
            self.getControl(self.image).setImage(CONFIG.BACKGROUND)
            self.getControl(self.image).setColorDiffuse('9FFFFFFF')
            msg_text = CONFIG.THEME2.format(self.msg)
            self.getControl(self.textbox).setText(msg_text)
            self.setFocusId(self.remindme)
            if CONFIG.HEADERTYPE == 'Text':
                self.getControl(self.titlebox).setLabel(CONFIG.THEME3.format(CONFIG.HEADERMESSAGE))
            else:
                self.getControl(self.titleimage).setImage(CONFIG.HEADERIMAGE)

        def do_remind(self):
            if not test:
                CONFIG.set_setting('notedismiss', 'false')
            logging.log('[Notifications] Notification {0} Remind Me Later'.format(CONFIG.get_setting('noteid')))
            self.close()

        def do_dismiss(self):
            if not test:
                CONFIG.set_setting('notedismiss', 'true')
            logging.log('[Notifications] Notification {0} Dismissed'.format(CONFIG.get_setting('noteid')))
            self.close()

        def onAction(self, action):
            if action.getId() in BACK_ACTIONS:
                self.do_remind()

        def onClick(self, controlid):
            if controlid == self.dismiss:
                self.do_dismiss()
            elif controlid == self.remindme:
                self.do_remind()

    xbmc.executebuiltin('Skin.SetString(headertexttype, {0})'.format('true' if CONFIG.HEADERTYPE == 'Text' else 'false'))
    xbmc.executebuiltin('Skin.SetString(headerimagetype, {0})'.format('true' if CONFIG.HEADERTYPE == 'Image' else 'false'))
    notify = Notification("Notifications.xml", CONFIG.ADDON_PATH, 'Default', msg=msg, test=test)
    notify.doModal()
    del notify


def show_log_viewer(window_title="Viewing Log File", window_msg=None, log_file=None, ext_buttons=False):
    class LogViewer(xbmcgui.WindowXMLDialog):
        def __init__(self, *args, **kwargs):
            self.log_file = kwargs['log_file']

        def onInit(self):
            self.title = 101
            self.msg = 102
            self.scrollbar = 103
            self.upload = 201
            self.kodilog = 202
            self.oldlog = 203
            self.wizardlog = 204
            self.closebutton = 205

            if window_msg is None:
                self.logmsg = tools.read_from_file(self.log_file)
            else:
                self.logmsg = window_msg
            self.logfile = os.path.basename(self.log_file)
            
            self.buttons = 'true' if ext_buttons else 'false'
            
            self.setProperty('texture.color1', CONFIG.COLOR1)
            self.setProperty('texture.color2', CONFIG.COLOR2)
            self.setProperty('message.title', window_title)
            self.setProperty('message.logmsg', highlight_text(self.logmsg))
            self.setProperty('message.logfile', self.logfile)
            self.setProperty('message.buttons', self.buttons)

        def onClick(self, controlId):
            if controlId == self.closebutton:
                self.close()
            elif controlId == self.upload:
                self.close()
                logging.upload_log()
            elif controlId in [self.kodilog, self.oldlog, self.wizardlog]:
                if controlId == self.kodilog:
                    newmsg = logging.grab_log()
                    filename = logging.grab_log(file=True)
                elif controlId == self.oldlog:
                    newmsg = logging.grab_log(old=True)
                    filename = logging.grab_log(file=True, old=True)
                elif controlId == self.wizardlog:
                    newmsg = logging.grab_log(wizard=True)
                    filename = logging.grab_log(file=True, wizard=True)
                
                if not newmsg:
                    self.setProperty('message.title', "Error Viewing Log File")
                    self.setProperty('message.logmsg', "File does not exist or could not be read.")
                else:
                    self.logmsg = newmsg
                    self.logfile = os.path.basename(filename)
                
                    self.setProperty('message.logmsg', highlight_text(self.logmsg))
                    self.setProperty('message.logfile', self.logfile)

        def onAction(self, action):
            if action.getId() in BACK_ACTIONS:
                self.close()

    if log_file is None:
        log_file = logging.grab_log(file=True)
        
    lv = LogViewer("log_viewer.xml", CONFIG.ADDON_PATH, 'Default', log_file=log_file)
    lv.doModal()
    del lv
