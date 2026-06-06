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

import os

from resources.libs.common import directory
from resources.libs.common import logging
from resources.libs.common import tools
from resources.libs.common.config import CONFIG


class MaintenanceMenu:

    def get_listing(self):
        directory.add_dir('[B]Cleaning Tools[/B]', {'mode': 'maint', 'name': 'clean'}, themeit=CONFIG.THEME1)
        directory.add_dir('[B]Addon Tools[/B]', {'mode': 'maint', 'name': 'addon'}, themeit=CONFIG.THEME1)
        directory.add_dir('[B]Logging Tools[/B]', {'mode': 'maint', 'name': 'logging'}, themeit=CONFIG.THEME1)
        directory.add_dir('[B]System Tweaks/Fixes[/B]', {'mode': 'maint', 'name': 'tweaks'}, themeit=CONFIG.THEME1)

    def clean_menu(self):
        from resources.libs import clear
        from resources.libs.common import tools

        on = '[B][COLOR springgreen]ON[/COLOR][/B]'
        off = '[B][COLOR red]OFF[/COLOR][/B]'

        autoclean = 'true' if CONFIG.AUTOCLEANUP == 'true' else 'false'
        cache = 'true' if CONFIG.AUTOCACHE == 'true' else 'false'
        packages = 'true' if CONFIG.AUTOPACKAGES == 'true' else 'false'
        thumbs = 'true' if CONFIG.AUTOTHUMBS == 'true' else 'false'
        includevid = 'true' if CONFIG.INCLUDEVIDEO == 'true' else 'false'
        includeall = 'true' if CONFIG.INCLUDEALL == 'true' else 'false'

        sizepack = tools.get_size(CONFIG.PACKAGES)
        sizethumb = tools.get_size(CONFIG.THUMBNAILS)
        archive = tools.get_size(CONFIG.ARCHIVE_CACHE)
        sizecache = (clear.get_cache_size()) - archive
        totalsize = sizepack + sizethumb + sizecache

        directory.add_file(
            'Total Clean Up: [COLOR springgreen][B]{0}[/B][/COLOR]'.format(tools.convert_size(totalsize)), {'mode': 'fullclean'},
            themeit=CONFIG.THEME3)
        directory.add_file('Clear Cache: [COLOR springgreen][B]{0}[/B][/COLOR]'.format(tools.convert_size(sizecache)),
                           {'mode': 'clearcache'}, themeit=CONFIG.THEME3)
        if xbmc.getCondVisibility('System.HasAddon(script.module.urlresolver)') or xbmc.getCondVisibility(
                'System.HasAddon(script.module.resolveurl)'):
            directory.add_file('Clear Resolver Function Caches', {'mode': 'clearfunctioncache'},
                               themeit=CONFIG.THEME3)
        directory.add_file('Clear Packages: [COLOR springgreen][B]{0}[/B][/COLOR]'.format(tools.convert_size(sizepack)),
                           {'mode': 'clearpackages'}, themeit=CONFIG.THEME3)
        directory.add_file(
            'Clear Thumbnails: [COLOR springgreen][B]{0}[/B][/COLOR]'.format(tools.convert_size(sizethumb)),
            {'mode': 'clearthumb'}, themeit=CONFIG.THEME3)
        if os.path.exists(CONFIG.ARCHIVE_CACHE):
            directory.add_file('Clear Archive_Cache: [COLOR springgreen][B]{0}[/B][/COLOR]'.format(
                tools.convert_size(archive)), {'mode': 'cleararchive'}, themeit=CONFIG.THEME3)
        directory.add_file('Clear Old Thumbnails', {'mode': 'oldThumbs'}, themeit=CONFIG.THEME3)
        directory.add_file('Clear Crash Logs', {'mode': 'clearcrash'}, themeit=CONFIG.THEME3)
        directory.add_file('Purge Databases', {'mode': 'purgedb'}, themeit=CONFIG.THEME3)
        directory.add_file('Fresh Start', {'mode': 'freshstart'}, themeit=CONFIG.THEME3)

        directory.add_file('Auto Clean', themeit=CONFIG.THEME1)
        directory.add_file('Auto Clean Up On Startup: {0}'.format(autoclean.replace('true', on).replace('false', off)),
                           {'mode': 'togglesetting', 'name': 'autoclean'}, themeit=CONFIG.THEME3)
        if autoclean == 'true':
            directory.add_file(
                '--- Auto Clean Frequency: [B][COLOR springgreen]{0}[/COLOR][/B]'.format(
                    CONFIG.CLEANFREQ[CONFIG.AUTOFREQ]),
                {'mode': 'changefreq'}, themeit=CONFIG.THEME3)
            directory.add_file(
                '--- Clear Cache on Startup: {0}'.format(cache.replace('true', on).replace('false', off)),
                {'mode': 'togglesetting', 'name': 'clearcache'}, themeit=CONFIG.THEME3)
            directory.add_file(
                '--- Clear Packages on Startup: {0}'.format(packages.replace('true', on).replace('false', off)),
                {'mode': 'togglesetting', 'name': 'clearpackages'}, themeit=CONFIG.THEME3)
            directory.add_file(
                '--- Clear Old Thumbs on Startup: {0}'.format(thumbs.replace('true', on).replace('false', off)),
                {'mode': 'togglesetting', 'name': 'clearthumbs'}, themeit=CONFIG.THEME3)
        directory.add_file('Clear Video Cache',
                           themeit=CONFIG.THEME1)
        directory.add_file(
            'Include Video Cache in Clear Cache: {0}'.format(includevid.replace('true', on).replace('false', off)),
            {'mode': 'togglecache', 'name': 'includevideo'}, themeit=CONFIG.THEME3)

        if includeall == 'true':
            includegaia = 'true'
            includeexodusredux = 'true'
            includethecrew = 'true'
            includeyoda = 'true'
            includevenom = 'true'
            includenumbers = 'true'
            includescrubs = 'true'
        else:
            includeexodusredux = 'true' if CONFIG.INCLUDEEXODUSREDUX == 'true' else 'false'
            includegaia = 'true' if CONFIG.INCLUDEGAIA == 'true' else 'false'
            includethecrew = 'true' if CONFIG.INCLUDETHECREW == 'true' else 'false'
            includeyoda = 'true' if CONFIG.INCLUDEYODA == 'true' else 'false'
            includevenom = 'true' if CONFIG.INCLUDEVENOM == 'true' else 'false'
            includenumbers = 'true' if CONFIG.INCLUDENUMBERS == 'true' else 'false'
            includescrubs = 'true' if CONFIG.INCLUDESCRUBS == 'true' else 'false'

        if includevid == 'true':
            directory.add_file(
                '--- Include All Video Addons: {0}'.format(includeall.replace('true', on).replace('false', off)),
                {'mode': 'togglecache', 'name': 'includeall'}, themeit=CONFIG.THEME3)
            if xbmc.getCondVisibility('System.HasAddon(plugin.video.exodusredux)'):
                directory.add_file(
                    '--- Include Exodus Redux: {0}'.format(
                        includeexodusredux.replace('true', on).replace('false', off)),
                    {'mode': 'togglecache', 'name': 'includeexodusredux'}, themeit=CONFIG.THEME3)
            if xbmc.getCondVisibility('System.HasAddon(plugin.video.gaia)'):
                directory.add_file(
                    '--- Include Gaia: {0}'.format(includegaia.replace('true', on).replace('false', off)),
                    {'mode': 'togglecache', 'name': 'includegaia'}, themeit=CONFIG.THEME3)
            if xbmc.getCondVisibility('System.HasAddon(plugin.video.numbersbynumbers)'):
                directory.add_file(
                    '--- Include NuMb3r5: {0}'.format(includenumbers.replace('true', on).replace('false', off)),
                    {'mode': 'togglecache', 'name': 'includenumbers'}, themeit=CONFIG.THEME3)
            if xbmc.getCondVisibility('System.HasAddon(plugin.video.scrubsv2)'):
                directory.add_file(
                    '--- Include Scrubs v2: {0}'.format(includescrubs.replace('true', on).replace('false', off)),
                    {'mode': 'togglecache', 'name': 'includescrubs'}, themeit=CONFIG.THEME3)
            if xbmc.getCondVisibility('System.HasAddon(plugin.video.thecrew)'):
                directory.add_file(
                    '--- Include THE CREW: {0}'.format(includethecrew.replace('true', on).replace('false', off)),
                    {'mode': 'togglecache', 'name': 'includethecrew'}, themeit=CONFIG.THEME3)
            if xbmc.getCondVisibility('System.HasAddon(plugin.video.venom)'):
                directory.add_file(
                    '--- Include Venom: {0}'.format(includevenom.replace('true', on).replace('false', off)),
                    {'mode': 'togglecache', 'name': 'includevenom'}, themeit=CONFIG.THEME3)
            if xbmc.getCondVisibility('System.HasAddon(plugin.video.yoda)'):
                directory.add_file(
                    '--- Include Yoda: {0}'.format(includeyoda.replace('true', on).replace('false', off)),
                    {'mode': 'togglecache', 'name': 'includeyoda'}, themeit=CONFIG.THEME3)
            directory.add_file('--- Enable All Video Addons', {'mode': 'togglecache', 'name': 'true'},
                               themeit=CONFIG.THEME3)
            directory.add_file('--- Disable All Video Addons', {'mode': 'togglecache', 'name': 'false'},
                               themeit=CONFIG.THEME3)

    def addon_menu(self):
        directory.add_file('Remove Addons', {'mode': 'removeaddons'}, themeit=CONFIG.THEME3)
        directory.add_dir('Remove Addon Data', {'mode': 'removeaddondata'}, themeit=CONFIG.THEME3)
        directory.add_dir('Enable/Disable Addons', {'mode': 'enableaddons'}, themeit=CONFIG.THEME3)
        # directory.add_file('Enable/Disable Adult Addons', 'toggleadult', themeit=CONFIG.THEME3)
        directory.add_file('Force Refresh all Repositories', {'mode': 'forceupdate'}, themeit=CONFIG.THEME3)
        directory.add_file('Force Update all Addons', {'mode': 'forceupdate', 'action': 'auto'}, themeit=CONFIG.THEME3)

   
    def logging_menu(self):
        errors = int(logging.error_checking(count=True))
        errorsfound = str(errors) + ' Error(s) Found' if errors > 0 else 'None Found'
        wizlogsize = ': [COLOR red]Not Found[/COLOR]' if not os.path.exists(
            CONFIG.WIZLOG) else ": [COLOR springgreen]{0}[/COLOR]".format(
            tools.convert_size(os.path.getsize(CONFIG.WIZLOG)))
            
        directory.add_file('Toggle Debug Logging', {'mode': 'enabledebug'}, themeit=CONFIG.THEME3)
        directory.add_file('Upload Log File', {'mode': 'uploadlog'}, themeit=CONFIG.THEME3)
        directory.add_file('View Errors in Log: [COLOR springgreen][B]{0}[/B][/COLOR]'.format(errorsfound), {'mode': 'viewerrorlog'}, themeit=CONFIG.THEME3)
        if errors > 0:
            directory.add_file('View Last Error In Log', {'mode': 'viewerrorlast'}, themeit=CONFIG.THEME3)
        directory.add_file('View Log File', {'mode': 'viewlog'}, themeit=CONFIG.THEME3)
        directory.add_file('View Wizard Log File', {'mode': 'viewwizlog'}, themeit=CONFIG.THEME3)
        directory.add_file('Clear Wizard Log File: [COLOR springgreen][B]{0}[/B][/COLOR]'.format(wizlogsize), {'mode': 'clearwizlog'}, themeit=CONFIG.THEME3)
   
        
    def tweaks_menu(self):
        directory.add_file('Scan Sources for broken links', {'mode': 'checksources'}, themeit=CONFIG.THEME3)
        directory.add_file('Scan For Broken Repositories', {'mode': 'checkrepos'}, themeit=CONFIG.THEME3)
        directory.add_file('Remove Non-Ascii filenames', {'mode': 'asciicheck'}, themeit=CONFIG.THEME3)
        # directory.add_file('Toggle Passwords On Keyboard Entry', {'mode': 'togglepasswords'}, themeit=CONFIG.THEME3)
        directory.add_file('Convert Paths to special', {'mode': 'convertpath'}, themeit=CONFIG.THEME3)
        directory.add_dir('System Information', {'mode': 'systeminfo'}, themeit=CONFIG.THEME3)
