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

import urlparse,sys
from resources.lib.indexers import navigator

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))
action = params.get('action')
url = params.get('url')
dataId = params.get('dataId')
dataViews = params.get('dataViews')

n = navigator.navigator()
if action == None:
    n.root()

elif action == 'category':
    n.getCategory(url, dataId, dataViews)

elif action == 'playmovie':
    n.playmovie(url)

elif action == 'search':
    n.doSearch()