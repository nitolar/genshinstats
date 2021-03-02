"""Genshin Impact gacha pulls log.

Gets pull data from the current banners in basic json.
Requires an auth key that can be gotten from an output_log.txt file.
"""
import os.path
import re
import time
from tempfile import gettempdir
from urllib.parse import unquote, urljoin

import requests

from .errors import *
from .pretty import prettify_gacha_log

GENSHIN_DIR = os.path.join(os.environ['HOME'],'AppData/LocalLow/miHoYo/Genshin Impact')
GENSHIN_LOG = os.path.join(GENSHIN_DIR,'output_log.txt')
GACHA_LOG_URL = "https://hk4e-api.mihoyo.com/event/gacha_info/api/"
AUTHKEY_FILE = os.path.join(gettempdir(),'genshinstats_authkey.txt')
AUTHKEY_DURATION = 60*60*24 # 1 day
_gacha_types = None

session = requests.Session()
session.headers({
    # recommended header
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
})
session.params = {
    # required params
    "authkey_ver":1,
    "lang":"en",
    # authentications params
    "authkey":"",
    # recommended headers
    "authkey_ver": "1",
    "device_type": "pc",
    "ext": '{"loc":{"x":1637.727294921875,"y":195.80615234375,"z":-2659.14208984375},"platform":"WinST"}',
    "gacha_id": "a3101d03239e0eb2a79c4b144c5197b296f087",
    "game_biz": "hk4e_global",
    "game_version": "OSRELWin1.3.2_R2079798_S2088824_D2088824",
    "init_type": "301",
    "lang": "en",
    "region": "os_euro",
    "sign_type": "2",
}

def get_authkey(logfile: str=None) -> str:
    """Gets the query for log requests.
    
    This will either be done from the logs or from a tempfile.
    """
    # first try the log
    log = open(logfile or GENSHIN_LOG).read()
    match = re.search(r'^OnGetWebViewPageFinish:https://.+authkey=([^&]+).+#/log$',log,re.MULTILINE)
    if match is not None:
        authkey = unquote(match.group(1))
        open(AUTHKEY_FILE,'w').write(authkey)
        return authkey
    
    # otherwise try the tempfile
    if (os.path.isfile(AUTHKEY_FILE) and 
        time.time()-os.path.getmtime(AUTHKEY_FILE) <= AUTHKEY_DURATION):
        return open(AUTHKEY_FILE).read()
    
    raise MissingAuthKey('No authkey could be found in the params, logs or in a tempfile. '
                         'Open the history in-game first before attempting to request it.')

def set_authkey(authkey: str=None, logfile: str=None):
    """Sets an authkey for log requests.
    
    Passing in authkey will simply save it, otherwise passing in a logfile will search it.
    If nothing is passed in, uses get_authkey.
    """
    if authkey is None:
        authkey = get_authkey(logfile)
    session.params['authkey'] = authkey

def fetch_gacha_endpoint(endpoint: str, **kwargs) -> dict:
    """Fetch an enpoint from mihoyo's gacha info.
    
    Takes in an endpoint or a url and kwargs that are later formatted to a query.
    A request is then sent and returns a parsed response.
    """
    session.params['authkey'] = session.params['authkey'] or get_authkey() # update authkey
    url = urljoin(GACHA_LOG_URL,endpoint)
    r = session.get(url,params=kwargs)
    r.raise_for_status()
    
    data = r.json()
    if data['data'] is not None:
        return data['data']
    
    if   data['retcode'] == -100 and data['message'] == "authkey error":
        raise AuthKeyError('Authkey is not valid.')
    elif data['retcode'] == -101 and data['message'] == "authkey timeout":
        raise AuthKeyTimeout('Authkey has timed-out. Update it by opening the history page in Genshin.')
    else:
        raise GenshinGachaLogException(f"{data['retcode']} error: {data['message']}")

def get_gacha_types() -> list:
    """Gets possible gacha types.
    
    Returns a list of dicts.
    """
    global _gacha_types
    if _gacha_types is not None:
        return _gacha_types
    _gacha_types = fetch_gacha_endpoint("getConfigList")['gacha_type_list']
    return _gacha_types

def recognize_gacha_type(gacha_type) -> str:
    """Recognizes the gacha type. Case Sensitive."""
    gacha_type = str(gacha_type)
    gacha_types = get_gacha_types()
    for i in gacha_types:
        if gacha_type in i.values():
            return i['key']
    
    raise BadGachaType(f'Gacha type "{gacha_type}" is not valid, must be one of {sum((list(i.values()) for i in gacha_types),[])}')

def get_gacha_log(gacha_type: str, page: int=1, size: int=20, raw: bool=False) -> list:
    """Gets the gacha pull history log.
    
    Needs a gacha type, this can either be its name, key or id.
    Possible gacha types can be found in the return of get_gacha_types().
    Returns a list of dicts. 
    """
    gacha_type = recognize_gacha_type(gacha_type)
    data = fetch_gacha_endpoint("getGachaLog",gacha_type=gacha_type,page=page,size=size)['list']
    return data if raw else prettify_gacha_log(data)