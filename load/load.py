import json

from config import RAW_DIR, RAW_NOAA_EARTHQUAKES_FILENAME, RAW_NOAA_VOLCANOES_FILENAME
from extract import extract


def load_noaa_earthquakes():
    """Load earthquakes data from NOAA and save to raw file."""
    data = extract.extract_earthquakes_from_noaa()
    save_to_file(data, RAW_NOAA_EARTHQUAKES_FILENAME)


def load_noaa_volcanoes():
    """Load volcanoes data from NOAA and save to raw file."""
    data = extract.extract_volcanoes_from_noaa()
    save_to_file(data, RAW_NOAA_VOLCANOES_FILENAME)


def save_to_file(data, filename):
    """Save data as JSON to data/raw/{filename}."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
