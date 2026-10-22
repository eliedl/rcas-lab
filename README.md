# rcas-lab

Exploration of the CaSR v3.2 daily reanalysis (Canadian Surface Reanalysis, ECCC)
over the Estuary and Gulf of St. Lawrence: per-month winter (Dec–Mar) climatology
and trend maps of surface air temperature, 1990–2020. ("rcas" is a historical name.)

## Data
The input is a ~2.8 GB NetCDF cache that is **not versioned** (`*.nc` is gitignored).
It is built on [PAVICS](https://pavics.ouranos.ca/) by
`exploration/02_casr_egsl_cache.ipynb`, which reads CaSR over THREDDS/OPeNDAP and
subsets it with the `egsl` mask, then downloaded locally. The expected path is set
in `src/config.py`:

    ~/data/ECCC/casr_v32_day_egsl_19900901-20200901.nc

### Subset mask
`data/egsl_32198_bbox.geojson` is the mask the cache was cut with: one axis-aligned
rectangle in EPSG:32198 (NAD83 / Québec Lambert), bounds
`(-232591.818, -129851.4, 1039420.0, 952110.276)` m ≈ 71.95–53.28°W, 42.03–52.54°N.
It covers the CIS daily-chart (SGRDA) extent of the Estuary and Gulf of St. Lawrence,
extended west to the weekly regional-chart limit, so it reaches beyond the Gulf proper
(seaward of Cabot Strait). It is a snapshot of the canonical `egsl` envelope shared with
a companion sea-ice climatology project, as of 2026-10-21.

**Caveat:** spatial means cover this envelope, not a Gulf coastline boundary.

To rebuild the cache: upload this file to your PAVICS writable workspace (the path in
`SHAPE_PATH`, `exploration/02_casr_egsl_cache.ipynb`), run the notebook on PAVICS, and
download the output to the path in `src/config.py`.

## Setup
Python 3.12 (`.python-version`).

    pip install -r requirements.txt

Direct dependencies are pinned to the PAVICS `birdy` environment (2026-10-20), so
local results match the cache-building environment.

## Run
From the repo root:

    python main.py

Writes `output/tas_mean.png` and `output/tas_trend.png` (trend in °C/decade;
dotted where p ≥ `SIGNIFICANT_P_VALUE`).

## Architecture
One module per concern, flat in `src/`. Concern modules import only `config`;
`main.py` is the only place they are wired together.

| Module | Concern |
|---|---|
| `config.py` | Cache path, output directory, season months, significance threshold |
| `access.py` | Open the local cache, load with timing |
| `climatology.py` | Daily → monthly reduction, unit conversion, season selection, per-month mean and trend; no display logic |
| `plotting.py` | Winter ordering (Dec → Mar), facets, significance hatching |

```
 PAVICS (outside the local runtime)
 ┌───────────────────────────────────────────────────────────────────────┐
 │ THREDDS/OPeNDAP ──► exploration/02_casr_egsl_cache.ipynb ──► .nc file │
 └───────────────────────────────────────────────────────────────┬───────┘
                                                     download    │
 ~/data/ECCC/casr_v32_day_egsl_19900901-20200901.nc  ◄───────────┘
 ════════════════════════════════ local ════════════════════════════════
                       ┌──────────────────────────────┐
                       │ config.py                    │
                       │ CACHE_PATH · SEASON_MONTHS   │
                       │ SIGNIFICANT_P_VALUE          │
                       │ OUTPUT_DIR                   │
                       └──────▲─────────▲─────────▲───┘
                              │         │         │
                ┌─────────────┘         │         └────────────┐
                │                       │                      │
       ┌────────┴───────┐    ┌──────────┴──────────┐   ┌───────┴────────┐
       │ access.py      │    │ climatology.py      │   │ plotting.py    │
       │ open_cache     │    │ monthly_means       │   │ winter_order   │
       │ timed_load     │    │ select_season       │   │ facet          │
       │                │    │ trend_per_decade    │   │ _hatch         │
       │                │    │ per_month           │   │ save           │
       └────────▲───────┘    └──────────▲──────────┘   └───────▲────────┘
                │                       │                      │
                └───────────────┬───────┴──────────────────────┘
                                │
                     ┌──────────┴─────────────────────┐
                     │ main.py  (entry point, tas)    │
                     └──────────┬─────────────────────┘
                                ▼ writes
                     output/*.png  (gitignored) ···► docs/NOTES.md (interpretation, by hand)
```

### Data flow
One run of `python main.py`:
```
open_cache()            Dataset, daily, lazy          (access)
   │ ds["tas"]
timed_load()            DataArray daily, K, loaded    (access)
   │
monthly_means()         monthly, °C, all 12 months    (climatology: tg_mean + convert_units_to)
   │
select_season()         DJFM monthly                  (climatology: SEASON_MONTHS)
   │
per_month()             per-month mean + trend_per_decade (climatology)
   │                    month-keyed, groupby order (1, 2, 3, 12): no display logic
winter_order()          Dec → Mar labels              (plotting)
facet()                 maps + hatching where p ≥ SIGNIFICANT_P_VALUE (plotting)
save()                  output/tas_mean.png · output/tas_trend.png (plotting)
```

## Repository layout
    main.py              entry point
    src/                 concern modules (above)
    data/                subset mask (small inputs only; *.nc is gitignored)
    exploration/         frozen notebooks: record of the exploration and parity
                         reference for the scripts (02 is the live cache builder)
    docs/NOTES.md        interpretation of the outputs
    docs/READING_LOG.md  literature
