# -*- coding: utf-8 -*-

'''
    wofvideo Add-on
    Copyright (C) 2020 btibi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import sys
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl


params = dict(parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')
url = params.get('url')
title = params.get('title')
season = params.get('season')
desc = params.get('desc')
img = params.get('img')

n = navigator.navigator()

if action == None:
    n.root()

elif action == 'categories':
    n.getCategories()

elif action == 'years':
    n.getYears()

elif action == 'search':
    n.getSearches()

elif action == 'items':
    n.getItems(url)

elif action == 'seasons':
    n.getSeasons(url)

elif action == 'episodes':
    n.getEpisodes(title, season, desc, url, img)

elif action == 'playmovie':
    n.playmovie(url)

elif action == 'newsearch':
    n.doSearch()

elif action == 'deletesearchhistory':
    n.deleteSearchHistory()