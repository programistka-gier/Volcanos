import json
from extract import extract


def load_eonet():
    """Load data from EONET and save to raw file."""
    data = extract.extract_volcanoes_from_eonet()
    save_to_file(data, "eonet_volcanoes.json")


def load_noaa():
    """Load data from NOAA and save to raw file."""
    data = extract.extract_volcanoes_from_eonet()
    save_to_file(data, "noaa_volcanoes.json")


def save_to_file(data, filename):
    """Save data as JSON to data/raw/{filename}."""
    path = f"data/raw/{filename}"
    with open(path, "w") as f:
        json.dump(data, f)