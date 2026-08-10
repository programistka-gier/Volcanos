import logging

from load.load import load_noaa_earthquakes, load_noaa_volcanoes

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    load_noaa_earthquakes()
    load_noaa_volcanoes()
