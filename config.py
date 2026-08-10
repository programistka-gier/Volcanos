from pathlib import Path

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")

EONET_FILENAME = "eonet_volcanoes.json"
NOAA_FILENAME = "noaa_volcanoes.json"

CLEAN_NOAA_FILENAME = "noaa_volcanoes_clean.parquet"
CLEAN_EONET_FILENAME = "eonet_volcanoes_clean.parquet" 

NASA_EONET = 'https://eonet.gsfc.nasa.gov/api/v3/events'
NOAA_NGDC = 'https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanoes'
EONET_CATEGORY = 'volcanoes'
EONET_STATUS = 'all'
EONET_DAYS_BACK = 730
EONET_LIMIT = 500
NOAA_PAGE_SIZE = 200
NOAA_TOTALPAGES = 'totalPages'