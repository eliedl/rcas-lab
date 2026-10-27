# rcas-lab

Exploration of the CaSR v3.2 daily reanalysis (Canadian Surface Reanalysis, ECCC)
over the Estuary and Gulf of St. Lawrence: per-month winter (Dec–Mar) climatology
and trend maps of surface air temperature, and climatological mean 10 m wind maps,
1990–2020. The same climatology and trend maps are produced for CIS sea-ice
concentration, rasterized onto the CaSR grid.

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

### Sea-ice input
`ice` reads a second file, also not versioned (`ICE_PATH` in `src/config.py`):

    ~/data/CIS/gridded/sgrdr_ct_casr-egsl_19900901-20200901.nc

It holds CIS weekly regional-chart (SGRDR) total concentration `ct` (open water = 0) on
this cache's rotated-pole grid, exported by the companion sea-ice project. Lineage and
the meanings of NaN: `~/data/CIS/gridded/README.md`.

The charts are weekly with 7- and 8-day steps, so xclim's missing-value check cannot
run: it needs a regular source step that divides the month. Instead, the ice analysis
only (not `tas` or `wind`) is gated on the charts actually present:
- **within a month:** a cell's monthly value is NaN if fewer than 50%
  of the month's charts have a value;
- **across years:** a cell-month's mean and trend are NaN if fewer than
  50% of the years have a monthly value.


## Setup
Python 3.12 (`.python-version`).

    pip install -r requirements.txt

Direct dependencies are pinned to the PAVICS `birdy` environment (2026-10-20), so
local results match the cache-building environment.

## Run
From the repo root:

    python main.py tas
    python main.py wind
    python main.py ice

`tas` writes `output/tas_mean.png` and `output/tas_trend.png` (trend in °C/decade;
dotted where p ≥ `SIGNIFICANT_P_VALUE`). `wind` writes `output/wind_mean.png`: the
norm of the climatological mean wind vector (colour) and its direction (equal-length
arrows pointing where the wind blows to). `ice` writes `output/ice_mean.png` and
`output/ice_trend.png` (dotted the same way as `tas`). Cells that are 0 in every
year have p = NaN, so they are not dotted even though their trend is not
significant.

## Architecture
One module per concern, flat in `src/`. Concern modules import only `config`;
`main.py` is the only place they are wired together.

| Module | Concern |
|---|---|
| `config.py` | Input paths (CaSR cache, CIS sea-ice grid), output directory, season months, coverage and significance thresholds |
| `access.py` | Open a local NetCDF input, load with timing |
| `climatology.py` | Daily/weekly → monthly reduction (tas, wind components, sea-ice concentration), unit conversion, season selection, coverage gates, per-month mean and trend, wind-vector norm; no display logic |
| `plotting.py` | Winter ordering (Dec → Mar), facets, overlays (significance hatching, graticule, wind quiver rotated onto the grid axes) |

```
 PAVICS (outside the local runtime)
 ┌───────────────────────────────────────────────────────────────────────┐
 │ THREDDS/OPeNDAP ──► exploration/02_casr_egsl_cache.ipynb ──► .nc file │
 └───────────────────────────────────────────────────────────────┬───────┘
                                                     download    │
 ~/data/ECCC/casr_v32_day_egsl_19900901-20200901.nc  ◄───────────┘
 ~/data/CIS/gridded/sgrdr_ct_casr-egsl_19900901-20200901.nc  ◄─── companion sea-ice data
 ════════════════════════════════ local ════════════════════════════════
                       ┌──────────────────────────────┐
                       │ config.py                    │
                       │ CASR_PATH · ICE_PATH         │
                       │ SEASON_MONTHS · OUTPUT_DIR   │
                       │ SIGNIFICANT_P_VALUE          │
                       │ MIN_MONTH_COVERAGE           │
                       │ MIN_PERIOD_COVERAGE          │
                       └──────▲─────────▲─────────▲───┘
                              │         │         │
                ┌─────────────┘         │         └────────────┐
                │                       │                      │
       ┌────────┴───────┐    ┌──────────┴──────────┐   ┌───────┴────────┐
       │ access.py      │    │ climatology.py      │   │ plotting.py    │
       │ open_cache     │    │ monthly_means       │   │ winter_order   │
       │ timed_load     │    │ monthly_wind_means  │   │ facet          │
       │                │    │ monthly_ct_means    │   │ hatch          │
       │                │    │ select_season       │   │ graticule      │
       │                │    │ climatological_mean │   │ quiver         │
       │                │    │ per_month           │   │ save           │
       │                │    │ gate_period_coverage│   │                │
       │                │    │ trend_per_decade    │   │                │
       │                │    │ wind_norm           │   │                │
       └────────▲───────┘    └──────────▲──────────┘   └───────▲────────┘
                │                       │                      │
                └───────────────┬───────┴──────────────────────┘
                                │
                     ┌──────────┴─────────────────────┐
                     │ main.py  (entry: tas|wind|ice) │
                     └──────────┬─────────────────────┘
                                ▼ writes
                     output/*.png  (gitignored) ···► docs/NOTES.md (interpretation, by hand)
```

### Data flow
One run of `python main.py tas`:
```
open_cache(CASR_PATH)   Dataset, daily, lazy          (access)
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

One run of `python main.py wind`:
```
open_cache(CASR_PATH)   Dataset, daily, lazy          (access)
   │ ds["uas"], ds["vas"]
timed_load()            2 DataArrays daily, m s-1     (access)
   │
monthly_wind_means()    monthly uas, vas              (climatology: xclim generic.stats, op="mean")
   │                    
select_season()         DJFM monthly                  (climatology)
   │
climatological_mean()   per-month mean uas, vas, month-keyed (climatology)
   │
wind_norm()             norm of the mean vector       (climatology: xclim wind_speed_from_vector)
   │
facet()                 norm map on the rlon/rlat axes (plotting)
graticule()             meridians and parallels from the 2D lat/lon (plotting)
quiver()                uas, vas rotated by the local grid angle (17–32° over egsl) onto the
   │                    rlon/rlat axes, equal-length arrows
   │                    
save()                  output/wind_mean.png          (plotting)
```

One run of `python main.py ice`:
```
open_cache(ICE_PATH)    Dataset, weekly charts, lazy  (access)
   │ ds["ct"]
timed_load()            DataArray weekly, fraction, loaded (access)
   │
monthly_ct_means()      monthly, NaN under MIN_MONTH_COVERAGE of the month's charts
   │                    (climatology: generic.stats, xclim missing check skipped)
select_season()         DJFM monthly                  (climatology)
   │
per_month()             per-month mean + trend_per_decade (climatology)
   │
gate_period_coverage()  mean and trend NaN under MIN_PERIOD_COVERAGE of the years (climatology)
   │
winter_order()          Dec → Mar labels              (plotting)
facet()                 maps + hatching where p ≥ SIGNIFICANT_P_VALUE (plotting)
save()                  output/ice_mean.png · output/ice_trend.png (plotting)
```

## Repository layout
    main.py              entry point
    src/                 concern modules (above)
    data/                subset mask (small inputs only; *.nc is gitignored)
    exploration/         frozen notebooks: record of the exploration (01: parity
                         reference for the scripts; 02: live cache builder;
                         03: evidence for rotating wind arrows onto the grid axes)
    docs/NOTES.md        interpretation of the outputs
    docs/READING_LOG.md  literature
