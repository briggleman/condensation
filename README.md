# condensation [![Build Status](https://travis-ci.org/briggleman/condensation.svg?branch=master)](https://travis-ci.org/briggleman/condensation)

Python Steam API Wrapper

## Usage
To use condensation simply include it in your project and initialize
a new object with your [Steam Web API Key](http://steamcommunity.com/dev/apikey).

```python
import condensation
steam = condensation.SteamAPI('XXXXXXXXXXXXXXXXXXXXXXX')
```

## APIKEY
To view the API Key current in use:

```python
>>> steam.apikey
XXXXXXXXXXXXXXXXXXXXXXX
```

## News
Returns the latest news for a game specified by its appid
:param appid: appid of the game you want the news of
:param count: how many news entities you want to get returned
:param maxlength: maximum length of each news entry
:return: appid, newsitems

# Usage

```python
>>> steam.news(271590)
{'newsitems': [{u'feedname': u'rps', u'author': u'contact@rockpapershotgun.com (Alec Meer)', u'url': u'http://store.steampowered.com/news/externalpost/rps/517128939709642530', u'is_external_url': True, u'gid': u'517128939709642530', u'feedlabel': u'Rock, Paper, Shotgun', u'date': 1429894850, u'title': u'Steam Charging For Mods: For And Against', u'contents': u'It used to be that the only way to make money from a mod was a) make a standalone sequel or remake b) use it as a portfolio to get hired by a studio or c) back in the pre-broadband days, shovel it onto <a href="http://www.rockpapershotgun.com/2014/05/08/total-converts-a-potted-history-of-half-life-modding/">a dodgy CD-ROM</a> (and even then, it almost certainly wasn&#8217;t the devs who profited). As of last night, that changed. Mod-makers can now charge for their work, <a href="http://steamcommunity.com/workshop/aboutpaidcontent">via Steam</a>. &#8230; '}], 'appid': 271590}
```