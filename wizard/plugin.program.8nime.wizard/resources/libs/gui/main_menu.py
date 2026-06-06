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
        from resources.libs import check

        # Current Build
        if len(CONFIG.BUILDNAME) > 0:
            version = check.check_build(CONFIG.BUILDNAME, 'version')
            build = '{0} (v{1})'.format(CONFIG.BUILDNAME, CONFIG.BUILDVERSION)
            if version and version > CONFIG.BUILDVERSION:
                build = '{0} [COLOR red][B][UPDATE v{1}][/B][/COLOR]'.format(build, version)
            directory.add_dir(build, {'mode': 'viewbuild', 'name': CONFIG.BUILDNAME}, themeit=CONFIG.THEME4)
        else:
            directory.add_dir('None', {'mode': 'builds'}, themeit=CONFIG.THEME4)

        # Builds + Maintenance tools
        directory.add_dir('Builds', {'mode': 'builds'}, themeit=CONFIG.THEME1)
        directory.add_dir('Maintenance', {'mode': 'maint'}, themeit=CONFIG.THEME1)
