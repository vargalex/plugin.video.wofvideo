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

import os,sys,re,xbmc,xbmcgui,xbmcplugin,xbmcaddon, locale
from bs4 import BeautifulSoup
from requests import Session

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

base_url = 'https://wofvideo.club/'
ajax_url = '%s%s' % (base_url, 'wp-admin/admin-ajax.php')
session = Session()

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "")
        except:
            pass
        self.base_path = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
        self.searchFileName = os.path.join(self.base_path, "search.history")

    def root(self):
        page = session.get(base_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        #xbmcaddon.Addon().setSetting('hash', soup.find('input', attrs={'class': 'main_session'}).get('value'))
        #xbmcaddon.Addon().setSetting('phpsessid', session.cookies.get('PHPSESSID'))
        self.addDirectoryItem('Keresés', 'search', '', 'DefaultFolder.png')
        #for link in soup.find_all('a', href=re.compile("category"), string=True):
        for category in soup.find_all('li', attrs={'class': 'cat-item'}):
            link = category.find('a')
            matches = re.search(r'^(.*)\(([0-9]*)\)(.*)$', str(category), re.S)
            cnt = ''
            if matches != None:
                cnt = " (%s)" % matches.group(2) 
            #if xbmcaddon.Addon().getSettingBool('categories.' + categoryUrl.rsplit('/', 1)[1]):
            self.addDirectoryItem("%s%s" % (link.string, cnt), 'category&url=%s' % link.get('href'), '', 'DefaultFolder.png')
        self.endDirectory()

    def getCategory(self, url):
        page = session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        xbmc.log('wofvideo: load URL: %s' % url, xbmc.LOGNOTICE)

        allmovies = soup.find('div', attrs={'class': 'aa-cn', 'id': 'aa-movies'})
        movies = allmovies.find_all('li', attrs={'class': 'hentry'})
        for movie in movies:
            movieTitle = movie.find('h2').string
            moviePageUrl = movie.find('a').get('href')
            movieImg = movie.find('img').get('src')
            sorozat = ''
            action = 'playmovie'
            isFolder = False
            if 'series' in str(moviePageUrl):
                sorozat = ' (sorozat)'
                action = 'seasons'
                isFolder = True
            self.addDirectoryItem('[B]%s[/B]%s' % (movieTitle, sorozat), '%s&url=%s' % (action, moviePageUrl), movieImg, 'DefaultMovies.png', isFolder=isFolder, meta={'title': movieTitle, 'plot': ''})

        navLinks = soup.find('div', attrs={'class': 'nav-links'})
        if navLinks != None:
            hrefs = navLinks.find_all('a')
            if hrefs[len(hrefs)-1].string == 'NEXT':
                self.addDirectoryItem('[I]Következö oldal[/I]', 'category&url=%s' % hrefs[len(hrefs)-1].get('href'), '', 'DefaultFolder.png')
        self.endDirectory('movies')

    def getSeasons(self, url):
        page = session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        #xbmc.log('wofvideo getSeasons: load URL: %s' % url, xbmc.LOGNOTICE)
        movieImg = ''
        article = soup.find('article', attrs={'class': 'post single'})
        if article:
            img = article.find('img')
            if img:
                movieImg = img.get('src')
        header = soup.find('header', attrs={'class': 'entry-header'})
        if header != None:
            title = header.find('h1', attrs={'class': 'entry-title'}).string
            desc = soup.find('div', attrs={'class': 'description'})
            if desc != None:
                desc = desc.find('p')
                if desc != None:
                    desc = desc.string
                    seasons = soup.find_all('li', attrs={'class': 'sel-temp'})
                    for season in seasons:
                        link = season.find('a')
                        if link != None:
                            datapost = link.get('data-post')
                            dataseason = link.get('data-season')
                            self.addDirectoryItem('[B]%s[/B]' % link.string, 'episodes&title=%s&post=%s&season=%s&desc=%s' % (title, datapost, dataseason, desc), movieImg, 'DefaultMovies.png', isFolder=True, meta={'title': title, 'plot': desc})
        self.endDirectory('tvshows')

    def getEpisodes(self, title, post, season, desc):
        data = {'action': 'action_select_season', 'season': season, 'post': post}
        page = session.post(ajax_url, data)
        soup = BeautifulSoup(page.text, 'html.parser')
        xbmc.log('wofvideo: load URL: %s' % ajax_url, xbmc.LOGNOTICE)
        articles = soup.find_all('article')
        for article in articles:
            img = article.find('img').get('src')
            episode = article.find('h2', attrs={'class': 'entry-title'}).string
            href = article.find('a', attrs={'class': 'lnk-blk'}).get('href')
            self.addDirectoryItem('[B]%s[/B]' % episode, 'playmovie&url=%s' % href, ('https:%s' % img) if img[0:2] == '//' else img, 'DefaultMovies.png', isFolder=False, meta={'title': episode, 'plot': desc})
        self.endDirectory('episodes')

    def playmovie(self, url):
        page = session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        url = soup.find('a', attrs={'rel': 'noopener', 'target': '_blank'})
        if url != None:
            page = session.get(url.get('href'))
            soup = BeautifulSoup(page.text, 'html.parser')
        else:
            iframeSrc = soup.find('iframe').get('src')
            page = session.get(iframeSrc)
            soup = BeautifulSoup(page.text, 'html.parser')    
        iframeSrc = soup.find('iframe').get('src')
        if iframeSrc != None:
            page = session.get(iframeSrc)
            soup = BeautifulSoup(page.text, 'html.parser')
            playlist = soup.find('ul', attrs={'id': 'fwduvpPlaylist0'})
            if playlist != None:
                videoSource = playlist.find('li').get('data-video-source')
                if videoSource != None:
                    matches=re.search(r'^(.*)source:([^\']*)\'([^\']*)\'(.*)', videoSource, re.S)
                    if matches != None:
                        try:
                            xbmc.log('wofvideo: playing URL: %s' % matches.group(3), xbmc.LOGNOTICE)
                            play_item = xbmcgui.ListItem(path=matches.group(3))
                            xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
                            return
                        except Exception as e:
                            xbmc.log('wofvideo: unable to playing URL: %s' % url, xbmc.LOGERROR)
                            xbmcgui.Dialog().notification(url, e.message)
                            return
    def getSearches(self):
        self.addDirectoryItem('Új keresés', 'newsearch', '', 'DefaultFolder.png')
        try:
            file = open(self.searchFileName, "r")
            items = file.read().splitlines()
            items.sort(cmp=locale.strcoll)
            file.close()
            for item in items:
                self.addDirectoryItem(item, 'category&url=%s?s=%s' % (base_url, item), '', 'DefaultFolder.png')
            if len(items) > 0:
                self.addDirectoryItem('Keresési előzmények törlése', 'deletesearchhistory', '', 'DefaultFolder.png') 
        except:
            pass   
        self.endDirectory()

    def deleteSearchHistory(self):
        if os.path.exists(self.searchFileName):
            os.remove(self.searchFileName)

    def doSearch(self):
        search_text = self.getSearchText()
        if search_text != '':
            if not os.path.exists(self.base_path):
                os.mkdir(self.base_path)
            file = open(self.searchFileName, "a")
            file.write("%s\n" % search_text)
            file.close()
            self.getCategory("%s?s=%s" % (base_url, search_text))

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
