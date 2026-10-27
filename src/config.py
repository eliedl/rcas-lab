"""Project configuration: input locations, output, season, coverage and significance thresholds."""
from pathlib import Path

CASR_PATH = Path.home() / "data" / "ECCC" / "casr_v32_day_egsl_19900901-20200901.nc"
ICE_PATH = Path.home() / "data" / "CIS" / "gridded" / "sgrdr_ct_casr-egsl_19900901-20200901.nc"
OUTPUT_DIR = Path(__file__).parents[1] / "output"
SEASON_MONTHS = (12, 1, 2, 3)   # display order: winter runs Dec → Mar
SIGNIFICANT_P_VALUE = 0.05
MIN_MONTH_COVERAGE = 0.5    # fraction of a month's charts a cell needs a value on (ice-clim DEC-060)
MIN_PERIOD_COVERAGE = 0.5   # fraction of the period's years a cell needs a monthly value in (MPO: 15 of 30)
