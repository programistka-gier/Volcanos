import json
from extract import extract
from config import RAW_DIR, EONET_FILENAME, NOAA_FILENAME


def load_eonet():
    """Load data from EONET and save to raw file."""
    data = extract.extract_volcanoes_from_eonet()
    save_to_file(data, EONET_FILENAME)


def load_noaa():
    """Load data from NOAA and save to raw file."""
    data = extract.extract_volcanoes_from_noaa()
    save_to_file(data, NOAA_FILENAME)


def save_to_file(data, filename):
    """Save data as JSON to data/raw/{filename}."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / filename
    with open(path, "w") as f:
        json.dump(data, f, indent=2)