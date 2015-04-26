# -*- coding: utf-8 -*-

"""
condensation.api
~~~~~~~~~~~~~~~~

This modules implements the Condensation API

:copyright: (c) 2015 by Ben Riggleman
:license: Apache2, see LICENSE for more details

"""

from .utils import chunk, convert_steamid
from bs4 import BeautifulSoup
import requests
import json
import re

class SteamAPI(object):
    DOMAIN = 'http://api.steampowered.com/'

    # Steam API paths
    API_PATHS = {'get_news_for_app': '%sISteamNews/GetNewsForApp/v0002/',
                 'get_global_achievement_pct': '%sISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/',
                 'get_global_stats_for_game': '%sISteamUserStats/GetGlobalStatsForGame/v0001/',
                 'get_player_summaries': '%sISteamUser/GetPlayerSummaries/v0002/',
                 'get_friend_list': '%sISteamUser/GetFriendList/v0001/',
                 'get_player_achievements': '%sISteamUserStats/GetPlayerAchievements/v0001/',
                 'get_user_stats_for_game': '%sISteamUserStats/GetUserStatsForGame/v0002/',
                 'get_owned_games': '%sIPlayerService/GetOwnedGames/v0001/',
                 'get_recently_played_games': '%sIPlayerService/GetRecentlyPlayedgames/v0001/',
                 'is_playing_shared_game': '%sIPlayerService/IsPlayingSharedGame/v0001/',
                 'resolve_vanity_url': '%sISteamUser/ResolveVanityURL/v0001/'}

    VANITY_URL = re.compile('(?<=http://steamcommunity.com/id/)([0-9a-zA-Z_]*)')
    PROFILE_URL = re.compile('(?<=http://steamcommunity.com/profiles/)([0-9]*)')

    ONLINE_STATE = {
        0: 'Offline',
        1: 'Online',
        2: 'Busy',
        3: 'Away',
        4: 'Snooze',
        5: 'Looking to Trade',
        6: 'Looking to Play'
    }

    def __init__(self, apikey):
        self._apikey = apikey

    @property
    def apikey(self):
        return self._apikey

    @apikey.setter
    def apikey(self, apikey):
        self._apikey = self._apikey

    def news(self, appid, **kwargs):
        """
        Returns the latest news for a game specified by its appid
        :param appid: appid of the game you want the news of
        :param count: how many news entities you want to get returned
        :param maxlength: maximum length of each news entry
        :return: appid, newsitems
        """
        params = {
            'appid': appid,
            'count': kwargs.pop('count', 1),
            'maxlength': kwargs.pop('maxlength', 1000)
        }

        url = self.API_PATHS['get_news_for_app'] % self.DOMAIN
        request = requests.get(url, params=params)

        if request.status_code == 200:
            data = json.loads(request.text)

            values = {
                'appid': data['appnews']['appid'],
                'newsitems': data['appnews']['newsitems']
            }

            return values
        else:
            return None

    def global_achievements(self, appid):
        """
        Returns global achievements overview of a specific game in percentages
        :param appid: appid of the game you want the achievements for
        :return:
        """

        params = {
            'gameid': appid
        }

        url = self.API_PATHS['get_global_achievement_pct'] % self.DOMAIN
        request = requests.get(url, params=params)

        if request.status_code == 200:
            data = json.loads(request.text)

            return data['achievementpercentages']['achievements']
        else:
            request.status_code

    #todo implement GetGlobalStatsForGame

    def summaries(self, sids):
        """
        Retrieves the players steam info
        :param sids: steam id 64 or list of steam id 64's
        :return: user(s) info
        """
        steaminfo = []

        if type(sids) == str:
            sids = [sids]

        csids = chunk(sids, 100)

        for ids in csids:
            ids = ', '.join(ids)

            params = {
                'key': self._apikey,
                'steamids': ids
            }

            url = self.API_PATHS['get_player_summaries'] % self.DOMAIN
            request = requests.get(url, params=params)

            if request.status_code == 200:
                data = json.loads(request.text)
                players = data['response']['players']

                for player in players:
                    values = {
                        'steamid64': player.get('steamid'),
                        'steamid': convert_steamid(player.get('steamid')),
                        'communityvisibilitystate': player.get('communityvisibilitystate'),
                        'profilestate': player.get('profilestate'),
                        'personaname': player.get('personaname'),
                        'lastlogoff': player.get('lastlogoff'),
                        'commentpermission': player.get('commentpermission'),
                        'profileurl': player.get('profileurl'),
                        'avatar': player.get('avatar'),
                        'avatarmedium': player.get('avatarmedium'),
                        'avatarfull': player.get('avatarfull'),
                        'personastate': self.ONLINE_STATE[player['personastate']]
                    }

                    if player.get('personastate') == 1:
                        values['realname'] = player.get('realname')
                        values['primaryclanid'] = player.get('primaryclanid')
                        values['timecreated'] = player.get('timecreated')
                        values['personastateflags'] = player.get('personastateflags')
                        values['loccountrycode'] = player.get('loccountrycode')
                        values['locstatecode'] = player.get('locstatecode')
                        values['loccityid'] = player.get('loccityid')

                    if len(sids) == 1:
                        return values
                    else:
                        steaminfo.append(values)

            return steaminfo

    def friends(self, steamid,  **kwargs):
        """
        Returns the users friends list
        :param steamid: steam id 64 of the user to retrieve friends for
        :param relationship: defaults to friend, can also be set to all to retain all relationships for the user
        :return: None, list of dictionaries containing steam id 64 of friend, relationship, friend as of date
        """
        params = {
            'key': self._apikey,
            'steamid': steamid,
            'relationship': kwargs.pop('relationship', 'friend')
        }

        url = self.API_PATHS['get_friend_list'] % self.DOMAIN
        request = requests.get(url, params=params)

        if request.status_code == 200:
            data = json.loads(request.text)

            return data['friendslist']['friends']
        else:
            return request.status_code

    def achievements(self, steamid, appid, **kwargs):
        """
        Returns a list of achievements for this user by appid
        :param apikey: steam web api key
        :param steamid: 64 bit steam id to return achievements for
        :param appid: the id for the game your requesting
        :param language: if specified, will return language data for the requested language
        :return: achievements
        """
        params = {
            'key': self._apikey,
            'steamid': steamid,
            'appid': appid,
            'l': kwargs.pop('language', 'en')
        }

        url = self.API_PATHS['get_player_achievements'] % self.DOMAIN
        request = requests.get(url, params=params)

        if request.status_code == 200:
            data = json.loads(request.text)
            values = {
                'steamid': data['playerstats']['steamID'],
                'game': data['playerstats']['gameName'],
                'achievements': data['playerstats']['achievements']
            }

            return values
        else:
            return request.status_code

    def user_stats(self, steamid, appid, **kwargs):
        """
        Returns a list of achievements for this user by appid
        :param apikey: steam web api key
        :param steamid: 64 bit steam id to return achievements for
        :param appid: the id for the game your requesting
        :param language: if specified, will return language data for the requested language
        :return: achievements
        """
        params = {
            'key': self._apikey,
            'steamid': steamid,
            'appid': appid,
            'l': kwargs.pop('language', 'en')
        }

        url = self.API_PATHS['get_user_stats_for_game'] % self.DOMAIN
        request = requests.get(url, params=params)

        if request.status_code == 200:
            data = json.loads(request.text)
            values = {
                'steamid': data['playerstats']['steamID'],
                'game': data['playerstats']['gameName'],
                'stats': data['playerstats']['stats']
            }

            return values
        else:
            return request.status_code

    def owned_games(self, steamid, **kwargs):
        """
        Retrieves the user(s) list of owned games
        :param sids: steam id 64, list of steam id 64's
        :param appinfo: include game name and logo information.  allowed values = 0 (False), 1 (True)
        :param free_games: include free games if played at some point. allowed values = 0 (False), 1 (True)
        :return: steam id 64 and their owned games.
        """

        params = {
            'key': self._apikey,
            'steamid': steamid,
            'include_appinfo': kwargs.pop('appinfo', 0),
            'include_played_free_games': kwargs.pop('free_games', 0)
        }

        url = self.API_PATHS['get_owned_games'] % self.DOMAIN
        request = requests.get(url, params=params)

        if request.status_code == 200:
            data = json.loads(request.text)
            values = {
                'game_count': data['response']['game_count'],
                'games': data['response']['games']
            }

            return values
        else:
            return request.status_code

    def wishlist_games(self, wurl):
        """
        Takes a users steam id profile url and returns their wishlist, count of games in their wishlist and
        number of games on sale
        :param wurl: url of users steam wish list
        :return: wished (list of games), count (count of games wished for), sale (number of games on sale in list)
        """
        wished = []
        count = 0
        sale = 0
        # get our wishlist url so we can make our get request
        request = requests.get(wurl)

        # take our returned request (raw html) and turn it into soup
        soup = BeautifulSoup(request.text)

        # return just the wish list row section for parsing
        list = soup.find_all(class_="wishlistRow ")

        for game in list:
            # start setting our variables
            count += 1
            values = {
                'appid': game['id'].replace('game_', ''),
                'gamename': game.h4.text,
                'imgurl': game.img['src'],
                'row': game.find('div', {'class': 'wishlist_rank_ro'}).text,
            }

            price = game.find('div', {'class': 'price'})

            # if the price is none then we found a game that is on sale
            if price is None:
                try:
                    price = game.find('div', {'class': 'discount_original_price'}).text.strip()
                    discount_price = game.find('div', {'class': 'discount_final_price'}).text.strip()
                    pct_off = game.find('div', {'class': 'discount_pct'}).text.strip()
                    sale += 1
                except:
                    # this exception means we found a game without a price set
                    price = 'N/A'
                    discount_price = '0'
                    pct_off = '0'
            else:
                price = game.find('div', {'class': 'price'}).text.strip()
                discount_price = '0'
                pct_off = '0'

            values['price'] = price
            values['discount'] = discount_price
            values['pct_off'] = pct_off

            wished.append(values)

        return wished, count, sale

    def vanity_url(self, url):
        """
        Retrieves the steam id from a steam vanity url
        :param apikey: steam api key
        :param url: steam users vanity url (i.e. http://steamcommunity.com/id/gabelogannewell)
        :return: users steam id 64 (i.e. 76561197960287930)
        """
        # grabs the persona from the steam vanity url
        persona = re.search(self.VANITY_URL, url).group()

        params = {
            'key': self._apikey,
            'vanityurl': persona
        }

        url = self.API_PATHS['resolve_vanity_url'] % self.DOMAIN
        request = requests.get(url, params=params)

        if request.status_code == 200:
            data = json.loads(request.text)

            if data['response']['success'] == 1:
                result = data['response']['steamid']

                return result
            else:
                return None
