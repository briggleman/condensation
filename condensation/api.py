# -*- coding: utf-8 -*-

"""
condensation.api
~~~~~~~~~~~~~~~~

This modules implements the Condensation API

:copyright: (c) 2015 by Ben Riggleman
:license: Apache2, see LICENSE for more details

"""

from .utils import chunk, get_steamid, convert_steamid
from bs4 import BeautifulSoup
import requests
import json
import re

DOMAIN = 'http://api.steampowered.com/'

# Steam API paths
API_PATHS = {'get_news_for_app': '%sISteamNews/GetNewsForApp/v0002/?appid=%s&count=%d&maxlength=%d&format=%s',
             'get_global_achievement_pct': '%sISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid=%s&format=%s',
             'get_global_stats_for_game': '%sISteamUserStats/GetGlobalStatsForGame/v0001/?appid=%s&count=%d&name[%d]=%s&format=%s',
             'get_player_summaries': '%sISteamUser/GetPlayerSummaries/v0002/',
             'get_friend_list': '%sISteamUser/GetFriendList/v0001/',
             'get_player_achievements': '%sISteamUserStats/GetPlayerAchievements/v0001/?key=%s&appid=%s&steamid=%s',
             'get_user_stats_for_game': '%sISteamUserStats/GetUserStatsForGame/v0002/?key=%s&appid=%s&steamid=%s',
             'get_owned_games': '%sIPlayerService/GetOwnedGames/v0001/',
             'get_recently_played_games': '%sIPlayerService/GetRecentlyPlayedgames/v0001/?key=%s&steamid=%s&format=%s',
             'is_playing_shared_game': '%sIPlayerService/IsPlayingSharedGame/v0001/?key=%s&appid_playing=%s&steamid=%s&format=%s',
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


def get_player_summaries(apikey, sids):
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
            'key': apikey,
            'steamids': ids
        }

        url = API_PATHS['get_player_summaries'] % DOMAIN
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
                    'personastate': ONLINE_STATE[player['personastate']]
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


def resolve_vanity_url(apikey, url):
    """
    Retrieves the steam id from a steam vanity url
    :param apikey: steam api key
    :param url: steam users vanity url (i.e. http://steamcommunity.com/id/gabelogannewell)
    :return: users steam id 64 (i.e. 76561197960287930)
    """
    # grabs the persona from the steam vanity url
    persona = re.search(VANITY_URL, url).group()

    params = {
        'key': apikey,
        'vanityurl': persona
    }

    url = API_PATHS['resolve_vanity_url'] % DOMAIN
    request = requests.get(url, params=params)

    if request.status_code == 200:
        data = json.loads(request.text)

        if data['response']['success'] == 1:
            result = data['response']['steamid']

            return result
        else:
            return None


def get_friend_list(apikey, steamid,  **kwargs):
    """
    Returns the users friends list
    :param steamid: steam id 64 of the user to retrieve friends for
    :param relationship: defaults to friend, can also be set to all to retain all relationships for the user
    :return: None, list of dictionaries containing steam id 64 of friend, relationship, friend as of date
    """
    params = {
        'key': apikey,
        'steamid': steamid,
        'relationship': kwargs.pop('relationship', 'friend')
    }

    url = API_PATHS['get_friend_list'] % DOMAIN
    request = requests.get(url, params=params)

    if request.status_code == 200:
        data = json.loads(request.text)
        friends = data['friendslist']['friends']

        return friends
    else:
        return None


def get_owned_games(apikey, steamid, **kwargs):
    """
    Retrieves the user(s) list of owned games
    :param sids: steam id 64, list of steam id 64's
    :param appinfo: include game name and logo information.  allowed values = 0 (False), 1 (True)
    :param free_games: include free games if played at some point. allowed values = 0 (False), 1 (True)
    :return: steam id 64 and their owned games.
    """

    params = {
        'key': apikey,
        'steamid': steamid,
        'include_appinfo': kwargs.pop('appinfo', 0),
        'include_played_free_games': kwargs.pop('free_games', 0)
    }

    url = API_PATHS['get_owned_games'] % DOMAIN
    request = requests.get(url, params=params)

    if request.status_code == 200:
        data = json.loads(request.text)
        values = {
            'game_count': data['response']['game_count'],
            'games': data['response']['games']
        }

        return values
    else:
        return None

def get_wishlist_games(self, wurl):
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