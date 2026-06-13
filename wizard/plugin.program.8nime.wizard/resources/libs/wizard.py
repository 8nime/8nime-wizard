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
import zipfile

from resources.libs import check
from resources.libs import db
from resources.libs import extract
from resources.libs import install
from resources.libs import skin
from resources.libs.common import logging
from resources.libs.common import tools
from resources.libs.common.config import CONFIG
from resources.libs.downloader import Downloader


# Keep AniList Login: these per-addon settings hold the AniList session. The build
# install wipes userdata, losing them; with the setting on we read them before the
# wipe and write them back after extract so the user stays logged in (helper canonical).
PRESERVE_TOKENS = [
    ("plugin.video.8nime.bingie.helper", "anilist_token"),
    ("plugin.video.otaku", "anilist.token"),
]


def _addon_settings_path(addon_id):
    return os.path.join(CONFIG.USERDATA, "addon_data", addon_id, "settings.xml")


def _read_addon_setting(addon_id, key):
    path = _addon_settings_path(addon_id)
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    match = re.search(r'<setting id="%s"[^>]*>([^<]*)</setting>' % re.escape(key), text)
    return match.group(1).strip() if match else ""


def _write_addon_setting(addon_id, key, value):
    if not value:
        return False
    path = _addon_settings_path(addon_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    else:
        text = '<settings version="2">\n</settings>\n'
    esc = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    setting = '<setting id="%s">%s</setting>' % (key, esc)
    pat = re.compile(r'<setting id="%s"[^>]*>.*?</setting>' % re.escape(key), re.DOTALL)
    if pat.search(text):
        text = pat.sub(setting, text, count=1)
    elif "</settings>" in text:
        text = text.replace("</settings>", "    %s\n</settings>" % setting, 1)
    else:
        text = '<settings version="2">\n    %s\n</settings>\n' % setting
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return True


def save_anilist_login():
    """Read the AniList tokens before a wipe (returns {(addon_id, key): value})."""
    if CONFIG.get_setting("keepanilistlogin") != "true":
        return {}
    saved = {}
    for addon_id, key in PRESERVE_TOKENS:
        value = _read_addon_setting(addon_id, key)
        if value:
            saved[(addon_id, key)] = value
    if saved:
        logging.log("Keep AniList Login: saved token for %d addon(s)" % len(saved))
    return saved


def restore_anilist_login(saved):
    """Write the saved AniList tokens back after a build extract."""
    if not saved:
        return
    restored = 0
    for (addon_id, key), value in saved.items():
        if _write_addon_setting(addon_id, key, value):
            restored += 1
    logging.log("Keep AniList Login: restored token into %d addon(s)" % restored)


class Wizard:

    def __init__(self):
        tools.ensure_folders(CONFIG.PACKAGES)
        
        self.dialog = xbmcgui.Dialog()
        self.dialogProgress = xbmcgui.DialogProgress()

    def _prompt_for_wipe(self):
        # Should we wipe first?
        if self.dialog.yesno(CONFIG.ADDONTITLE,
                           "[COLOR {0}]Do you wish to restore your".format(CONFIG.COLOR2),
                           "Kodi configuration to default settings",
                           "Before installing the build backup?[/COLOR]",
                           nolabel='[B][COLOR red]No[/COLOR][/B]',
                           yeslabel='[B][COLOR springgreen]Yes[/COLOR][/B]'):
            install.wipe()

    def build(self, name, over=False):
        temp_kodiv = int(CONFIG.KODIV)
        buildv = int(float(check.check_build(name, 'kodi')))

        if not temp_kodiv == buildv:
            warning = True
        else:
            warning = False

        if warning:
            yes_pressed = self.dialog.yesno("{0} - [COLOR red]WARNING!![/COLOR]".format(CONFIG.ADDONTITLE),
                                       '[COLOR {0}]There is a chance that the skin will not appear correctly'.format(
                                           CONFIG.COLOR2),
                                       'When installing a {0} build on a Kodi {1} install'.format(
                                           check.check_build(name, 'kodi'), CONFIG.KODIV),
                                       'Would you still like to install: [COLOR {0}]{1} v{2}[/COLOR]?[/COLOR]'.format(
                                           CONFIG.COLOR1, name, check.check_build(name, 'version')),
                                       nolabel='[B][COLOR red]No, Cancel[/COLOR][/B]',
                                       yeslabel='[B][COLOR springgreen]Yes, Install[/COLOR][/B]')
        else:
            if over:
                yes_pressed = 1
            else:
                yes_pressed = self.dialog.yesno(CONFIG.ADDONTITLE,
                                           '[COLOR {0}]Would you like to Download and Install:'.format(
                                               CONFIG.COLOR2),
                                           '[COLOR {0}]{1} v{2}[/COLOR]?[/COLOR]'.format(CONFIG.COLOR1, name,
                                                                                         check.check_build(name,
                                                                                                           'version')),
                                           nolabel='[B][COLOR red]No, Cancel[/COLOR][/B]',
                                           yeslabel='[B][COLOR springgreen]Yes, Install[/COLOR][/B]')
        if yes_pressed:
            CONFIG.clear_setting('build')
            buildzip = check.check_build(name, 'url')
            zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')

            self.dialogProgress.create(CONFIG.ADDONTITLE, '[COLOR {0}][B]Downloading:[/B][/COLOR] [COLOR {1}]{2} v{3}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name, check.check_build(name, 'version')), '', 'Please Wait')

            lib = os.path.join(CONFIG.MYBUILDS, '{0}.zip'.format(zipname))
            
            try:
                os.remove(lib)
            except:
                pass

            Downloader().download(buildzip, lib)
            xbmc.sleep(500)
            
            if os.path.getsize(lib) == 0:
                try:
                    os.remove(lib)
                except:
                    pass
                    
                return
                
            saved_login = save_anilist_login()

            install.wipe()

            skin.look_and_feel_data('save')

            title = '[COLOR {0}][B]Installing:[/B][/COLOR] [COLOR {1}]{2} v{3}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name, check.check_build(name, 'version'))
            self.dialogProgress.update(0, title, '', 'Please Wait')
            percent, errors, error = extract.all(lib, CONFIG.HOME, title=title)

            restore_anilist_login(saved_login)
            
            skin.skin_to_default('Build Install')

            if int(float(percent)) > 0:
                db.fix_metas()
                CONFIG.set_setting('buildname', name)
                CONFIG.set_setting('buildversion', check.check_build(name, 'version'))
                CONFIG.set_setting('buildtheme', '')
                CONFIG.set_setting('latestversion', check.check_build(name, 'version'))
                CONFIG.set_setting('nextbuildcheck', tools.get_date(days=CONFIG.UPDATECHECK, formatted=True))
                CONFIG.set_setting('installed', 'true')
                CONFIG.set_setting('extract', percent)
                CONFIG.set_setting('errors', errors)
                logging.log('INSTALLED {0}: [ERRORS:{1}]'.format(percent, errors))

                try:
                    os.remove(lib)
                except:
                    pass

                if int(float(errors)) > 0:
                    yes_pressed = self.dialog.yesno(CONFIG.ADDONTITLE,
                                       '[COLOR {0}][COLOR {1}]{2} v{3}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1,
                                                                                       name, check.check_build(name, 'version')),
                                       'Completed: [COLOR {0}]{1}{2}[/COLOR] [Errors:[COLOR {3}]{4}[/COLOR]]'.format(
                                           CONFIG.COLOR1, percent, '%', CONFIG.COLOR1, errors),
                                       'Would you like to view the errors?[/COLOR]',
                                       nolabel='[B][COLOR red]No Thanks[/COLOR][/B]',
                                       yeslabel='[B][COLOR springgreen]View Errors[/COLOR][/B]')
                    if yes_pressed:
                        from resources.libs.gui import window
                        window.show_text_box("Viewing Build Install Errors", error)
                self.dialogProgress.close()

                from resources.libs.gui.build_menu import BuildMenu
                themecount = BuildMenu().theme_count(name)

                if themecount > 0:
                    self.theme(name)

                db.addon_database(CONFIG.ADDON_ID, 1)
                db.force_check_updates(over=True)

                self.dialog.ok(CONFIG.ADDONTITLE, "[COLOR {0}]To save changes you now need to force close Kodi, Press OK to force close Kodi[/COLOR]".format(CONFIG.COLOR2))
                tools.kill_kodi(over=True)
            else:
                from resources.libs.gui import window
                window.show_text_box("Viewing Build Install Errors", error)
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]Build Install: Cancelled![/COLOR]'.format(CONFIG.COLOR2))

    def gui(self, name, over=False):
        if name == CONFIG.get_setting('buildname'):
            if over:
                yes_pressed = 1
            else:
                yes_pressed = self.dialog.yesno(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]Would you like to apply the guifix for:'.format(CONFIG.COLOR2),
                                   '[COLOR {0}]{1}[/COLOR]?[/COLOR]'.format(CONFIG.COLOR1, name),
                                   nolabel='[B][COLOR red]No, Cancel[/COLOR][/B]',
                                   yeslabel='[B][COLOR springgreen]Apply Fix[/COLOR][/B]')
        else:
            yes_pressed = self.dialog.yesno("{0} - [COLOR red]WARNING!![/COLOR]".format(CONFIG.ADDONTITLE),
                               "[COLOR {0}][COLOR {1}]{2}[/COLOR] community build is not currently installed.".format(
                                   CONFIG.COLOR2, CONFIG.COLOR1, name),
                               "Would you like to apply the guiFix anyways?.[/COLOR]",
                               nolabel='[B][COLOR red]No, Cancel[/COLOR][/B]',
                               yeslabel='[B][COLOR springgreen]Apply Fix[/COLOR][/B]')
        if yes_pressed:
            guizip = check.check_build(name, 'gui')
            zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')

            response = tools.open_url(guizip, check=True)
            if not response:
                logging.log_notify(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]GuiFix: Invalid Zip Url![/COLOR]'.format(CONFIG.COLOR2))
                return

            self.dialogProgress.create(CONFIG.ADDONTITLE, '[COLOR {0}][B]Downloading GuiFix:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name), '', 'Please Wait')

            lib = os.path.join(CONFIG.PACKAGES, '{0}_guisettings.zip'.format(zipname))
            
            try:
                os.remove(lib)
            except:
                pass

            Downloader().download(guizip, lib)
            xbmc.sleep(500)
            
            if os.path.getsize(lib) == 0:
                try:
                    os.remove(lib)
                except:
                    pass
                    
                return
            
            title = '[COLOR {0}][B]Installing:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, name)
            self.dialogProgress.update(0, title, '', 'Please Wait')
            extract.all(lib, CONFIG.USERDATA, title=title)
            self.dialogProgress.close()
            skin.skin_to_default('Build Install')
            skin.look_and_feel_data('save')
            installed = db.grab_addons(lib)
            db.addon_database(installed, 1, True)

            self.dialog.ok(CONFIG.ADDONTITLE, "[COLOR {0}]To save changes you now need to force close Kodi, Press OK to force close Kodi[/COLOR]".format(CONFIG.COLOR2))
            tools.kill_kodi(over=True)
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]GuiFix: Cancelled![/COLOR]'.format(CONFIG.COLOR2))

    def theme(self, name, theme='', over=False):
        installtheme = False

        if not theme:
            themefile = check.check_build(name, 'theme')

            response = tools.open_url(themefile, check=True)
            if response:
                from resources.libs.gui.build_menu import BuildMenu
                themes = BuildMenu().theme_count(name, False)
                if len(themes) > 0:
                    if self.dialog.yesno(CONFIG.ADDONTITLE,
                                    "[COLOR {0}]The Build [COLOR {1}]{2}[/COLOR] comes with [COLOR {3}]{4}[/COLOR] different themes".format(
                                        CONFIG.COLOR2, CONFIG.COLOR1, name, CONFIG.COLOR1, len(themes)),
                                    "Would you like to install one now?[/COLOR]",
                                    yeslabel="[B][COLOR springgreen]Install Theme[/COLOR][/B]",
                                    nolabel="[B][COLOR red]Cancel Themes[/COLOR][/B]"):
                        logging.log("Theme List: {0}".format(str(themes)))
                        ret = self.dialog.select(CONFIG.ADDONTITLE, themes)
                        logging.log("Theme install selected: {0}".format(ret))
                        if not ret == -1:
                            theme = themes[ret]
                            installtheme = True
                        else:
                            logging.log_notify(CONFIG.ADDONTITLE,
                                               '[COLOR {0}]Theme Install: Cancelled![/COLOR]'.format(CONFIG.COLOR2))
                            return
                    else:
                        logging.log_notify(CONFIG.ADDONTITLE,
                                           '[COLOR {0}]Theme Install: Cancelled![/COLOR]'.format(CONFIG.COLOR2))
                        return
            else:
                logging.log_notify(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]Theme Install: None Found![/COLOR]'.format(CONFIG.COLOR2))
        else:
            installtheme = self.dialog.yesno(CONFIG.ADDONTITLE,
                                        '[COLOR {0}]Would you like to install the theme:'.format(CONFIG.COLOR2),
                                        '[COLOR {0}]{1}[/COLOR]'.format(CONFIG.COLOR1, theme),
                                        'for [COLOR {0}]{1} v{2}[/COLOR]?[/COLOR]'.format(CONFIG.COLOR1, name,
                                                                                          check.check_build(name,
                                                                                                            'version')),
                                        yeslabel="[B][COLOR springgreen]Install Theme[/COLOR][/B]",
                                        nolabel="[B][COLOR red]Cancel Themes[/COLOR][/B]")
                                        
        if installtheme:
            themezip = check.check_theme(name, theme, 'url')
            zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')

            response = tools.open_url(themezip, check=True)
            if not response:
                logging.log_notify(CONFIG.ADDONTITLE,
                                   '[COLOR {0}]Theme Install: Invalid Zip Url![/COLOR]'.format(CONFIG.COLOR2))
                return False

            self.dialogProgress.create(CONFIG.ADDONTITLE, '[COLOR {0}][B]Downloading:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2, CONFIG.COLOR1, theme), '', 'Please Wait')

            lib = os.path.join(CONFIG.PACKAGES, '{0}.zip'.format(zipname))
            
            try:
                os.remove(lib)
            except:
                pass

            Downloader().download(themezip, lib)
            xbmc.sleep(500)
            
            if os.path.getsize(lib) == 0:
                try:
                    os.remove(lib)
                except:
                    pass
                    
                return
            
            self.dialogProgress.update(0, "", "Installing {0}".format(name))

            test1 = False
            test2 = False

            from resources.libs import skin
            if CONFIG.SKIN not in skin.DEFAULT_SKINS:
                zfile = zipfile.ZipFile(lib, allowZip64=True)
                names = [item.filename for item in zfile.infolist()]
                test1 = any('/settings.xml' in n for n in names)
                test2 = any('/guisettings.xml' in n for n in names)

            if test1:
                skin.look_and_feel_data('save')
                swap = skin.skin_to_default('Theme Install')

                if not swap:
                    return False

                xbmc.sleep(500)

            title = '[COLOR {0}][B]Installing Theme:[/B][/COLOR] [COLOR {1}]{2}[/COLOR]'.format(CONFIG.COLOR2,
                                                                                                CONFIG.COLOR1,
                                                                                                theme)
            self.dialogProgress.update(0, title, '', 'Please Wait')
            percent, errors, error = extract.all(lib, CONFIG.HOME, title=title)
            CONFIG.set_setting('buildtheme', theme)
            logging.log('INSTALLED {0}: [ERRORS:{1}]'.format(percent, errors))
            self.dialogProgress.close()

            db.force_check_updates(over=True)
            installed = db.grab_addons(lib)
            db.addon_database(installed, 1, True)

            if test2:
                skin.look_and_feel_data('save')
                skin.skin_to_default("Theme Install")
                gotoskin = CONFIG.get_setting('defaultskin')
                skin.switch_to_skin(gotoskin, "Theme Installer")
                skin.look_and_feel_data('restore')
            elif test1:
                skin.look_and_feel_data('save')
                skin.skin_to_default("Theme Install")
                gotoskin = CONFIG.get_setting('defaultskin')
                skin.switch_to_skin(gotoskin, "Theme Installer")
                skin.look_and_feel_data('restore')
            else:
                xbmc.executebuiltin("ReloadSkin()")
                xbmc.sleep(1000)
                xbmc.executebuiltin("Container.Refresh()")
        else:
            logging.log_notify(CONFIG.ADDONTITLE,
                               '[COLOR {0}]Theme Install: Cancelled![/COLOR]'.format(CONFIG.COLOR2))


def wizard(action, name, url):
    cls = Wizard()

    if action in ['fresh', 'normal']:
        cls.build(action, name)
    elif action == 'gui':
        cls.gui(name)
    elif action == 'theme':
        cls.theme(name, url)
