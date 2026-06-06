import xbmcaddon

import os

#########################################################
# Global Variables - DON'T EDIT!!!                      #
#########################################################
ADDON_ID = xbmcaddon.Addon().getAddonInfo('id')
PATH = xbmcaddon.Addon().getAddonInfo('path')
ART = os.path.join(PATH, 'resources', 'media')
#########################################################

#########################################################
# User Edit Variables                                   #
#########################################################
ADDONTITLE = '[COLOR deeppink][B]8nime[/B][/COLOR]Wizard'
BUILDERNAME = '8nime'
EXCLUDES = [ADDON_ID, 'repository.8nime']

# Hosted text files — replace BASE_URL when publishing to GitHub Pages
BASE_URL = 'https://8nime.github.io/kodi-build/hosted'

BUILDFILE = BASE_URL + '/builds.txt'
UPDATECHECK = 1
APKFILE = 'http://'
YOUTUBETITLE = 'Anime Guides'
YOUTUBEFILE = BASE_URL + '/youtube.txt'
ADDONFILE = BASE_URL + '/addons.json'
ADVANCEDFILE = BASE_URL + '/advanced.json'
#########################################################

#########################################################
# Theming Menu Items                                    #
#########################################################
ICONBUILDS = os.path.join(ART, 'builds.png')
ICONMAINT = os.path.join(ART, 'maintenance.png')
ICONSPEED = os.path.join(ART, 'speed.png')
ICONAPK = os.path.join(ART, 'apkinstaller.png')
ICONADDONS = os.path.join(ART, 'addoninstaller.png')
ICONYOUTUBE = os.path.join(ART, 'youtube.png')
ICONSAVE = os.path.join(ART, 'savedata.png')
ICONTRAKT = os.path.join(ART, 'keeptrakt.png')
ICONLOGIN = os.path.join(ART, 'keeplogin.png')
ICONCONTACT = os.path.join(ART, 'information.png')
ICONSETTINGS = os.path.join(ART, 'settings.png')

HIDESPACERS = 'No'
SPACER = '='

COLOR1 = 'deeppink'
COLOR2 = 'white'
THEME1 = u'[COLOR {color1}][B]8nime[/B][/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
THEME2 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR1)
THEME3 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR1)
THEME4 = u'[COLOR {color1}]Current Build:[/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
THEME5 = u'[COLOR {color1}]Current Theme:[/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)

HIDECONTACT = 'No'
CONTACT = '8nime — a Kodi build for anime movies and series.\n\nSkin: Bingie (Netflix-style UI)\nAddons: Otaku, WatchNixtoons2, Fanime F\n\nConfigure Trakt after install for watchlist sync.'
CONTACTICON = os.path.join(ART, 'qricon.png')
CONTACTFANART = 'http://'
#########################################################

#########################################################
# Auto Update For Those With No Repo                    #
#########################################################
AUTOUPDATE = 'Yes'
#########################################################

#########################################################
# Auto Install Repo If Not Installed                    #
#########################################################
AUTOINSTALL = 'Yes'
REPOID = 'repository.8nime'
REPOADDONXML = BASE_URL + '/addons.xml'
REPOZIPURL = BASE_URL + '/zips/repository.8nime/'
#########################################################

#########################################################
# Notification Window                                   #
#########################################################
ENABLE = 'Yes'
NOTIFICATION = BASE_URL + '/notify.txt'
HEADERTYPE = 'Text'
FONTHEADER = 'Font14'
HEADERMESSAGE = '[COLOR deeppink][B]8nime[/B][/COLOR]'
HEADERIMAGE = 'http://'
FONTSETTINGS = 'Font13'
BACKGROUND = 'http://'
#########################################################
