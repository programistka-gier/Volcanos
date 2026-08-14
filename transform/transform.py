import logging

import pandas as pd

from config import (
    CLEAN_DIR,
    CLEAN_NOAA_EARTHQUAKES_FILENAME,
    CLEAN_NOAA_VOLCANOES_FILENAME,
    RAW_DIR,
    RAW_NOAA_EARTHQUAKES_FILENAME,
    RAW_NOAA_VOLCANOES_FILENAME,
)

logger = logging.getLogger(__name__)

NOAA_VOLCANOES_COLUMN_MAP = {
    "id": "id",
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
    "earthquakeEventId": "earthquake_event_id",
}

NOAA_EARTHQUAKES_COLUMN_MAP = {
    "id": "id",
    "year": "year",
    "month": "month",
    "day": "day",
    "country": "country",
    "latitude": "latitude",
    "longitude": "longitude",
    "eqMagnitude": "magnitude",
    "deathsTotal": "deaths_total",
    "volcanoEventId": "volcano_event_id",
}


def transform_noaa_volcanoes() -> pd.DataFrame:
    """Clean raw NOAA eruption data and return the Silver-layer DataFrame."""
    df = load_raw(RAW_DIR / RAW_NOAA_VOLCANOES_FILENAME)

    # save only important columns and rename
    df = df[list(NOAA_VOLCANOES_COLUMN_MAP)].rename(columns=NOAA_VOLCANOES_COLUMN_MAP)

    # clearing NaN and set type
    df["deaths_total"] = df["deaths_total"].fillna(0).astype(int)
    df["vei"] = df["vei"].fillna(-1).astype(int)
    df["earthquake_event_id"] = df["earthquake_event_id"].astype("Int64")

    # clear duplicates and reset index
    df = df.drop_duplicates().reset_index(drop=True)

    logger.info(f"Silver shape for NOAA volcanoes: {df.shape}")

    return df


def transform_noaa_earthquakes() -> pd.DataFrame:
    """Clean raw NOAA earthquakes data and return the Silver-layer DataFrame."""
    df = load_raw(RAW_DIR / RAW_NOAA_EARTHQUAKES_FILENAME)

    df = df[list(NOAA_EARTHQUAKES_COLUMN_MAP)].rename(
        columns=NOAA_EARTHQUAKES_COLUMN_MAP
    )

    df["deaths_total"] = df["deaths_total"].fillna(0).astype(int)
    df["volcano_event_id"] = df["volcano_event_id"].astype("Int64")

    df = df.drop_duplicates().reset_index(drop=True)
    logger.info(f"Silver shape for NOAA earthquakes: {df.shape}")

    return df


def load_raw(path) -> pd.DataFrame:
    df = pd.read_json(path)
    logger.info(f"Raw shape for {path}: {df.shape}")
    return df


def save_to_clean(df: pd.DataFrame, filename: str) -> None:
    """Save data as PARQUET to data/clean/{filename}."""
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    path = CLEAN_DIR / filename
    df.to_parquet(path, index=False)
    logger.info(f"Saved {len(df)} records to {path}")
