from pathlib import Path

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")

RAW_NOAA_VOLCANOES_FILENAME = "noaa_volcanoes.json"
CLEAN_NOAA_VOLCANOES_FILENAME = "noaa_volcanoes_clean.parquet"
NOAA_VOLCANOES = "https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanoes"

RAW_NOAA_EARTHQUAKES_FILENAME = "noaa_earthquakes.json"
CLEAN_NOAA_EARTHQUAKES_FILENAME = "noaa_earthquakes_clean.parquet"
NOAA_EARTHQUAKES = "https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes"

NOAA_PAGE_SIZE = 200
NOAA_TOTALPAGES = "totalPages"
