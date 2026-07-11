# Volcano ELT Pipeline

A Python-based ELT (Extract → Load → Transform) pipeline that ingests volcanic activity data from two public APIs, stores raw data locally, and produces cleaned datasets ready for analysis.

## Data Sources

| Source | API | Coverage |
|--------|-----|----------|
| [NASA EONET](https://eonet.gsfc.nasa.gov/) | Earth Observatory Natural Event Tracker | Recent volcanic events (last 2 years) |
| [NOAA NGDC](https://www.ngdc.noaa.gov/hazel/hazard-service/) | National Geophysical Data Center | Historical significant eruptions (1900–present) |

Both APIs are free and require no API key.

## Project Structure

```
volcano-elt/
├── volcano_elt.ipynb     # Main ELT notebook
├── requirements.txt      # Python dependencies
├── raw/                  # Raw JSON from APIs (gitignored)
└── clean/                # Cleaned CSV output
    └── eruptions_clean.csv
```

## Pipeline Overview

```
NASA EONET API ──→ raw/eonet_volcanoes.json ──→
                                                 Transform → clean/eruptions_clean.csv
NOAA NGDC API  ──→ raw/noaa_eruptions.json  ──→
```

**Extract** — HTTP requests to two REST APIs  
**Load** — Raw JSON saved to disk without modification (local data lake pattern)  
**Transform** — Pandas: column selection, renaming, null checks, analysis

## Analyses

1. **Top 15 countries** by number of eruptions since 1900
2. **Most powerful eruptions** — VEI ≥ 5 (Mount St. Helens level and above)
3. **Eruption trend per decade** — is volcanic activity increasing?

## Tech Stack

- Python 3
- `pandas` — data transformation
- `requests` — API calls
- Jupyter Notebook (via VS Code)

## Setup

```bash
# Clone the repo
git clone https://github.com/weronikaslusarczyk/volcano-elt-pipeline.git
cd volcano-elt-pipeline

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Open notebook
code volcano_elt.ipynb
```

Then run all cells in order — the pipeline will fetch data, save raw files, and produce `clean/eruptions_clean.csv`.

## Key Concepts Demonstrated

- ELT pattern (raw data preserved before transformation)
- REST API consumption
- Data cleaning and column standardisation with pandas
- Exploratory data analysis on geophysical datasets
