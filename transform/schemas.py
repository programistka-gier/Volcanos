"""Pandera schemas — Silver-layer data quality contracts for NOAA DataFrames."""

import pandera.pandas as pa

fact_eruptions_schema = pa.DataFrameSchema(
    {
        "volcano_location_id": pa.Column(int, nullable=False),
        "year": pa.Column(int, nullable=False),
        "vei": pa.Column(int, pa.Check.between(-1, 8), nullable=False),
        "deaths_total": pa.Column(
            int, pa.Check.greater_than_or_equal_to(0), nullable=False
        ),
        "earthquake_event_id": pa.Column("Int64", nullable=True),
    },
    unique=["id"],
    strict=False,
)

dim_volcano_schema = pa.DataFrameSchema(
    {
        "name": pa.Column(str, nullable=False),
        "country": pa.Column(str, nullable=False),
        "latitude": pa.Column(float, pa.Check.between(-90, 90), nullable=False),
        "longitude": pa.Column(float, pa.Check.between(-180, 180), nullable=False),
    },
    unique=["volcano_location_id"],
    strict=False,
)

dim_date_schema = pa.DataFrameSchema(
    {
        "year": pa.Column(int, nullable=False),
        "decade": pa.Column(int, nullable=False),
    },
    unique=["year"],
    strict=False,
)

fact_earthquakes_schema = pa.DataFrameSchema(
    {
        "year": pa.Column(int, nullable=False),
        "country": pa.Column(str, nullable=False),
        "latitude": pa.Column(float, pa.Check.between(-90, 90), nullable=True),
        "longitude": pa.Column(float, pa.Check.between(-180, 180), nullable=True),
        "magnitude": pa.Column(float, nullable=True),
        "deaths_total": pa.Column(int, pa.Check.greater_than_or_equal_to(0), nullable=False),
        "volcano_event_id": pa.Column("Int64", nullable=True),
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
