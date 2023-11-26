# -*- coding: utf-8 -*-

'''
    Filmezek Addon
    Copyright (C) 2023 heg, vargalex

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

import os, sys, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, locale, base64
from bs4 import BeautifulSoup
import requests
import urllib.parse
import resolveurl as urlresolver
from resources.lib.modules.utils import py2_decode, py2_encode
import html

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

base_url = 'https://filmezek.com'

headers = {
    'authority': 'filmezek.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'referer': 'https://filmezek.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
}

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

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
        self.addDirectoryItem("Filmek", f"movie_items&url={base_url}/legujabb/", '', 'DefaultFolder.png')
        self.addDirectoryItem("Sorozatok", f"series_items&url={base_url}/sorozatok/legujabb/", '', 'DefaultFolder.png')
        self.addDirectoryItem("Film Kategóriák", "movie_categories", '', 'DefaultFolder.png')
        self.addDirectoryItem("Keresés", "search", '', 'DefaultFolder.png')
        self.endDirectory()
        
    def getMovieCategories(self):
        page = requests.get(f"{base_url}/filmek/legujabb/", headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        for genre_div in soup.find_all('div', class_='col-md-4 col-xs-6'):
            genre_link = genre_div.find('a')['href']
            genre_name = genre_div.find('span', class_='badge badge-primary').text.strip()
            
            enc_link = urllib.parse.quote(genre_link, safe=':/') + 'legujabb/'
            xbmc.log(f'Filmezek | getMovieCategories | enc_link | {enc_link}', xbmc.LOGINFO)
            
            self.addDirectoryItem(f"{genre_name}", f'items&url={enc_link}', '', 'DefaultFolder.png')

        self.endDirectory()

    def getItems(self, url):
        import re
    
        pattern = r"-.*[eé]vad"
        
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
    
        for movie_box in soup.find_all('div', class_='moviebox'):
        
            card_link = movie_box.find('a')['href']
            
            hun_title = movie_box.find('div', class_='caption-text-title').find('h5').text
            img_url = movie_box.find('a').find('img')['src']

            if hun_title is not None and isinstance(hun_title, str) and re.search(pattern, hun_title):
                type = 'Sorozat'
                self.addDirectoryItem(f'[B]|{type}| {hun_title}[/B]', f'get_series_providers&url={card_link}&img_url={img_url}&hun_title={hun_title}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})
            else:
                type = 'Film'
                self.addDirectoryItem(f'[B]|{type:^10}| {hun_title}[/B]', f'get_movie_providers&url={card_link}&img_url={img_url}&hun_title={hun_title}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})
            
        try:
            next_page_element = soup.find('li', class_='active').find_next_sibling('li')
            next_page_url = next_page_element.find('a')['href'] if next_page_element else None
            
            self.addDirectoryItem('[I]Következő oldal[/I]', f'items&url={quote_plus(next_page_url)}', '', 'DefaultFolder.png')
        except AttributeError:
            xbmc.log(f'Filmezek | getItems | next_page_url | csak egy oldal található', xbmc.LOGINFO)
        
        self.endDirectory('movies')

    def getMovieProviders(self, url):
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        img_element = soup.select_one('.img-movie')
        img_url = img_element['src'] if img_element and 'src' in img_element.attrs else None

        imdb_rating_element = soup.select_one('.movielist .btn-default')
        imdb_rating = imdb_rating_element.text.strip() if imdb_rating_element else None

        hun_title_element = soup.select_one('.media-body h4')
        hun_title = hun_title_element.text.strip() if hun_title_element else None

        en_title_element = soup.select_one('.media-body h6')
        en_title = en_title_element.text.strip() if en_title_element else None

        content_element = soup.select_one('.media-body p')
        content = content_element.text.strip() if content_element else None

        anchor_tag = soup.find('a', {'onclick': True})

        onclick_value = anchor_tag['onclick']
        link_match = re.search(r"window\.open\('(.+?)'\);", onclick_value)
        link_2 = link_match.group(1)

        resp2 = requests.get(link_2, headers=headers).text

        soup_2 = BeautifulSoup(resp2, 'html.parser')
        play_icons = soup_2.find_all('i', {'data-mediatype': True, 'data-video_id': True})

        unique_combinations = []

        for play_icon in play_icons:
            mediatype = play_icon['data-mediatype']
            video_id = play_icon['data-video_id']

            td_tags = play_icon.find_all_next('td', limit=4)

            provider = td_tags[0].text.strip()
            lang = td_tags[1].text.strip()
            quality = td_tags[2].text.strip()

            skip_iteration = False

            if mediatype and video_id and provider and lang and quality:

                #lang
                lang_category = None
                if 'szinkron' in lang.lower():
                    lang_category = 'Szinkron'
                elif 'felirat' in lang.lower():
                    lang_category = 'Felirat'
                elif 'eredet' in lang.lower():
                    lang_category = 'Eredeti'
                else:
                    lang_category = lang

                #quality
                quali_category = None
                if 'mozi' in quality.lower():
                    quali_category = 'Mozis'
                else:
                    quali_category = quality

                if skip_iteration:
                    continue

                combination_dict = {
                    "mediatype": mediatype,
                    "video_id": video_id,
                    "provider": provider,
                    "lang": lang_category,
                    "quality": quali_category,
                }

                if combination_dict not in unique_combinations:
                    unique_combinations.append(combination_dict)

                    self.addDirectoryItem(f'[B][COLOR lightblue]{quali_category}[/COLOR] | [COLOR orange]{lang_category}[/COLOR] | [COLOR red]{provider}[/COLOR] | {hun_title}[/B]', f'extract_movie_provider&mediatype={mediatype}&video_id={video_id}&img_url={img_url}&hun_title={hun_title}&content={content}&provider={provider}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': provider, 'plot': content})

        self.endDirectory('movies')        

    def extractMovieProviders(self, mediatype, video_id, img_url, hun_title, content, provider):

        data = {
            'datatype': mediatype,
            'videodataid': video_id,
        }

        resp_3 = requests.post('https://online-filmek.app/ajax/load.php', headers=headers, data=data).text

        fix_prov_url = re.sub(r'\"', r'', resp_3)
        fix_prov_url = re.sub(r'(\\/)', '/', fix_prov_url)
        fix_prov_url = f'{quote_plus(fix_prov_url)}'

        self.addDirectoryItem(f'[B][COLOR red]{provider}[/COLOR] | {hun_title}[/B]', f'playmovie&url={fix_prov_url}', img_url, 'DefaultMovies.png', isFolder=False, meta={'title': hun_title, 'plot': content})

        self.endDirectory('movies')

    def getSeriesProviders(self, url):
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        one_season = []

        img_element = soup.select_one('.img-movie')
        img_url = img_element['src'] if img_element and 'src' in img_element.attrs else None

        imdb_rating_element = soup.select_one('.movielist .btn-default')
        imdb_rating = imdb_rating_element.text.strip() if imdb_rating_element else None

        hun_title_element = soup.select_one('.media-body h4')
        hun_title = hun_title_element.text.strip() if hun_title_element else None

        en_title_element = soup.select_one('.media-body h6')
        en_title = en_title_element.text.strip() if en_title_element else None

        content_element = soup.select_one('.media-body p')
        content = content_element.text.strip() if content_element else None

        series_data = {
            "img_url": img_url,
            "imdb_rating": imdb_rating,
            "hun_title": hun_title,
            "en_title": en_title,
            "tartalom": content
        }

        one_season.append(series_data)

        try:
            first_ep_link = re.findall(r"window.open\('(https://.*)'\).*\"nofollow\">", str(soup))[0].strip()
            
            response_2 = requests.get(first_ep_link, headers=headers)
            soup_season = BeautifulSoup(response_2.text, 'html.parser')

            resz_buttons = soup_season.find_all('div', class_='btn-resz')

            for index, resz_button in enumerate(resz_buttons, start=1):
                button_element = resz_button.find('button')
                if button_element:
                    resz_number = f"resz{index}"
                    ep_title = button_element.text.strip()

                    table = resz_button.find_next('table')
                    if table:
                        rows = table.find_all('tr')
                        for row in rows:
                            cells = row.find_all('td')

                            if len(cells) >= 4:
                                play_icon = cells[0].find('i')

                                if play_icon:
                                    mediatype = play_icon.get('data-mediatype', '')
                                    video_id = play_icon.get('data-video_id', '')
                                else:
                                    mediatype = ''
                                    video_id = ''

                                quality = cells[1].text.strip()
                                lang = cells[2].text.strip()
                                provider = cells[3].text.strip()
                                provider = re.sub(r'( tipp)', r'', provider)

                                if all([ep_title, mediatype, video_id, quality, lang, provider]):

                                    # lang
                                    lang_category = None
                                    if 'szinkron' in lang.lower():
                                        lang_category = 'Szinkron'
                                    elif 'felirat' in lang.lower():
                                        lang_category = 'Felirat'
                                    elif 'eredet' in lang.lower():
                                        lang_category = 'Eredeti'
                                    else:
                                        lang_category = lang

                                    # quality
                                    quali_category = None
                                    if 'mozi' in quality.lower():
                                        quali_category = 'Mozis'
                                    else:
                                        quali_category = quality

                                    providers = {
                                        "resz": resz_number,
                                        "ep_title": ep_title,
                                        "mediatype": mediatype,
                                        "video_id": video_id,
                                        "quality": quali_category,
                                        "lang": lang_category,
                                        "provider": provider,
                                    }

                                    one_season[-1].setdefault("providers_info", []).append(providers)

                                    def color_and_concatenate(ep_title):
                                        episode_matches = re.findall(r'(\d+)\.rész', ep_title)
                                        colored_text = ""
                                        for episode_number in episode_matches:
                                            color_code = "lightgreen" if int(episode_number) % 2 == 0 else "yellow"
                                            colored_text += f"[COLOR {color_code}]{episode_number}.rész[/COLOR] "
                                        return colored_text.strip()                                

                                    for stuffs in one_season:
                                        providers_info = stuffs.get('providers_info', [])
                                        for provider_info in providers_info:
                                            if 'ep_title' in provider_info:
                                                ep_title = provider_info['ep_title']
                                                mediatype = provider_info['mediatype']
                                                video_id = provider_info['video_id']
                                                quality = provider_info['quality']
                                                lang = provider_info['lang']
                                                provider = provider_info['provider']

                                        colored_text = color_and_concatenate(ep_title)

                                        self.addDirectoryItem(f'[B]{colored_text} | [COLOR lightblue]{quali_category}[/COLOR] | [COLOR orange]{lang_category}[/COLOR] | [COLOR red]{provider}[/COLOR] | {hun_title}[/B]', f'extract_series_provider&mediatype={mediatype}&video_id={video_id}&img_url={img_url}&hun_title={hun_title}&content={content}&provider={provider}&ep_title={ep_title}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title, 'plot': content})
        except IndexError:
            xbmc.log(f'Filmezek | getSeriesProviders | name: No video sources found', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("Filmezek", "Nem található epizód", time=5000)

        self.endDirectory('series')

    def extractSeriesProviders(self, mediatype, video_id, img_url, hun_title, content, provider, ep_title):
        data = {
            'datatype': mediatype,
            'videodataid': video_id,
        }

        resp_3 = requests.post('https://online-filmek.app/ajax/load.php', headers=headers, data=data).text

        fix_prov_url = re.sub(r'\"', r'', resp_3)
        fix_prov_url = re.sub(r'(\\/)', '/', fix_prov_url)
        fix_prov_url = f'{quote_plus(fix_prov_url)}'

        def color_and_concatenate(ep_title):
            episode_matches = re.findall(r'(\d+)\.rész', ep_title)
            colored_text = ""
            for episode_number in episode_matches:
                color_code = "lightgreen" if int(episode_number) % 2 == 0 else "yellow"
                colored_text += f"[COLOR {color_code}]{episode_number}.rész[/COLOR] "
            return colored_text.strip()                       

        colored_text = color_and_concatenate(ep_title)

        ep_hun_title = ep_title +' - '+ hun_title

        self.addDirectoryItem(f'[B][COLOR red]{provider}[/COLOR] | {colored_text} | {hun_title}[/B]', f'playmovie&url={fix_prov_url}', img_url, 'DefaultMovies.png', isFolder=False, meta={'title': ep_hun_title, 'plot': content})

        self.endDirectory('series')    

    def getMovieItems(self, url):
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        for movie_box in soup.find_all('div', class_='moviebox'):

            card_link = movie_box.find('a')['href']

            hun_title = movie_box.find('div', class_='caption-text-title').find('h5').text
            img_url = movie_box.find('a').find('img')['src']

            self.addDirectoryItem(f'[B]{hun_title}[/B]', f'get_movie_providers&url={card_link}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})

        try:
            next_page_element = soup.find('li', class_='active').find_next_sibling('li')
            next_page_url = next_page_element.find('a')['href'] if next_page_element else None

            self.addDirectoryItem('[I]Következő oldal[/I]', f'movie_items&url={quote_plus(next_page_url)}', '', 'DefaultFolder.png')
        except AttributeError:
            xbmc.log(f'Filmezek | getMovieItems | next_page_url | csak egy oldal található', xbmc.LOGINFO)

        self.endDirectory('movies')

    def getSeriesItems(self, url):
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        for movie_box in soup.find_all('div', class_='moviebox'):

            card_link = movie_box.find('a')['href']

            hun_title = movie_box.find('div', class_='caption-text-title').find('h5').text
            img_url = movie_box.find('a').find('img')['src']

            self.addDirectoryItem(f'[B]{hun_title}[/B]', f'get_series_providers&url={card_link}', img_url, 'DefaultMovies.png', isFolder=True, meta={'title': hun_title})

        try:
            next_page_element = soup.find('li', class_='active').find_next_sibling('li')
            next_page_url = next_page_element.find('a')['href'] if next_page_element else None

            self.addDirectoryItem('[I]Következő oldal[/I]', f'series_items&url={quote_plus(next_page_url)}', '', 'DefaultFolder.png')
        except AttributeError:
            xbmc.log(f'Filmezek | getSeriesItems | next_page_url | csak egy oldal található', xbmc.LOGINFO)

        self.endDirectory('movies')

    def playMovie(self, url):
        try:
            direct_url = urlresolver.resolve(url)

            xbmc.log(f'Filmezek | playMovie | direct_url: {direct_url}', xbmc.LOGINFO)
            play_item = xbmcgui.ListItem(path=direct_url)
            if 'm3u8' in direct_url:
                from inputstreamhelper import Helper
                is_helper = Helper('hls')
                if is_helper.check_inputstream():
                    play_item.setProperty('inputstream', 'inputstream.adaptive')  # compatible with recent builds Kodi 19 API
                    play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
        except:
            xbmc.log(f'Filmezek | playMovie | name: No video sources found', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("Filmezek", "Törölt tartalom", time=5000)

    def getSearches(self):
        self.addDirectoryItem('[COLOR lightgreen]Új keresés[/COLOR]', 'newsearch', '', 'DefaultFolder.png')
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
                url_p = f"{base_url}/search_cat.php?film={item}&type=1"
                enc_url = quote_plus(url_p)                
                self.addDirectoryItem(item, f'items&url={url_p}', '', 'DefaultFolder.png')

            if len(items) > 0:
                self.addDirectoryItem('[COLOR red]Keresési előzmények törlése[/COLOR]', 'deletesearchhistory', '', 'DefaultFolder.png')
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
            file.write(f"{search_text}\n")
            file.close()
            url = f"{base_url}/search_cat.php?film={search_text}&type=1"
            self.getItems(url, None, None, None)

    def getSearchText(self):
        search_text = ''
        keyb = xbmc.Keyboard('', u'Add meg a keresend\xF5 film c\xEDm\xE9t')
        keyb.doModal()
        if keyb.isConfirmed():
            search_text = keyb.getText()
        return search_text

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = f'{sysaddon}?action={query}' if isAction else query
        if thumb == '':
            thumb = icon
        cm = []
        if queue:
            cm.append((queueMenu, f'RunPlugin({sysaddon}?action=queueItem)'))
        if not context is None:
            cm.append((context[0].encode('utf-8'), f'RunPlugin({sysaddon}?action={context[1]})'))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart is None:
            Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if not isFolder:
            item.setProperty('IsPlayable', 'true')
        if not meta is None:
            item.setInfo(type='Video', infoLabels=meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)