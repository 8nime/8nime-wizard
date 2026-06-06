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

from resources.libs.common import directory
from resources.libs.common.config import CONFIG


class MainMenu:

    def get_listing(self):
        # Current Build — the remote update check must NEVER be able to hide the
        # rest of the menu. A slow/failed builds.txt fetch used to raise out of
        # get_listing before Builds/Maintenance were added, leaving a half-built
        # menu. Show the installed build immediately, then check for updates
        # defensively.
        if len(CONFIG.BUILDNAME) > 0:
            build = '{0} (v{1})'.format(CONFIG.BUILDNAME, CONFIG.BUILDVERSION)
            try:
                from resources.libs import check
                version = check.check_build(CONFIG.BUILDNAME, 'version')
                if version and version > CONFIG.BUILDVERSION:
                    build = '{0} [COLOR red][B][UPDATE v{1}][/B][/COLOR]'.format(build, version)
            except Exception:
                pass  # offline / timeout — just show the current build name
            directory.add_dir(build, {'mode': 'viewbuild', 'name': CONFIG.BUILDNAME}, themeit=CONFIG.THEME4)
        else:
            directory.add_dir('None', {'mode': 'builds'}, themeit=CONFIG.THEME4)

        # Builds + Maintenance tools — always rendered, never gated on the network
        directory.add_dir('Builds', {'mode': 'builds'}, themeit=CONFIG.THEME1)
        directory.add_dir('Maintenance', {'mode': 'maint'}, themeit=CONFIG.THEME1)
