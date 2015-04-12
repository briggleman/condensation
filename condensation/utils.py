__author__ = 'Ben Riggleman'

import re

def get_steamid(url):
    sid = re.compile('(?<=http://steamcommunity.com/openid/id/)([0-9]{0,})')
    steamid = re.search(sid, url).group()

    if steamid:
        return steamid
    else:
        return None

def convert_steamid(i):
    '''
    takes the players steam id and converts it to their formal steam id
    :param i: players steam id
    :return: computed steam id
    '''
    # (((i - (i % 2)) - 76561197960265728) / 2)
    i = int(i)
    server = i % 2
    auth = (((i - (i % 2)) - 76561197960265728) / 2)
    #computed steam id
    steamid = 'STEAM_0:' + str(server) + ':' + str(auth)

    return steamid

def chunk(l, n):
    '''
    Yield successive n-sized chunks from l
    :param l: list to chunk
    :param n: size of chunks
    :return: list of chunked lists
    '''

    for i in xrange(0, len(l), n):
        yield l[i:i+n]