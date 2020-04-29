import json
import requests
from .nyt import fetch_nyt

CACHE_FILE_NAME = 'cache.json'

def load_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the cache dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and
    repeatably identify an get request by its baseurl and params

    Parameters
    ----------
    baseurl: string
        The URL for get request
    params: dict
        A dictionary of param:value pairs

    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key

def make_url_request_using_cache(url, params, source):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new
    request, save it, then return it.

    Parameters
    ----------
    baseurl: string
        The URL for get request
    params: dict
        A dictionary of param:value pairs

    Returns
    -------
    dict
        the results of the get request as a dictionary loaded from cache
    '''
    unique_key = construct_unique_key(url, params)
    cache = load_cache()

    if (unique_key in cache.keys()):
        print("Using cache...")
        using_cache = True
    else:
        print("Fetching...")
        using_cache = False
        if source == "covid19api":
            response = requests.get(url)
            cache[unique_key] = response.json()

        elif "nyt" in source:
            response = fetch_nyt(url, source)
            cache[unique_key] = response

        save_cache(cache)

    return cache[unique_key], using_cache
