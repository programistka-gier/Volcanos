# Volcano ELT Pipeline

A Python ELT (Extract → Load → Transform) pipeline built on the Medallion architecture
(Bronze → Silver → Gold). Ingests volcanic eruption and earthquake data from NOAA's public
hazard-service API, preserves the raw data as-is, and produces cleaned, typed Parquet datasets
ready for analysis.

## Data Sources

| Source | API | Coverage |
|--------|-----|----------|
| [NOAA NGDC hazard-service — volcanoes](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanoes) | Significant volcanic eruptions | 900 records, from 1169 to present |
| [NOAA NGDC hazard-service — earthquakes](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes) | Significant earthquakes | 6,692 records |

Both endpoints are free, require no API key, and are paginated (200 records/page).

**Why earthquakes, not NASA EONET?** An earlier version of this project used NASA EONET
(recent volcanic activity) as a second source. It was dropped: EONET's ~75 records had no shared key with the NOAA volcano data and was too small for this project.

## Project Structure

```
Volcanos/
├── extract/
│   └── extract.py        # HTTP calls to NOAA API, paginated, returns lists of dicts
├── load/
│   └── load.py            # Writes raw JSON to data/raw/ (Bronze), unmodified
├── transform/
│   └── transform.py       # pandas cleaning → returns DataFrames (Silver)
├── notebooks/
│   └── test_transform.ipynb  # Dev-loop: test transform functions against saved Bronze data
├── data/
│   ├── raw/                # Bronze — raw JSON, 1:1 with the API (gitignored)
│   └── clean/               # Silver — cleaned Parquet (gitignored)
├── config.py               # URLs, page size, file names, paths (pathlib, anchored to this file)
├── pipeline.py              # Single entry point — orchestrates the whole run
├── requirements.txt         # Runtime dependencies only
├── requirements-dev.txt     # + Jupyter, for notebook work
└── PROJECT_ROADMAP.html     # Detailed step-by-step build log
```

## Architecture — Medallion

```
NOAA volcanoes  ──┐                                          ┌──→ data/clean/noaa_volcanoes_clean.parquet
                   ├─→ extract.py → load.py → data/raw/*.json ─┤
NOAA earthquakes ──┘         (Bronze)              (transform.py)  └──→ data/clean/noaa_earthquakes_clean.parquet
                                                          (Silver)
```

- **Bronze** (`data/raw/`) — exact API responses as JSON, never modified. If a bug is found in
  the cleaning logic, or requirements change, Silver/Gold can be rebuilt from Bronze without
  hitting the API again.
- **Silver** (`data/clean/`) — typed, deduplicated Parquet. Column selection and renaming to
  snake_case, domain-aware null handling (see below), foreign keys kept as pandas nullable
  `Int64` rather than filled with sentinels.
- **Gold** (`data/gold/`) — planned, optional: a star schema (fact/dimension tables) for
  aggregate analysis, potentially joining volcanoes and earthquakes via `volcano_event_id`.

## Data Quality Decisions

A few null-handling choices worth calling out, since "just fillna everything" is the wrong
default:

- `vei` (Volcanic Explosivity Index) — missing values filled with `-1`, **not** `0`. VEI `0` is
  a real value (non-explosive eruption); `-1` is an explicit sentinel meaning "not measured."
- `deaths_total` — missing filled with `0` (no recorded deaths = reasonable default for a count).
- `volcano_event_id`, `earthquake_event_id` (foreign keys) — **not** filled with a sentinel.
  Cast to pandas nullable `Int64`, which represents "no linked event" as `pd.NA` instead of a
  fabricated ID. An identifier is not a measurement — there's no domain-sensible default for it.
- `latitude`, `longitude`, `magnitude`, `month`, `day` — left as `NaN` where genuinely unknown
  (mostly older/historical records). No fabricated defaults; filtered explicitly at analysis time.

## Analyses (planned, based on NOAA volcanoes)

1. **Top countries** by number of significant eruptions
2. **Most powerful eruptions** — VEI ≥ 5 (Mount St. Helens level and above)
3. **Eruption trend per decade** — is volcanic activity increasing?

## Tech Stack

- Python 3.12
- `pandas` — extraction, cleaning, transformation
- `requests` — API calls
- `pyarrow` — Parquet read/write engine
- Ruff — linting + formatting
- Jupyter
## Setup

```bash
git clone https://github.com/programistka-gier/Volcanos.git
cd Volcanos

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt          # runtime only
# pip install -r requirements-dev.txt    # + Jupyter, for notebook work

python pipeline.py
```

`pipeline.py` is the only file meant to be run directly — it fetches both datasets, saves Bronze,
cleans to Silver, runs data-quality checks, and writes Parquet. Modules inside `extract/`,
`load/`, `transform/` are not standalone entry points.

## Key Concepts Demonstrated

- Medallion architecture (Bronze/Silver/Gold) with reproducibility from raw data
- REST API pagination and error handling (timeout/connection retries)
- Foreign-key-based multi-source joins (NOAA volcanoes ↔ earthquakes via `volcanoEventId`) —
  chosen deliberately over fuzzy geographic matching
- Domain-aware null handling: sentinel values for measures (VEI) vs. pandas nullable `Int64`
  for identifiers, vs. leaving genuine unknowns as `NaN`
- Config centralization with `pathlib`, paths anchored to `Path(__file__).resolve().parent`
  (same pattern as Django's `BASE_DIR`) instead of relative paths that break depending on cwd
- Separation of concerns: `transform_*()` functions are pure (no I/O), saving is a distinct step
- Data quality gates (`assert` checks) between Bronze, Silver, and Gold

## Status

Bronze and Silver layers are complete and running end-to-end. Tests (pytest, mocked HTTP calls)
