"""Pandera schemas — Silver-layer data quality contracts for NOAA DataFrames."""

import pandera.pandas as pa

volcanoes_schema = pa.DataFrameSchema(
    {
        "year": pa.Column(nullable=False),
        "name": pa.Column(nullable=False),
        "country": pa.Column(nullable=False),
        "latitude": pa.Column(float, pa.Check.between(-90, 90), nullable=False),
        "longitude": pa.Column(float, pa.Check.between(-180, 180), nullable=False),
        "vei": pa.Column(int, pa.Check.between(-1, 8), nullable=False),
    },
    unique=["id"],
    strict=False,
)


earthquakes_schema = pa.DataFrameSchema(
    {
        "year": pa.Column(nullable=False),
        "country": pa.Column(nullable=False),
        "latitude": pa.Column(float, pa.Check.between(-90, 90), nullable=True),
        "longitude": pa.Column(float, pa.Check.between(-180, 180), nullable=True),
    },
    unique=["id"],
    strict=False,
)
