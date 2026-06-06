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
ADDONTITLE = '[COLOR red][B]8nime[/B][/COLOR] Wizard'
BUILDERNAME = '8nime'
EXCLUDES = [ADDON_ID, 'repository.8nime']

# Hosted text files — served raw from the 8nime-repo (raw.githubusercontent,
# NOT GitHub Pages: Pages gzips + Kodi HTTP/2 stalls; these are fetched with
# requests so raw is simplest and consistent with the repo index).
BASE_URL = 'https://raw.githubusercontent.com/8nime/8nime-repo/main/hosted'

BUILDFILE = BASE_URL + '/builds.txt'
UPDATECHECK = 1
ADDONFILE = BASE_URL + '/addons-anime.json'
#########################################################

#########################################################
# Theming Menu Items                                    #
#########################################################
COLOR1 = 'red'
COLOR2 = 'white'
THEME1 = u'[COLOR {color1}][B]8nime[/B][/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
THEME2 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR1)
THEME3 = u'[COLOR {color1}]{{}}[/COLOR]'.format(color1=COLOR1)
THEME4 = u'[COLOR {color1}]Current Build:[/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
THEME5 = u'[COLOR {color1}]Current Theme:[/COLOR] [COLOR {color2}]{{}}[/COLOR]'.format(color1=COLOR1, color2=COLOR2)
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
HEADERMESSAGE = '[COLOR red][B]8nime[/B][/COLOR]'
HEADERIMAGE = 'http://'
FONTSETTINGS = 'Font13'
BACKGROUND = 'http://'
#########################################################
