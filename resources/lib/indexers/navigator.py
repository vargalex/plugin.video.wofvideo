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

import os,sys,re,xbmc,xbmcgui,xbmcplugin,xbmcaddon, locale, base64
from bs4 import BeautifulSoup
from requests import Session
from resources.lib.modules.utils import py2_decode

sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

base_url = 'https://wofvideo.club/'
ajax_url = '%s%s' % (base_url, 'wp-admin/admin-ajax.php')
session = Session()

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
else:
    from xbmc import translatePath

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        self.base_path = py2_decode(translatePath(xbmcaddon.Addon().getAddonInfo('profile')))
        self.searchFileName = os.path.join(self.base_path, "search.history")

    def root(self):
        self.addDirectoryItem("Kategóriák", "categories", '', 'DefaultFolder.png')
        self.addDirectoryItem("Megjelenés éve", "years", '', 'DefaultFolder.png')
        self.addDirectoryItem("Keresés", "search", '', 'DefaultFolder.png')
        self.endDirectory()

    def getCategories(self):
        page = session.get(base_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        for category in soup.find_all('li', attrs={'class': 'cat-item'}):
            link = category.find('a')
            matches = re.search(r'^(.*)\(([0-9]*)\)(.*)$', str(category), re.S)
            cnt = ''
            if matches != None:
                cnt = " (%s)" % matches.group(2) 
            self.addDirectoryItem("%s%s" % (link.string, cnt), 'items&url=%s' % link.get('href'), '', 'DefaultFolder.png')
        self.endDirectory()

    def getYears(self):
        page = session.get(base_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        years = soup.find('section', attrs={'id': 'torofilm_movies_annee-2'})
        for yearli in years.find_all('li'):
            link = yearli.find('a').get('href')
            year = yearli.find('a').string
            self.addDirectoryItem(year, 'items&url=%s' % link, '', 'DefaultFolder.png')
        self.endDirectory()

    def getItems(self, url):
        page = session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        xbmc.log('wofvideo: load URL: %s' % url, xbmc.LOGINFO)

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
                self.addDirectoryItem('[I]Következö oldal[/I]', 'items&url=%s' % hrefs[len(hrefs)-1].get('href'), '', 'DefaultFolder.png')
        self.endDirectory('movies')

    def getSeasons(self, url):
        page = session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        movieImg = ''
        article = soup.find('article', attrs={'class': 'post single'})
        if article:
            img = article.find('img')
            if img:
                movieImg = img.get('src')
        header = soup.find('header', attrs={'class': 'entry-header'})
        if header != None:
            title = header.find('h1', attrs={'class': 'entry-title'}).string
            descDiv = soup.find('div', attrs={'class': 'description'})
            if descDiv != None:
                desc = descDiv.find('p')
                if desc != None:
                    desc = desc.string
                    seasonUrl = descDiv.find('a').get('href')
                    if seasonUrl != None:
                        page = session.get(seasonUrl)
                        soup = BeautifulSoup(page.text, 'html.parser')
                        entryContent = soup.find('div', attrs={'class': 'entry-content'})
                        seasons =entryContent.find_all('ul')
                        seasonNr = 0
                        for season in seasons:
                            seasonNr += 1
                            self.addDirectoryItem('[B]%d. évad[/B]' % seasonNr, 'episodes&title=%s&season=%d&desc=%s&url=%s&img=%s' % (title, seasonNr, desc, seasonUrl, movieImg), movieImg, 'DefaultMovies.png', isFolder=True, meta={'title': title, 'plot': desc})
        self.endDirectory('tvshows')

    def getEpisodes(self, title, season, desc, url, img):
        page = session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        entryContent = soup.find('div', attrs={'class': 'entry-content'})
        actSeason = entryContent.find_all('ul')[int(season)-1]
        episodes = actSeason.find_all('li')
        for episode in episodes:
            href = episode.find('a').get('href')
            episodeTitle = episode.find('a').string
            self.addDirectoryItem('[B]%s[/B]' % episodeTitle, 'playmovie&url=%s' % href, img, 'DefaultMovies.png', isFolder=False, meta={'title': episodeTitle, 'plot': desc})
        self.endDirectory('episodes')

    def playmovie(self, url):
        page = session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        url = soup.find('a', attrs={'rel': 'noopener', 'target': '_blank', 'class': 'maxbutton-1 maxbutton maxbutton-b1'})
        if url != None:
            page = session.get(url.get('href'))
            soup = BeautifulSoup(page.text, 'html.parser')
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            iframeSrc = iframe.get('src')
            if iframeSrc != None and not "player.twitch" in iframeSrc:
                page = session.get(iframeSrc)
                soup = BeautifulSoup(page.text, 'html.parser')
                playlist = soup.find('ul', attrs={'id': 'fwduvpPlaylist0'})
                if playlist != None:
                    videoSource = playlist.find('li').get('data-video-source')
                    if videoSource != None:
                        matches=re.search(r'^(.*)source:([^\']*)\'([^\']*)\'(.*)', videoSource, re.S)
                        if matches != None:
                            if "encrypt:" in matches.group(3):
                                videoURL = base64.b64decode(matches.group(3).replace("encrypt:", "")).decode('utf-8')
                            else:
                                videoURL = matches.group(3)
                            try:
                                xbmc.log('wofvideo: playing URL: %s' % videoURL, xbmc.LOGINFO)
                                play_item = xbmcgui.ListItem(path=videoURL)
                                xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
                            except Exception as e:
                                xbmc.log('wofvideo: unable to playing URL: %s' % url, xbmc.LOGERROR)
                                xbmcgui.Dialog().notification(url, str(e))
                                return
                            
    def getSearches(self):
        self.addDirectoryItem('Új keresés', 'newsearch', '', 'DefaultFolder.png')
        try:
            file = open(self.searchFileName, "r")
            olditems = file.read().splitlines()
            file.close()
            items = list(set(olditems))
            items.sort(key=locale.strxfrm)
            if len(items) != len(olditems):
                file = open(self.searchFileName, "w")
                file.write("\n".join(items))
                file.close()
            for item in items:
                self.addDirectoryItem(item, 'items&url=%s?s=%s' % (base_url, item), '', 'DefaultFolder.png')
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
            self.getItems("%s?s=%s" % (base_url, search_text))

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
