# -*- coding: utf-8 -*-

'''
    wofvideo Addon
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

import os,sys,re,xbmc,xbmcgui,xbmcplugin,xbmcaddon
from bs4 import BeautifulSoup
from requests import Session

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

base_url = 'https://wofvideo.club/'
session = Session()

class navigator:
    def __init__(self):
        self.hash = xbmcaddon.Addon().getSetting('hash')
        self.phpsessid = xbmcaddon.Addon().getSetting('phpsessid')

    def root(self):
        page = session.get(base_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        xbmcaddon.Addon().setSetting('hash', soup.find('input', attrs={'class': 'main_session'}).get('value'))
        xbmcaddon.Addon().setSetting('phpsessid', session.cookies.get('PHPSESSID'))
        self.addDirectoryItem('Keresés', 'search', '', 'DefaultFolder.png')
        for link in soup.find_all('a', href=re.compile("videos"), string=True):
            categoryUrl = link.get('href')
            if xbmcaddon.Addon().getSettingBool('categories.' + categoryUrl.rsplit('/', 1)[1]):
                self.addDirectoryItem(link.string, 'category&url=%s' % categoryUrl, '', 'DefaultFolder.png')
        self.endDirectory()

    def getCategory(self, url, dataId=None, dataViews=None):
        if dataId:
            data = {'hash': self.hash, 'last_id': dataId, 'ids[0]': dataId, 'keyword': '', 'user_id': '0'}
            nextUrl = url.replace(base_url + 'videos', base_url + 'aj/load-more').replace('category/', 'category?c_id=') + '?views=%s' % dataViews
            xbmc.log('wofvideo: load URL: %s %s %s' % (nextUrl, dataId, dataViews), xbmc.LOGNOTICE)
            response = session.post(url=nextUrl, data=data, cookies={'PHPSESSID': self.phpsessid})
            soup = BeautifulSoup(response.json().get('videos'), 'html.parser')
        else:
            page = session.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')
            xbmc.log('wofvideo: load URL: %s' % url, xbmc.LOGNOTICE)

        movies = soup.find_all('div', attrs={'class': 'video-wrapper'}, limit=20) 
        for movie in movies:
            movieTitle = movie.find('img').get('alt').replace(' online','')
            moviePageUrl = movie.find('a').get('href')
            movieImg = movie.find('img').get('src')
            movieDurationArray = movie.find('div',  attrs={'class': 'video-duration'}).text.split(':')[::-1]
            movieDuration = int(movieDurationArray[0]) + (int(movieDurationArray[1]) * 60) + (0 if len(movieDurationArray) == 2 else (int(movieDurationArray[2]) *60 * 60)) 
            self.addDirectoryItem('[B]%s[/B]' % movieTitle, 'playmovie&url=%s' % moviePageUrl, movieImg, 'DefaultMovies.png', isFolder=False, meta={'title': movieTitle, 'plot': '', 'duration': movieDuration})

        if len(movies) >= 20:
            lastMovie = movies[len(movies)-1]
            self.addDirectoryItem('Következö', 'category&url=%s&dataId=%s&dataViews=%s' % (url, lastMovie.get('data-id'), lastMovie.get('data-views')), '', 'DefaultFolder.png')

        self.endDirectory('movies')

    def playmovie(self, url):
        page = session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        try:
            movieUrl = soup.find('source').get('src')
            if movieUrl:
                xbmc.log('wofvideo: playing URL: %s' % movieUrl, xbmc.LOGNOTICE)
                play_item = xbmcgui.ListItem(path=movieUrl)
                xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
        except Exception as e:
            xbmc.log('wofvideo: unable to playing URL: %s' % url, xbmc.LOGERROR)
            xbmcgui.Dialog().notification(url, e.message)
            return

    def doSearch(self):
        search_text = self.getSearchText()
        if search_text != '':
            data = {'hash': self.hash, 'search_value': search_text}
            searchUrl = base_url + 'aj/search'
            xbmc.log('wofvideo: search URL: %s' % searchUrl, xbmc.LOGNOTICE)
            response = session.post(url=searchUrl, data=data, cookies={'PHPSESSID': self.phpsessid})
            if response.json().get('status') == 200:
                soup = BeautifulSoup(response.json().get('html'), 'html.parser')
                movies = soup.find_all('div', attrs={'class': 'search-result'}) 
                for movie in movies:
                    movieTitle = movie.find('a').text.replace(' online','')
                    moviePageUrl = movie.find('a').get('href')
                    self.addDirectoryItem('[B]%s[/B]' % movieTitle, 'playmovie&url=%s' % moviePageUrl, '', 'DefaultMovies.png', isFolder=False, meta={'title': movieTitle, 'plot': ''})
                    self.endDirectory('movies')	

    def getSearchText(self):
        search_text = ''
        keyb = xbmc.Keyboard('',u'Add meg a keresend\xF5 film c\xEDm\xE9t')
        keyb.doModal()
        if (keyb.isConfirmed()):
            search_text = keyb.getText()
        return search_text

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        if thumb == '': thumb = icon
        cm = []
        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        if not context == None: cm.append((context[0].encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart == None: Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if isFolder == False: item.setProperty('IsPlayable', 'true')
        if not meta == None: item.setInfo(type='Video', infoLabels = meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)
