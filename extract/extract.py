import requests
import config
import logging

def extract_volcanoes_from_eonet():
    """
    Extracts volcano events from NASA EONET API.
    Returns a list of volcano events.
    """
    url = config.NASA_EONET
    params = {
        'category': config.EONET_CATEGORY,
        'status': config.EONET_STATUS,
        'days': config.EONET_DAYS_BACK,
        'limit': config.EONET_LIMIT
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        return data.get('events', []) #nie wysypuje sie jak klucz nie istnieje, tylko zwraca pusta liste, lepsze niz data['events'] bo wtedy KeyError
    except requests.exceptions.Timeout:
        logging.error("EONET API timed out — retrying later")
        raise #wyrzuca wyjatek wyzej do pipeline.py
    except requests.exceptions.ConnectionError:
        logging.error("No network connection")
        raise

def extract_volcanoes_from_noaa():
    """
    Extracts volcano events from NOAA NGDC API.
    Returns a list of volcano events.
    """
    url = config.NOAA_NGDC
    volcanoes = []
    try:
        pure_response = requests.get(url)
        pure_response.raise_for_status()
        last_page = pure_response.json()['totalPages']
        for page_index in range(1, last_page+1):
            response = requests.get(url, params={'page': page_index, 'pageSize': config.NOAA_PAGE_SIZE})
            response.raise_for_status()
            volcanoes.extend(response.json()['items'])
    except requests.exceptions.Timeout:
        logging.error("NOAA NGDC API timed out — retrying later")
        raise
    except requests.exceptions.ConnectionError:
        logging.error("No network connection")
        raise
    
    return volcanoes
    

