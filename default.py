# -*- coding: utf-8 -*-

'''
    Filmezek Add-on
    Copyright (C) 2020 heg, vargalex

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

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
url = params.get('url')

mediatype = params.get('mediatype')
video_id = params.get('video_id')
img_url = params.get('img_url')
hun_title = params.get('hun_title')
content = params.get('content')
provider = params.get('provider')
ep_title = params.get('ep_title')

if action is None:
    navigator.navigator().root()

elif action == 'movie_categories':
    navigator.navigator().getMovieCategories()

elif action == 'get_movie_providers':
    navigator.navigator().getMovieProviders(url, mediatype, video_id, img_url, hun_title, content, provider)

elif action == 'extract_movie_provider':
    navigator.navigator().extractMovieProviders(mediatype, video_id, img_url, hun_title, content, provider)

elif action == 'get_series_providers':
    navigator.navigator().getSeriesProviders(url, mediatype, video_id, img_url, hun_title, content, provider, ep_title)

elif action == 'extract_series_provider':
    navigator.navigator().extractSeriesProviders(mediatype, video_id, img_url, hun_title, content, provider, ep_title)

elif action == 'only_movies':
    navigator.navigator().getOnlyMovies()

elif action == 'only_series':
    navigator.navigator().getOnlySeries()

elif action == 'items':
    navigator.navigator().getItems(url, img_url, hun_title, content)

elif action == 'search':
    navigator.navigator().getSearches()

elif action == 'movie_items':
    navigator.navigator().getMovieItems(url)

elif action == 'series_items':
    navigator.navigator().getSeriesItems(url)

elif action == 'playmovie':
    navigator.navigator().playMovie(url)

elif action == 'newsearch':
    navigator.navigator().doSearch()

elif action == 'deletesearchhistory':
    navigator.navigator().deleteSearchHistory()