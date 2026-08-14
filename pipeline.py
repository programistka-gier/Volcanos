import logging

from config import CLEAN_NOAA_EARTHQUAKES_FILENAME, CLEAN_NOAA_VOLCANOES_FILENAME
from load.load import load_noaa_earthquakes, load_noaa_volcanoes
from transform.transform import (
    save_to_clean,
    transform_noaa_earthquakes,
    transform_noaa_volcanoes,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    load_noaa_earthquakes()
    load_noaa_volcanoes()
    volcanoes = transform_noaa_volcanoes()
    save_to_clean(volcanoes, CLEAN_NOAA_VOLCANOES_FILENAME)
    earthquakes = transform_noaa_earthquakes()
    save_to_clean(earthquakes, CLEAN_NOAA_EARTHQUAKES_FILENAME)
