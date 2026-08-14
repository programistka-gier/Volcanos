from pathlib import Path

# folder, w którym leży config.py = root projektu
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"

RAW_NOAA_VOLCANOES_FILENAME = "noaa_volcanoes.json"
CLEAN_NOAA_VOLCANOES_FILENAME = "noaa_volcanoes_clean.parquet"
NOAA_VOLCANOES = "https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanoes"

RAW_NOAA_EARTHQUAKES_FILENAME = "noaa_earthquakes.json"
CLEAN_NOAA_EARTHQUAKES_FILENAME = "noaa_earthquakes_clean.parquet"
NOAA_EARTHQUAKES = "https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes"

NOAA_PAGE_SIZE = 200
NOAA_TOTALPAGES = "totalPages"
