import logging

import requests

import config

logger = logging.getLogger(__name__)


def extract_volcanoes_from_noaa():
    """
    Extracts volcano events from NOAA NGDC API.
    Returns a list of volcano events.
    """
    url = config.NOAA_VOLCANOES
    volcanoes = []
    try:
        pure_response = requests.get(url)
        pure_response.raise_for_status()
        last_page = pure_response.json()["totalPages"]

        logger.info("Fetching volcanoes from NOAA NGDC...")
        for page_index in range(1, last_page + 1):
            response = requests.get(
                url, params={"page": page_index, "pageSize": config.NOAA_PAGE_SIZE}
            )
            response.raise_for_status()
            volcanoes.extend(response.json()["items"])
    except requests.exceptions.Timeout:
        logger.error("NOAA NGDC API timed out — retrying later")
        raise
    except requests.exceptions.ConnectionError:
        logger.error("No network connection")
        raise

    logger.info(f"Fetched {len(volcanoes)} volcanoes records")
    return volcanoes


def extract_earthquakes_from_noaa():
    """
    Extracts earthquake events from NOAA NGDC API.
    Returns a list of earthquakes events.
    """
    url = config.NOAA_EARTHQUAKES
    earthquakes = []
    try:
        pure_response = requests.get(url)
        pure_response.raise_for_status()
        last_page = pure_response.json()["totalPages"]

        logger.info("Fetching earthquakes from NOAA NGDC...")
        for page_index in range(1, last_page + 1):
            response = requests.get(
                url, params={"page": page_index, "pageSize": config.NOAA_PAGE_SIZE}
            )
            response.raise_for_status()
            earthquakes.extend(response.json()["items"])
    except requests.exceptions.Timeout:
        logger.error("NOAA NGDC API timed out — retrying later")
        raise
    except requests.exceptions.ConnectionError:
        logger.error("No network connection")
        raise

    logger.info(f"Fetched {len(earthquakes)} earthquakes records")
    return earthquakes
