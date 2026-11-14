import argparse
import logging

from config import CLEAN_NOAA_EARTHQUAKES_FILENAME, CLEAN_NOAA_VOLCANOES_FILENAME
from load.load import load_noaa_earthquakes, load_noaa_volcanoes
from transform.schemas import earthquakes_schema, volcanoes_schema
from transform.transform import (
    save_to_clean,
    transform_noaa_earthquakes,
    transform_noaa_volcanoes,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Volcano ELT pipeline: extract, load and transform data from NOAA"
    )
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Skip extraction from NOAA phase, use saved raw data.",
    )
    args = parser.parse_args()
    if not args.skip_extract:
        logger.info("Extracting data from NOAA.")
        load_noaa_earthquakes()
        load_noaa_volcanoes()
    else:
        logger.info("Skipped extraction, using data from data/raw")

    volcanoes = transform_noaa_volcanoes()
    volcanoes_schema.validate(volcanoes, lazy=True)
    save_to_clean(volcanoes, CLEAN_NOAA_VOLCANOES_FILENAME)

    earthquakes = transform_noaa_earthquakes()
    earthquakes_schema.validate(earthquakes, lazy=True)
    save_to_clean(earthquakes, CLEAN_NOAA_EARTHQUAKES_FILENAME)
