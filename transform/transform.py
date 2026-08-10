import pandas as pd
import logging
from config import RAW_DIR, EONET_FILENAME, NOAA_FILENAME, CLEAN_DIR, CLEAN_NOAA_FILENAME, CLEAN_EONET_FILENAME

NOAA_COLUMN_MAP = {
    "year": "year",
    "month": "month",
    "day": "day",
    "name": "name",
    "country": "country",
    "latitude": "latitude",
    "longitude": "longitude",
    "elevation": "elevation",
    "morphology": "morphology",
    "vei": "vei",
    "deathsTotal": "deaths_total",
    "significant": "significant",
}

def transform_noaa() -> pd.DataFrame:
    """Clean raw NOAA eruption data and return the Silver-layer DataFrame."""
    df = data_check(RAW_DIR/NOAA_FILENAME)

    #save only important columns
    df = df[list(NOAA_COLUMN_MAP)].rename(columns=NOAA_COLUMN_MAP)

    df["deaths_total"] = df["deaths_total"].fillna(0).astype(int)
    df["vei"] = df["vei"].fillna(-1).astype(int)
    return df



def check_eonet():
    """Check eonet info, shape and null"""
    data_check(RAW_DIR/EONET_FILENAME)


def data_check(path) -> pd.DataFrame:
    df = pd.read_json(path)
    logging.info(f"Raw shape for {path}: {df.shape}")
    return df
